# Recovery Playbook

Recovery must be staged. Start with observation, then low-impact control, then
board-approved reset or power recovery. AI agents should not jump directly to
reset, flash, or register mutation.

## Failure Classes

### Connection Failure

Symptoms:

- pyrcl connect timeout;
- `ping()` fails;
- socket transmit or receive error;
- wrong PowerView instance or port.

First checks:

- confirm PowerView is running;
- confirm `RCL=NETTCP` and `PORT=20000` or the selected unique port;
- confirm firewall, localhost binding, VPN, and lab host route;
- confirm only one controller owns the session.

Recovery:

1. retry connect with a short bounded timeout;
2. try a low-risk query such as version or state;
3. if still failing, start or restart PowerView only through the local
   approved launcher.

### Command Error

Symptoms:

- command rejected;
- TRACE32 message type indicates error;
- syntax error, unknown command, command locked, or option locked.

Recovery:

1. capture message and command text;
2. stop command chain;
3. do not infer target state from the failed command;
4. run only observation probes until a human or policy approves the next step.

### PRACTICE Timeout

Symptoms:

- CMM did not return before timeout;
- PRACTICE state still running;
- dialog state is possible;
- CI job is waiting forever.

Recovery:

1. capture PRACTICE state, messages, and AREA/window text;
2. avoid starting another CMM on top of the blocked stack;
3. if approved, send a low-impact break/stop action;
4. if still blocked, terminate the session through the CI cleanup path and
   preserve evidence.

### Target Run Timeout

Symptoms:

- `STATE.RUN()` remains true after the expected breakpoint or stop condition;
- `Go` was issued without a bounded wait;
- target may be out of control.

Recovery:

1. capture target state and last message;
2. if policy allows, issue `Break`;
3. inspect PC and relevant variables;
4. only then consider board-specific reset.

### Hidden Dialog Or Headless Block

Symptoms:

- works in GUI but hangs with `SCREEN=OFF`;
- PRACTICE state indicates dialog;
- no progress in logs.

Recovery:

1. ban interactive commands in automation;
2. use `ENTRY` parameters or command envelopes instead of prompts;
3. capture AREA/window content;
4. fail fast with a classification that says `dialog_blocked`.

## Escalation Ladder

1. Observe only.
2. Reconnect and query state.
3. Capture evidence.
4. Stop target execution with approved `Break`.
5. Clean up PRACTICE/session through approved CI exit flow.
6. Run board-approved reset/power-cycle only if documented.
7. Require human approval for flash, register, watchdog, clock, or security
   state mutation.

## Board-Specific Runbook Template

```text
Board:
Probe:
TRACE32 build:
pyrcl version:
RCL protocol/port:
Power/reset owner:
Allowed observation commands:
Allowed execution control commands:
Approved reset sequence:
Commands requiring human approval:
Evidence files:
CI cleanup action:
Known failure signatures:
```

