# Unknowns Field Guide For TRACE32 Automation

The quality of any automated debugging workflow depends on shrinking the gap
between the *map* (scripts, plans, assumptions, tool docs) and the *territory*
(real silicon, probes, licenses, GUI state, target state, and CI behavior).

This is a generic engineering technique, not a product feature. It uses the
classic four-quadrant unknowns matrix (known knowns, known unknowns, unknown
knowns, unknown unknowns) and applies it to the specific boundary where
software, hardware, GUI state, and target state meet. It is useful whether the
automation is driven by a human-run script, a CI job, or an AI agent.

For TRACE32 that map/territory gap is large. A controller can know the exact
syntax of a command yet still fail because a probe is disconnected, a license is
missing, a CMM script opened a dialog, a hidden PowerView instance never quit, or
the target kept running after the command returned.

## When To Apply

Apply this unknowns-driven workflow when moving from interactive debugging to
repeated firmware tests, CI/HIL, scripted recovery, or agent-assisted debugging.
It is worth the overhead precisely because TRACE32 automation carries many
unknown unknowns at the hardware/GUI/target boundary.

Use a lighter version for mostly manual exploration. In that case keep only:

- a checklist of target/probe/license prerequisites;
- a safe CMM command policy;
- an observer that can collect state without changing the target.

## Known Knowns

- TRACE32 PowerView can be controlled through the Remote API.
- `lauterbach-trace32-rcl` (the Python Remote Control Library, commonly shortened
  to *pyrcl*) is the supported Python binding.
- Port `20000` is the common default Remote API port.
- PRACTICE/CMM is the native automation language.
- Firmware automation benefits from reproducible scripts and evidence capture.

## Known Unknowns

- Which exact TRACE32 build, pyrcl version, and CPU package will be used?
- Is the session GUI, hidden, `SCREEN=OFF`, or virtual console?
- Which commands are safe for this board and which require human approval?
- What is the board-specific reset sequence?
- What does "test passed" mean: breakpoint hit, variable value, log line, trace
  event, exit code, or CMM return macro? (See
  [test-verdict-model.md](test-verdict-model.md).)

## Unknown Knowns

These are often obvious to the firmware engineer but absent from the automation
inputs:

- Which jumper positions and power rails are required.
- Which CMM scripts are trusted locally but unsafe for a generic repo.
- Which target states are acceptable after a timeout.
- Which failures are recoverable by `Break` and which need a physical reset.
- Which log windows contain the evidence humans actually inspect.

## Unknown Unknowns To Hunt

- A command returns but the CMM script continues running.
- An error appears only as a TRACE32 message after command acceptance.
- A dialog is open in headless mode and blocks the PRACTICE stack.
- A global `ON ERROR` handler hides the root cause or recurses.
- Two PowerView instances share or race for the wrong RCL port.
- Recovery commands mutate flash, memory, registers, watchdogs, or clocks.
- The CI job kills PowerView before evidence is collected.

## Pre-Automation Blindspot Pass

Before enabling automated TRACE32 control on a new board, run this checklist.
It works as a human review step and also as a prompt for an AI assistant.

```text
Before writing control code for this board, perform a blindspot pass.
List assumptions about:
  - RCL config (protocol, port, packet length)
  - pyrcl / TRACE32 build versions
  - CMM scripts and their side effects
  - target reset and power ownership
  - command safety classification
  - GUI vs headless (SCREEN=OFF) behavior
  - evidence collection
  - CI cleanup
Separate what can be inferred from documentation from what must be verified on
the physical hardware. Do not treat inferred facts as verified.
```

That checklist turns "please automate TRACE32" into a workflow with explicit
unknowns, verification gates, and recovery boundaries.
