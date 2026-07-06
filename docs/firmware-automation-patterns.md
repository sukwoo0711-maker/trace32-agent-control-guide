# Firmware Automation Patterns

TRACE32 automation is most valuable when it makes firmware tests repeatable and
reviewable. The useful pattern is not "run CMM from CI"; it is "run CMM with
state observation, timeouts, evidence capture, and cleanup".

## CI/HIL Flow

1. Reserve hardware and probe.
2. Start or attach to the intended PowerView instance.
3. Verify RCL configuration and unique port.
4. Capture initial version, target, and connection state.
5. Run an approved setup script.
6. Run the test with bounded waits.
7. Capture evidence on success and failure.
8. Classify result and export machine-readable JSON.
9. Quit or clean up through the approved session path.
10. Release hardware.

## Good Test Artifacts

- CMM scripts with explicit input macros.
- Python command envelopes with timeouts and expected states.
- Logs that include target state and messages.
- AREA/window snapshots for what a human would inspect in the GUI.
- A failure bundle that survives CI cleanup.

## Post-Failure Evidence

Collect before destructive cleanup:

- command envelope;
- pyrcl exception class and message;
- TRACE32 message text/type;
- PRACTICE state;
- debugger state;
- `STATE.RUN()` and `STATE.TARGET()` where available;
- PC or selected registers if read-only access is approved;
- selected variable values;
- CMM log files;
- trace capture only if approved for IP/security policy.

## Headless Mode Notes

Headless or hidden PowerView sessions reduce GUI friction, but they hide
dialogs and visual clues. Therefore, `SCREEN=OFF` style runs should add more
text evidence, not less.

Always verify that the session exits. A missing quit/cleanup command can leave
hidden PowerView processes behind and poison the next CI job.

## AI-Agent Specific Pattern

AI agents should operate like cautious test orchestrators:

- propose commands as structured envelopes;
- run policy checks before execution;
- collect state after each command;
- stop on uncertainty instead of escalating destructively;
- write implementation notes when a new failure mode appears.

