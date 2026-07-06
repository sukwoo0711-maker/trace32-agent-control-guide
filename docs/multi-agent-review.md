# Multi-Agent Review Notes

Two research agents were used during preparation.

## Official Documentation Scout

Focus:

- Lauterbach official PDFs;
- pyrcl ReadTheDocs;
- PyPI release metadata;
- support articles.

Key findings:

- TCP on RCL port `20000` is the recommended modern baseline.
- `T32_Cmd` command acceptance is not the same as CMM completion.
- `T32_GetPracticeState`, TRACE32 message type, debugger state, and target run
  state are separate signals.
- CMM waits should be bounded and condition-based.
- Error state handling should avoid recursive or hidden `ON ERROR` behavior.
- pyrcl `1.1.6` was the latest observed PyPI release on 2026-07-02.

## Community And Trend Scout

Focus:

- GitHub projects;
- CI/HIL examples;
- usage reports;
- blogs and Q&A.

Key findings:

- CI/headless failure modes are a major practical risk.
- Hidden PowerView sessions must be explicitly cleaned up.
- Public CMM examples often include unsafe board-specific commands.
- Emerging AI/MCP TRACE32 tools exist, but need allowlists and evidence
  capture before broad use.
- Parser/editor tooling is useful for authoring, but syntax highlighting is not
  semantic safety.

## Integrated Decision

The guide recommends a small but strict control layer:

- structured command envelopes;
- command safety policy;
- explicit timeouts;
- state polling;
- evidence capture;
- recovery escalation.

This is more important than adding a large framework. The hard part is not API
access. The hard part is knowing whether TRACE32, PRACTICE, the target, and CI
are actually in the state the agent assumes.

