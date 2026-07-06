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

## Controller Pattern

Any controller (a local script, a CI job, or an AI agent) should operate like a
cautious test orchestrator:

- propose commands as structured envelopes;
- run policy checks before execution;
- collect state after each command;
- stop on uncertainty instead of escalating destructively;
- write implementation notes when a new failure mode appears.

## Test Case Lifecycle

A regression-grade MCU test is more than "run CMM from CI". Structure each test
as a lifecycle with a deterministic verdict:

1. **Select and skip early.** If the board, probe, license, or feature is
   missing, emit `skip` before touching the target.
2. **Baseline.** Confirm connection, versions, and a known target state. A dirty
   baseline is an `error`, not a `fail`.
3. **Setup.** Run a board-approved setup script (load, run to entry). Any
   target-mutating setup stays behind the approval gate.
4. **Assert.** Resolve each assertion from a read-only source and compare it to
   the expected value. See [test-verdict-model.md](test-verdict-model.md).
5. **Reduce.** Collapse assertions into one verdict: `pass`, `fail`, `error`,
   `timeout`, or `skip`, with the environment-vs-defect distinction preserved.
6. **Report.** Emit machine-readable results (JSON plus JUnit XML) with evidence.
7. **Teardown.** Clean up through the approved session path so no hidden
   PowerView instance survives.

The structured test case in
[../schemas/test_case.schema.json](../schemas/test_case.schema.json) and the
runner in
[../examples/python/trace32_test_runner.py](../examples/python/trace32_test_runner.py)
implement steps 4 to 6.

## Deterministic Verdicts And Reliability

- Never let an infrastructure fault (probe, license, connection, dialog) count as
  a firmware `fail`; classify it as `error` and retry a bounded number of times.
- Never retry a genuine `fail`; that hides defects.
- Prefer symbol-name assertions over raw addresses so verdicts survive relinks.
- Keep a stable test id so flaky tests are tracked, not silently tolerated.
- Gate the CI pipeline on the reduced verdict, and attach the evidence bundle for
  every non-pass result.

