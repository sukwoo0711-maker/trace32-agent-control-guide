# Research Notes And Consolidated Findings

This guide was built by cross-checking two source classes and reconciling them.
The findings below are technical conclusions, independent of how the review was
performed. Prefer the official Lauterbach source when behavior matters.

## Source Class 1: Official Documentation

Scope: Lauterbach official PDFs, the pyrcl documentation, PyPI release metadata,
and support articles.

Findings:

- TCP on RCL port `20000` is the recommended modern baseline; UDP appears mainly
  in older examples.
- `T32_Cmd`-level command acceptance is not the same as CMM/PRACTICE completion.
- `T32_GetPracticeState`, the TRACE32 message type, the debugger state, and the
  target run state are four separate signals and must be polled separately.
- CMM waits should be bounded and condition-based, not open-ended.
- Error handling should avoid recursive or hidden `ON ERROR` behavior.
- The `lauterbach-trace32-rcl` package (pyrcl) exposes `connect()`, and on the
  returned debugger object: `cmd(...)`, `fnc(...)`, `cmm(..., timeout=...)`,
  `ping()`, `get_message()` (returns `text` and `type`), and `get_state()`.
  See [evidence-index.md](evidence-index.md) for version specifics.

## Source Class 2: Community And Ecosystem

Scope: public GitHub projects, CI/HIL examples, usage reports, blogs, and Q&A.

Findings:

- CI and headless failure modes are a major practical risk.
- Hidden PowerView sessions must be explicitly cleaned up or they poison later
  jobs.
- Public CMM examples often include unsafe board-specific commands.
- Editor and parser tooling (syntax, language server, tree-sitter) helps with
  authoring, but syntax highlighting is not semantic safety.
- Early AI/MCP TRACE32 control tools exist, but they need command allowlists and
  evidence capture before broad use.

## Integrated Conclusion

The high-value layer is a small but strict control protocol, not a large
framework:

- structured command envelopes;
- a command safety policy;
- explicit timeouts;
- state polling;
- evidence capture;
- staged recovery escalation.

The hard part is not API access. The hard part is knowing whether TRACE32,
PRACTICE, the target, and CI are actually in the state the controller assumes.
