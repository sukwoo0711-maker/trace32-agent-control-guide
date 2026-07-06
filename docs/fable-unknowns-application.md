# Applying The "Unknowns" Field Guide

This guide started from the GeekNews topic
"Fable field guide: finding my unknowns". The useful takeaway is simple:
agentic coding quality depends on shrinking the gap between the map
(prompts, plans, assumptions, skills) and the territory (real code, tools,
hardware, licenses, physical boards, CI behavior, and failure modes).

For TRACE32 automation that gap is large. The agent can know the syntax for a
command, but the actual lab can still fail because a probe is disconnected, a
license is missing, a CMM script opened a dialog, a hidden PowerView instance
never quit, or the target kept running after a command returned.

## Apply Or Not

Apply this unknowns-driven workflow now if you are moving from interactive
debugging to repeated firmware tests, AI-assisted debugging, CI/HIL, or
scripted recovery. The workflow is necessary because TRACE32 automation has
many unknown unknowns at the boundary between software, hardware, GUI state,
and target state.

Use a lighter version if your work is mostly manual exploration. In that case,
keep only:

- a checklist of target/probe/license prerequisites;
- a safe CMM command policy;
- a Python observer that can collect state without changing the target.

## Known Knowns

- TRACE32 PowerView can be controlled through the Remote API.
- pyrcl is Lauterbach's Python Remote Control Library.
- Port `20000` is the common default Remote API port.
- PRACTICE/CMM is the native automation language.
- Firmware automation benefits from reproducible scripts and evidence capture.

## Known Unknowns

- Which exact TRACE32 build, pyrcl version, and CPU package will be used?
- Is the session GUI, hidden, `SCREEN=OFF`, or virtual console?
- Which commands are safe for this board and which require human approval?
- What is the board-specific reset sequence?
- What does "test passed" mean: breakpoint hit, variable value, log line,
  trace event, exit code, or CMM return macro?

## Unknown Knowns

These are often obvious to the firmware engineer but absent from prompts:

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

## Recommended Prompt Pattern

Before giving an AI agent TRACE32 control, ask it for a blindspot pass:

```text
I am automating TRACE32 for this board. Before writing code, perform a
blindspot pass. List assumptions about RCL config, pyrcl version, CMM scripts,
target reset, command safety, GUI/headless state, evidence collection, and CI
cleanup. Separate what can be inferred from what must be verified on hardware.
```

That prompt turns "please automate TRACE32" into a safer workflow with explicit
unknowns, verification gates, and recovery boundaries.

