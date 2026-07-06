# pyrcl Observation Loop

The central rule is: do not send a command and then wait blindly.

TRACE32 Remote API command return, CMM/PRACTICE completion, target execution
state, and displayed error messages are different signals. Treat them as
separate checks.

## Recommended Loop

1. Snapshot current state.
2. Validate the command envelope and risk level.
3. Verify connection with `ping()` or a low-risk function.
4. Send the command with an explicit timeout policy.
5. Immediately collect TRACE32 message text and type.
6. Poll PRACTICE state if a CMM or `DO` script may be active.
7. Poll target state with `STATE.RUN()` and debugger state.
8. Capture relevant AREA/window content.
9. Classify the result as `ok`, `command_error`, `practice_timeout`,
   `target_timeout`, `dialog_blocked`, `connection_lost`, or `unsafe_request`.
10. Run the next recovery step only if it is approved for that classification.

## Why `dbg.cmm(timeout=...)` Matters

pyrcl's `dbg.cmm(...)` is a safer default than raw `dbg.cmd("DO ...")`
because it is designed to wait for the PRACTICE stack to return. However,
`timeout=None` can wait forever and `timeout=0` is non-blocking. Always pass a
timeout and still collect messages and state around the call.

Use raw `DO` only when the surrounding controller intentionally owns a
non-blocking observation loop.

## Message Types

The underlying Remote API exposes TRACE32 messages with type information.
Operationally useful categories include:

- `0`: OK or no actionable message;
- `1`: information;
- `2`: error;
- `8`: status information;
- `16`: error information;
- `32` and `64`: temporary display or info messages.

The exact pyrcl wrapper surface can differ by version. Preserve both message
text and type when available.

## State Signals

Useful state sources:

- `dbg.get_state()` for debugger state;
- `dbg.fnc("STATE.RUN()")` for target run status;
- `dbg.fnc("STATE.TARGET()")` if supported in the environment;
- internal or wrapper access to PRACTICE state when available;
- AREA/window snapshots for text that would otherwise only be visible in the
  GUI.

`STATE.RUN()` alone is not enough. It can indicate that execution is running,
but it does not prove that the intended test progressed or that the debugger is
healthy.

## Command Envelope Result

Each action should return a structured result:

```json
{
  "status": "ok",
  "classification": "completed",
  "command_returned": true,
  "practice_state": "not_running",
  "debugger_state": 2,
  "target_running": false,
  "message": {
    "text": "",
    "type": 0
  },
  "evidence": {
    "area_tail": [],
    "window_snapshot": null
  }
}
```

This is the minimum useful shape for AI-agent supervision and CI diagnostics.

