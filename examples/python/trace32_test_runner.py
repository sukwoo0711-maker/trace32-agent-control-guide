#!/usr/bin/env python3
"""Evaluate a TRACE32 MCU test case into a deterministic verdict.

The runner reads a test case (see schemas/test_case.schema.json), resolves each
assertion's actual value, compares it to the expected value, and reduces the
result to one verdict: pass, fail, error, timeout, or skip
(see docs/test-verdict-model.md).

It is safe to run without hardware using --dry-run, in which case each assertion
is resolved from its optional ``dry_run_actual`` field. Real mode requires
Lauterbach's lauterbach-trace32-rcl package, a running PowerView instance with
the Remote API enabled, and the Trace32Observer wrapper in this directory.

Exit codes: 0 pass, 1 fail, 2 error/timeout, 3 skip.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from xml.etree import ElementTree as ET


VERDICT_EXIT = {"pass": 0, "fail": 1, "error": 2, "timeout": 2, "skip": 3}

# Sources that are read from a single target/debugger snapshot rather than by
# evaluating a TRACE32 function expression directly.
SNAPSHOT_SOURCES = {"target_state", "practice_state", "message"}


class Unresolved(Exception):
    """Raised when an assertion's actual value cannot be trustworthy."""


def compare(actual: Any, operator: str, expected: Any, tolerance: float = 0.0) -> bool:
    """Pure comparison used by every assertion. Never raises for a normal miss."""
    if operator == "eq":
        if is_number(actual) and is_number(expected):
            return abs(float(actual) - float(expected)) <= tolerance
        return actual == expected
    if operator == "ne":
        return not compare(actual, "eq", expected, tolerance)
    if operator in {"lt", "le", "gt", "ge"}:
        a, e = float(actual), float(expected)
        return {
            "lt": a < e,
            "le": a <= e + tolerance,
            "gt": a > e,
            "ge": a >= e - tolerance,
        }[operator]
    if operator == "in":
        return actual in expected
    if operator == "contains":
        return expected in actual
    if operator == "matches":
        return re.search(str(expected), str(actual)) is not None
    raise ValueError(f"unsupported operator: {operator}")


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def resolve_dry_run(assertion: Dict[str, Any]) -> Any:
    if "dry_run_actual" not in assertion:
        raise Unresolved(
            f"assertion '{assertion.get('id')}' has no dry_run_actual for --dry-run"
        )
    return assertion["dry_run_actual"]


def resolve_real(observer: Any, assertion: Dict[str, Any]) -> Any:
    source = assertion["source"]
    expression = assertion["expression"]
    try:
        if source in SNAPSHOT_SOURCES:
            obs = observer.snapshot()
            if obs.connected is False:
                raise Unresolved(obs.error or "not connected")
            if source == "target_state":
                return obs.target_running
            if source == "practice_state":
                return obs.practice_state
            return obs.message_type
        return observer.dbg.fnc(expression)
    except Unresolved:
        raise
    except Exception as exc:  # pragma: no cover - requires TRACE32
        raise Unresolved(f"{type(exc).__name__}: {exc}") from exc


def evaluate(
    test_case: Dict[str, Any],
    resolver,
    deadline: float,
) -> Dict[str, Any]:
    results: List[Dict[str, Any]] = []
    saw_error = False
    saw_fail = False
    saw_timeout = False

    for assertion in test_case["assertions"]:
        entry: Dict[str, Any] = {
            "id": assertion["id"],
            "source": assertion["source"],
            "expression": assertion["expression"],
            "operator": assertion["operator"],
            "expected": assertion["expected"],
        }
        if time.monotonic() > deadline:
            entry["outcome"] = "timeout"
            saw_timeout = True
            results.append(entry)
            continue
        try:
            actual = resolver(assertion)
        except Unresolved as exc:
            entry["outcome"] = "error"
            entry["error"] = str(exc)
            saw_error = True
            results.append(entry)
            continue

        entry["actual"] = actual
        try:
            passed = compare(
                actual,
                assertion["operator"],
                assertion["expected"],
                float(assertion.get("tolerance", 0) or 0),
            )
        except Exception as exc:
            entry["outcome"] = "error"
            entry["error"] = f"comparison failed: {type(exc).__name__}: {exc}"
            saw_error = True
            results.append(entry)
            continue

        entry["outcome"] = "pass" if passed else "fail"
        saw_fail = saw_fail or not passed
        results.append(entry)

    # Reduction order matters: error and timeout outrank fail so that a broken
    # environment is never reported as a firmware defect.
    if saw_error:
        verdict = "error"
    elif saw_timeout:
        verdict = "timeout"
    elif saw_fail:
        verdict = "fail"
    else:
        verdict = "pass"

    return {
        "test_id": test_case["id"],
        "title": test_case["title"],
        "verdict": verdict,
        "assertions": results,
    }


