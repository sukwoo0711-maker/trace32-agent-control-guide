#!/usr/bin/env python3
"""Repository sanity checks for docs, schemas, and CMM examples."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DANGEROUS_PATTERNS = [
    r"^\s*SYStem\.",
    r"^\s*RESet\b",
    r"^\s*Data\.LOAD\.",
    r"^\s*Data\.Set\b",
    r"^\s*Register\.Set\b",
    r"^\s*r\.s\b",
    r"^\s*Var\.set\b",
    r"^\s*FLASH\.",
    r"^\s*TERM\.Out\b",
    r"^\s*DIALOG\.",
    r"^\s*ENTER\b",
    r"^\s*PAUSE\b",
    r"^\s*STOP\b",
    r"^\s*SCREEN\.WAIT\b",
]


def main() -> int:
    errors: list[str] = []
    errors.extend(check_json())
    errors.extend(check_cmm())
    errors.extend(check_markdown_links())

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("validation ok")
    return 0


def check_json() -> list[str]:
    errors: list[str] = []
    for path in list((ROOT / "data").glob("*.json")) + list((ROOT / "schemas").glob("*.json")):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"{path.relative_to(ROOT)} is not valid JSON: {exc}")
    return errors


def check_cmm() -> list[str]:
    errors: list[str] = []
    for path in (ROOT / "examples" / "cmm").glob("*.cmm"):
        text = path.read_text(encoding="utf-8")
        if "ENDDO" not in text:
            errors.append(f"{path.relative_to(ROOT)} does not contain ENDDO")
        if path.name == "recovery_candidates.cmm":
            continue
        for number, line in enumerate(text.splitlines(), start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith(";"):
                continue
            for pattern in DANGEROUS_PATTERNS:
                if re.search(pattern, stripped, flags=re.IGNORECASE):
                    errors.append(
                        f"{path.relative_to(ROOT)}:{number} contains dangerous command: {stripped}"
                    )
    return errors


def check_markdown_links() -> list[str]:
    errors: list[str] = []
    for path in ROOT.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        for match in re.finditer(r"\]\(([^)]+)\)", text):
            target = match.group(1)
            if "://" in target or target.startswith("#"):
                continue
            local = (path.parent / target).resolve()
            if not str(local).startswith(str(ROOT.resolve())):
                errors.append(f"{path.relative_to(ROOT)} has out-of-root link {target}")
            elif not local.exists():
                errors.append(f"{path.relative_to(ROOT)} has missing link {target}")
    return errors


if __name__ == "__main__":
    raise SystemExit(main())

