# Test Verdict Model

Sending commands is the easy half of MCU test automation. The hard half is
deciding, deterministically and with evidence, whether a test **passed**,
**failed**, or never ran cleanly. This document defines that decision model.

The single most damaging mistake in firmware CI is collapsing three different
outcomes into one:

- **FAIL** — the target ran and produced the wrong result. This is a real defect.
- **ERROR** — the environment broke (probe, license, connection, timeout, hidden
  dialog). The device under test is not implicated.
- **PASS** — the target ran and met every assertion, with evidence.

If ERROR is reported as FAIL, engineers stop trusting the suite. If ERROR is
reported as PASS, defects ship. Every verdict below therefore carries its class
and its evidence.

## Verdict States

| State | Meaning | Typical trigger |
|---|---|---|
| `pass` | All assertions held, evidence captured. | Expected variable/state observed. |
| `fail` | Target reachable, an assertion did not hold. | Variable mismatch, wrong PC, bad register. |
| `error` | Could not obtain a trustworthy observation. | Connection lost, license, dialog block. |
| `timeout` | Bounded wait expired before a decision. | `Go` never hit the stop condition. |
| `skip` | Preconditions not met, test not run. | Board/probe/feature unavailable. |

`fail` and `error` MUST be distinguishable in the report. A numeric assertion
that cannot be evaluated because the connection dropped is `error`, not `fail`.

## Verdict Sources

Each assertion draws its actual value from one observable source. All sources
below are read-only or bounded and map to TRACE32 functions the observer can
evaluate with `dbg.fnc(...)`.

| Source | TRACE32 expression example | Notes |
|---|---|---|
| Variable / symbol | `Var.VALUE(g_state)` | HLL variable by name; preferred for logic checks. |
| Register | `Register(PC)`, `Register(R0)` | CPU register read. |
| Memory | `Data.Long(A:0x20000000)` | Read-only memory access at an address. |
| Target run state | `STATE.RUN()` | True while executing; not proof of progress. |
| Breakpoint hit | `Register(PC)` after `STATE.RUN()` is false | Ran to and stopped at expected symbol. |
| PRACTICE result | `PRACTICE.SD()`, CMM `RETURN` macro | Script completed and returned a value. |
| Message | `get_message().type` | Error message types indicate command-level failure. |
| Terminal / semihosting | captured `TERM` / log line | Firmware `printf`-style evidence. |
| Trace event | analyzer/trace query | Advanced; gated by IP/security policy. |

`STATE.RUN()` alone is never a pass criterion. It reports motion, not the
intended result. Pair it with a value or location assertion.

## Assertion Model

An assertion is `actual <operator> expected`, with optional numeric tolerance.

- Operators: `eq`, `ne`, `lt`, `le`, `gt`, `ge`, `in`, `contains`, `matches`.
- Numeric comparisons SHOULD support `tolerance` for clocks, timers, and analog.
- Every assertion records `expected`, `actual`, `operator`, and `passed`.
- An assertion whose actual value cannot be resolved yields `error`, not `fail`.

A test's verdict is the reduction of its assertions:

1. any unresolved assertion -> `error`;
2. else any bounded wait expired -> `timeout`;
3. else any assertion false -> `fail`;
4. else -> `pass`.

See [../schemas/test_case.schema.json](../schemas/test_case.schema.json) for the
structured form and
[../examples/python/trace32_test_runner.py](../examples/python/trace32_test_runner.py)
for a dry-run-safe reference implementation.

## Evidence Binding

A verdict without evidence is an opinion. Each result MUST bundle:

- the resolved actual value and the expression used;
- target run state and debugger state at decision time;
- the last TRACE32 message text and type;
- relevant AREA/window lines;
- the elapsed time and timeout budget;
- for `error`, the exception class and message.

This bundle is what a human reviews and what a regression diff compares.

## Reliability And Flakiness

Hardware suites are noisy. Keep the noise out of the defect signal.

- Classify infrastructure faults as `error` and retry a bounded number of times;
  never retry a genuine `fail`, which would mask defects.
- Reserve hardware and confirm a clean baseline (connection, version, target
  state) before the first assertion.
- Record a stable `test id` so flaky tests can be tracked across runs.
- Prefer symbol-name assertions over raw addresses so results survive relinks.

## CI Reporting

Emit machine-readable results so dashboards and gates can consume them:

- map each test case to a JUnit `<testcase>`;
- map `fail` to `<failure>` and `error`/`timeout` to `<error>`;
- attach the evidence bundle as the element text or a linked artifact;
- keep the raw JSON result alongside the JUnit XML for deep inspection.

The reference runner emits both a JSON verdict and JUnit XML.