def to_junit(result: Dict[str, Any]) -> str:
    total = len(result["assertions"])
    failures = sum(1 for a in result["assertions"] if a["outcome"] == "fail")
    errors = sum(1 for a in result["assertions"] if a["outcome"] in {"error", "timeout"})

    suites = ET.Element("testsuites")
    suite = ET.SubElement(
        suites,
        "testsuite",
        name=result["test_id"],
        tests=str(total),
        failures=str(failures),
        errors=str(errors),
    )
    for a in result["assertions"]:
        case = ET.SubElement(
            suite,
            "testcase",
            classname=result["test_id"],
            name=a["id"],
        )
        detail = (
            f"source={a['source']} expr={a['expression']} "
            f"operator={a['operator']} expected={a.get('expected')!r} "
            f"actual={a.get('actual', 'unresolved')!r}"
        )
        if a["outcome"] == "fail":
            node = ET.SubElement(case, "failure", message="assertion failed")
            node.text = detail
        elif a["outcome"] in {"error", "timeout"}:
            node = ET.SubElement(case, "error", message=a.get("error", a["outcome"]))
            node.text = detail
    ET.indent(suites, space="  ")
    return ET.tostring(suites, encoding="unicode")


BUILTIN_SAMPLE = {
    "id": "TC-DRYRUN-SAMPLE",
    "title": "Built-in dry-run sample",
    "timeout_ms": 5000,
    "assertions": [
        {
            "id": "sample-eq",
            "source": "variable",
            "expression": "Var.VALUE(g_status)",
            "operator": "eq",
            "expected": 2,
            "dry_run_actual": 2,
        },
        {
            "id": "sample-stopped",
            "source": "target_state",
            "expression": "STATE.RUN()",
            "operator": "eq",
            "expected": False,
            "dry_run_actual": False,
        },
    ],
}


def load_test_case(path: Optional[str], dry_run: bool) -> Dict[str, Any]:
    if path:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    if dry_run:
        return BUILTIN_SAMPLE
    raise SystemExit("a --test-case path is required unless --dry-run is used")


def build_resolver(args, dry_run: bool):
    if dry_run:
        return resolve_dry_run, None

    script_dir = Path(__file__).resolve().parent
    if str(script_dir) not in sys.path:
        sys.path.insert(0, str(script_dir))
    from trace32_observer import Trace32Observer  # local wrapper

    observer = Trace32Observer(
        node=args.node,
        port=args.port,
        protocol=args.protocol,
        connect_timeout=args.timeout,
        dry_run=False,
    )
    observer.connect()
    return (lambda assertion: resolve_real(observer, assertion)), observer


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--test-case", help="Path to a test case JSON file.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--node", default="localhost")
    parser.add_argument("--port", type=int, default=20000)
    parser.add_argument("--protocol", default="TCP")
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--junit", help="Optional path to write JUnit XML.")
    parser.add_argument("--json", dest="json_out", help="Optional path to write JSON result.")
    args = parser.parse_args()

    test_case = load_test_case(args.test_case, args.dry_run)
    resolver, _observer = build_resolver(args, args.dry_run)

    deadline = time.monotonic() + float(test_case.get("timeout_ms", 5000)) / 1000.0
    result = evaluate(test_case, resolver, deadline)

    text = json.dumps(result, indent=2, sort_keys=True, default=str)
    print(text)
    if args.json_out:
        Path(args.json_out).write_text(text, encoding="utf-8")

    junit_xml = to_junit(result)
    if args.junit:
        Path(args.junit).write_text(junit_xml, encoding="utf-8")

    return VERDICT_EXIT[result["verdict"]]


if __name__ == "__main__":
    raise SystemExit(main())
