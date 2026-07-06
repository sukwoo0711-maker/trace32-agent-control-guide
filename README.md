# TRACE32 Agent Control Guide

Practical guide for driving Lauterbach TRACE32 from any automated controller —
an AI agent, a CI job, or a local script — through the Remote API, pyrcl, and
PRACTICE/CMM scripts, without falling into blind waits, unsafe recovery commands,
or headless CI hangs.

This guide is deliberately harness-neutral. It does not depend on any specific AI
product, model, IDE, or agent runtime. "Controller" below means whatever drives
TRACE32: a human-run script, a CI pipeline, or an autonomous agent.

Research date: 2026-07-06 KST. Technical claims in this repo were verified against
PyPI metadata and the pyrcl source; see [docs/evidence-index.md](docs/evidence-index.md).

## Executive Recommendation

Adopt this pattern if any of these are true:

- Firmware tests are repeated often enough that manual TRACE32 operation is a
  bottleneck.
- An AI agent, CI job, or local script needs to control TRACE32 through the
  default Remote API port `20000`.
- CMM scripts sometimes hang, leave PowerView running, open dialogs, or fail
  differently in GUI and headless modes.
- Debug sessions need post-failure evidence such as messages, AREA/window
  snapshots, target state, and PRACTICE state.

Do not adopt the full stack yet if debugging is rare, board reset is not
documented, or the team cannot define which commands are safe to automate.
In that case, start with the observer loop and the CMM safety policy only.

The need is high for firmware automation and agent-driven debugging because
the biggest risk is not sending a command. The risk is believing the command
finished correctly when TRACE32 only accepted the command, a CMM script is
still running, the target is still executing, or an error is hidden in a
headless session.

## What To Build First

1. Enable Remote API on localhost using TCP and explicit port `20000`.
2. Put a thin Python observation layer between the agent and pyrcl.
3. Run every command through a command envelope with timeout, risk level,
   expected state, and evidence collection.
4. Replace blind sleeps with bounded polls of:
   command result, TRACE32 message, PRACTICE state, debugger state,
   `STATE.RUN()`, and selected AREA/window content.
5. Keep destructive recovery as board-approved playbooks, not default agent
   behavior.

## Repository Map

- [docs/unknowns-field-guide.md](docs/unknowns-field-guide.md) applies the
  known/unknown quadrant matrix to the TRACE32 hardware/GUI/target boundary.
- [docs/architecture.md](docs/architecture.md) describes the controller-to-
  TRACE32 control architecture.
- [docs/pyrcl-observation-loop.md](docs/pyrcl-observation-loop.md) is the core
  non-blind wait design.
- [docs/cmm-practice-guide.md](docs/cmm-practice-guide.md) covers practical
  CMM/PRACTICE rules and gotchas.
- [docs/test-verdict-model.md](docs/test-verdict-model.md) turns observations
  into deterministic PASS/FAIL verdicts and CI-readable reports.
- [docs/recovery-playbook.md](docs/recovery-playbook.md) classifies failures
  and recovery escalation.
- [docs/firmware-automation-patterns.md](docs/firmware-automation-patterns.md)
  connects the pattern to CI, HIL, and regression tests.
- [docs/research-notes.md](docs/research-notes.md) records the consolidated
  official and community findings.
- [docs/evidence-index.md](docs/evidence-index.md) lists official, GitHub,
  video, blog, and community sources.
- [examples/python/trace32_observer.py](examples/python/trace32_observer.py)
  provides a dry-run friendly observer wrapper for pyrcl.
- [examples/python/trace32_test_runner.py](examples/python/trace32_test_runner.py)
  evaluates a test case into a verdict and emits JUnit XML.
- [examples/cmm](examples/cmm) contains catalog-safe CMM examples and recovery
  candidates.
- [schemas/command_envelope.schema.json](schemas/command_envelope.schema.json)
  defines a structured controller-to-TRACE32 command envelope.
- [schemas/test_case.schema.json](schemas/test_case.schema.json) defines a
  structured MCU test case with assertions and evidence requests.

## Minimal RCL Configuration

Prefer TCP for new work:

```text
RCL=NETTCP
PORT=20000
```

UDP is still seen in older examples:

```text
RCL=NETASSIST
PACKLEN=1024
PORT=20000
```

Use one unique port per running PowerView instance. Restrict exposure to
localhost, VPN, or a trusted lab network because the RCL port is a remote
debugger control surface.

## Non-Blind Control Rule

Every automated action should answer these questions:

- Was the API connection alive before the command?
- Did TRACE32 accept the command?
- Did TRACE32 report an error message after accepting it?
- Is a PRACTICE script still running or blocked in a dialog?
- Is the target running, stopped, down, or in an unexpected state?
- What text evidence can be captured for a human review?
- What is the next safest recovery step?

That rule is the main design difference between an agent that merely sends
TRACE32 commands and an agent that can be trusted in firmware automation.

## Version Notes

- `lauterbach-trace32-rcl` latest observed release: `1.1.6`, released
  2026-07-02 on PyPI.
- ReadTheDocs may lag package metadata, so pin versions and read release notes.
- Always pass explicit `timeout=` values; defaults differ across docs and
  wrappers.

## Safety Boundary

This repository intentionally avoids executable examples for target-changing
commands such as `SYStem.RESet`, `SYStem.Up`, `SYStem.Down`, `FLASH.*`,
`Data.Set`, `Data.LOAD.*`, `Register.Set`, watchdog disable commands, and
terminal injection. Those belong in local, board-approved runbooks.

## Quick Validation

```bash
python scripts/validate_repo.py
python examples/python/trace32_observer.py --dry-run --command "PRINT agent_probe"
```

