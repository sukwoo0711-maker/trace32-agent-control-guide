#!/usr/bin/env python3
"""Small TRACE32/pyrcl observer wrapper.

The module is safe to run without TRACE32 when --dry-run is used. Real mode
requires Lauterbach's lauterbach-trace32-rcl package and a running PowerView
instance with Remote API enabled.
"""

from __future__ import annotations

import argparse
import json
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


ERROR_MESSAGE_TYPES = {2, 16}


@dataclass
class Observation:
    connected: Optional[bool] = None
    message_text: Optional[str] = None
    message_type: Optional[int] = None
    practice_state: Optional[Any] = None
    debugger_state: Optional[Any] = None
    target_running: Optional[bool] = None
    error: Optional[str] = None
    area_tail: list[str] = field(default_factory=list)


class Trace32Observer:
    def __init__(
        self,
        node: str = "localhost",
        port: int = 20000,
        protocol: str = "TCP",
        connect_timeout: float = 5.0,
        dry_run: bool = False,
    ) -> None:
        self.node = node
        self.port = port
        self.protocol = protocol
        self.connect_timeout = connect_timeout
        self.dry_run = dry_run
        self.dbg: Any = None

    def connect(self) -> None:
        if self.dry_run:
            return

        import lauterbach.trace32.rcl as t32  # type: ignore

        self.dbg = t32.connect(
            node=self.node,
            port=self.port,
            protocol=self.protocol,
            timeout=self.connect_timeout,
        )

    def snapshot(self) -> Observation:
        if self.dry_run:
            return Observation(
                connected=True,
                message_text="dry-run",
                message_type=0,
                practice_state="not_running",
                debugger_state="dry-run",
                target_running=False,
            )

        obs = Observation()

        try:
            self.dbg.ping()
            obs.connected = True
        except Exception as exc:  # pragma: no cover - requires TRACE32
            obs.connected = False
            obs.error = f"ping failed: {type(exc).__name__}: {exc}"
            return obs

        try:
            msg = self.dbg.get_message()
            obs.message_text = getattr(msg, "text", None)
            obs.message_type = getattr(msg, "type", None)
        except Exception as exc:  # pragma: no cover - requires TRACE32
            obs.error = append_error(obs.error, f"message failed: {exc}")

        try:
            if hasattr(self.dbg, "_get_practice_state"):
                obs.practice_state = self.dbg._get_practice_state()
        except Exception as exc:  # pragma: no cover - requires TRACE32
            obs.error = append_error(obs.error, f"practice state failed: {exc}")

        try:
            if hasattr(self.dbg, "get_state"):
                obs.debugger_state = self.dbg.get_state()
        except Exception as exc:  # pragma: no cover - requires TRACE32
            obs.error = append_error(obs.error, f"debugger state failed: {exc}")

        try:
            value = self.dbg.fnc("STATE.RUN()")
            obs.target_running = normalize_bool(value)
        except Exception as exc:  # pragma: no cover - requires TRACE32
            obs.error = append_error(obs.error, f"STATE.RUN failed: {exc}")

        return obs

    def command_checked(
        self,
        command: str,
        timeout_s: float,
        kind: str = "cmd",
        poll_interval_s: float = 0.2,
    ) -> Dict[str, Any]:
        before = self.snapshot()
        started_at = time.monotonic()

        if self.dry_run:
            after = self.snapshot()
            return result_dict("ok", "dry_run", before, after, command, kind)

        try:
            if kind == "cmd":
                self.dbg.cmd(command)
            elif kind == "fnc":
                value = self.dbg.fnc(command)
                after = self.snapshot()
                data = result_dict("ok", "function_returned", before, after, command, kind)
                data["function_value"] = value
                return data
            elif kind == "cmm":
                self.dbg.cmm(command, timeout=timeout_s)
            else:
                raise ValueError(f"unsupported command kind: {kind}")
        except TimeoutError as exc:
            after = self.snapshot()
            data = result_dict("timeout", "practice_timeout", before, after, command, kind)
            data["error"] = f"{type(exc).__name__}: {exc}"
            return data
        except Exception as exc:  # pragma: no cover - requires TRACE32
            after = self.snapshot()
            data = result_dict("error", "command_error", before, after, command, kind)
            data["error"] = f"{type(exc).__name__}: {exc}"
            return data

        while time.monotonic() - started_at < timeout_s:
            after = self.snapshot()
            if is_error_message(after):
                return result_dict("error", "trace32_message_error", before, after, command, kind)
            if kind != "cmm" or practice_complete(after.practice_state):
                return result_dict("ok", "completed", before, after, command, kind)
            time.sleep(poll_interval_s)

        after = self.snapshot()
        return result_dict("timeout", "observation_timeout", before, after, command, kind)


def append_error(current: Optional[str], new: str) -> str:
    if current:
        return f"{current}; {new}"
    return new


def normalize_bool(value: Any) -> Optional[bool]:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "1", "yes"}:
            return True
        if lowered in {"false", "0", "no"}:
            return False
    if isinstance(value, (int, float)):
        return bool(value)
    return None


def practice_complete(state: Any) -> bool:
    if state is None:
        return True
    if isinstance(state, str):
        return state.lower() in {"not_running", "not running", "0", "stopped"}
    return state == 0


def is_error_message(obs: Observation) -> bool:
    return obs.message_type in ERROR_MESSAGE_TYPES


def result_dict(
    status: str,
    classification: str,
    before: Observation,
    after: Observation,
    command: str,
    kind: str,
) -> Dict[str, Any]:
    return {
        "status": status,
        "classification": classification,
        "command": {"kind": kind, "text": command},
        "before": before.__dict__,
        "after": after.__dict__,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--node", default="localhost")
    parser.add_argument("--port", type=int, default=20000)
    parser.add_argument("--protocol", default="TCP")
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--kind", choices=["cmd", "fnc", "cmm"], default="cmd")
    parser.add_argument("--command", default="PRINT agent_probe")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    observer = Trace32Observer(
        node=args.node,
        port=args.port,
        protocol=args.protocol,
        connect_timeout=args.timeout,
        dry_run=args.dry_run,
    )
    observer.connect()
    result = observer.command_checked(args.command, timeout_s=args.timeout, kind=args.kind)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())

