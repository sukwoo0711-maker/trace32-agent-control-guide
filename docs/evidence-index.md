# Evidence Index

This file records the main sources used for the guide. It is not a complete
mirror of vendor documentation. Prefer the official source when behavior
matters.

## Original Prompt Source

- GeekNews topic 31107, "Fable field guide: finding my unknowns":
  <https://news.hada.io/topic?id=31107>

Useful application: start agentic engineering work by finding unknowns before
implementation. For TRACE32 this means explicitly listing hardware, RCL,
pyrcl, CMM, GUI/headless, recovery, and safety unknowns.

## Official Lauterbach And pyrcl Sources

- pyrcl ReadTheDocs:
  <https://pyrcl.readthedocs.io/>
- pyrcl installation:
  <https://pyrcl.readthedocs.io/en/latest/sub/installation.html>
- pyrcl basics:
  <https://pyrcl.readthedocs.io/en/latest/sub/intro_basics.html>
- pyrcl commands/functions:
  <https://pyrcl.readthedocs.io/en/latest/sub/intro_command_function.html>
- pyrcl PRACTICE macros:
  <https://pyrcl.readthedocs.io/en/latest/sub/intro_practice.html>
- PyPI package metadata:
  <https://pypi.org/project/lauterbach-trace32-rcl/>
- Remote API C reference:
  <https://www2.lauterbach.com/pdf/api_remote_c.pdf>
- Controlling TRACE32 via Python 3:
  <https://www2.lauterbach.com/pdf/app_python.pdf>
- PRACTICE user's guide:
  <https://www2.lauterbach.com/pdf/practice_user.pdf>
- PRACTICE reference guide:
  <https://www2.lauterbach.com/pdf/practice_ref.pdf>
- Error messages:
  <https://www2.lauterbach.com/pdf/error.pdf>
- t32rem support article:
  <https://support.lauterbach.com/kb/articles/how-to-use-the-t32rem-tool>
- Remote control PowerView support article:
  <https://support.lauterbach.com/kb/articles/how-to-remotely-control-trace32-powerview>
- Jenkins integration support article:
  <https://support.lauterbach.com/kb/articles/how-to-integrate-trace32-with-jenkins>
- Hidden TRACE32 instance support article:
  <https://support.lauterbach.com/kb/articles/how-do-i-start-a-hidden-instance-of-trace32>
- TRACE32 demo scripts note:
  <https://repo.lauterbach.com/scripts.html>
- pystart documentation:
  <https://lauterbach-trace32-pystart.readthedocs.io/>

## GitHub And Tooling Trends

- Official pyrcl mirror:
  <https://github.com/lauterbach-mirror/pyrcl>
- Lauterbach awesome TRACE32:
  <https://github.com/lauterbach-mirror/awesome-trace32>
- Zephyr TRACE32 runner context:
  <https://github.com/zephyrproject-rtos/zephyr-testing>
- t32xil:
  <https://github.com/lauterbach-mirror/t32xil>
- tree-sitter grammar for TRACE32:
  <https://github.com/xasc/tree-sitter-t32>
- TRACE32 language server:
  <https://github.com/xasc/t32-language-server>
- doxypractice:
  <https://github.com/lauterbach-mirror/doxypractice>
- VS Code PRACTICE extension:
  <https://marketplace.visualstudio.com/items?itemName=lauterbach.practice>
- Community Go wrapper:
  <https://github.com/yongzhy/t32>
- Emerging MCP/AI control examples:
  <https://github.com/ormastes/trace32_tools>
  and <https://github.com/hsoffar/lauterbach-trace32-mcp>

Trend: the ecosystem is moving toward Python wrappers, editor tooling, parser
tooling, CI/HIL integration, and early AI/MCP control. The missing layer is a
clear safety and observation protocol between the agent and TRACE32.

## Videos And Usage Reports

- Lauterbach videos around Remote API, Python control, PRACTICE tutorial, and
  automation were used as directional context. The implementation guidance in
  this repo relies on official PDFs and API docs for behavior.
- AdaCore TRACE32 CI demo:
  <https://www.adacore.com/videos/ada-source-level-debugging-with-lauterbach-trace32>
- Nohau real-time testing article:
  <https://nohau.eu/blogs/knowledge-center/enhancing-real-time-testing-with-lauterbach-trace32>
- SCHUTZWERK embedded fuzzing with TRACE32:
  <https://www.schutzwerk.com/en/blog/lauterbach-embedded-fuzzing-cooperation-2/>

## Community Signals

Community posts repeatedly show these failure themes:

- CI or service-account GUI behavior differs from desktop use.
- `SCREEN=OFF` can hide dialogs and visual errors.
- RCL config details such as port, protocol, pack length, and blank lines can
  cause connection failures.
- CMM examples in public repos are often board-specific and include reset,
  flash, register, watchdog, or memory mutation.
- Timeout-free `Go` and `WAIT` patterns can hang CI.

GeekNews direct searches for TRACE32/Lauterbach did not show a dedicated
thread, so GeekNews is used here for the "unknowns" workflow rather than as a
TRACE32 technical source.

