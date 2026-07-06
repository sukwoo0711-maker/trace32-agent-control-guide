# CMM And PRACTICE Guide

PRACTICE scripts are powerful enough to automate startup, board setup,
debugging, and regression tests. That power is also why CMM examples from the
internet should not be pasted into an AI-controlled workflow without review.

## Practical Syntax Rules

- CMM is line-oriented.
- Macros start with `&` and behave like text replacement, not typed variables.
- Use `PRIVATE` or `LOCAL` for script-local macros.
- Labels must start in the first column and end with `:`.
- End scripts with `ENDDO` so the PRACTICE stack unwinds cleanly.
- Prefer bounded loops and timeouts over endless loops.
- Avoid interactive commands in automation.

## Safe Example Command Set

This repository's executable examples use a conservative subset:

- flow: `ENTRY`, `PARAMETERS`, `PRIVATE`, `LOCAL`, `IF`, `ELSE`, `RePeaT`,
  `WHILE`, `GOTO`, `GOSUB`, `RETURN`, `ENDDO`;
- text/logging: `PRINT`, `AREA`, `OPEN`, `WRITE`, `CLOSE`;
- observation: `Var.PRINT`, `Var.WRITE`, `Var.EXPORT`, `Register(...)`,
  `Var.VALUE(...)`, `STATE.RUN()`, `FOUND()`, `FILE.EOF()`;
- bounded control: `WAIT`, `Go`, `Break`, `Step`, selected breakpoint setup
  only when explicitly needed.

## Avoid In Generic Automation

These are not generic examples. They require a board-specific approval gate:

- reset and debug-system state changes: `SYStem.*`, `SYStem.Up`,
  `SYStem.Down`, `SYStem.RESet`, `RESet`;
- flash and permanent memory actions: `FLASH.*`, mass erase, unlock;
- memory/register writes: `Data.Set`, `Data.LOAD.*`, `Register.Set`, `r.s`;
- watchdog or safety-feature disable commands;
- target terminal injection through `TERM.Out`;
- firmware dump commands such as broad `Data.SAVE.*`;
- UI blockers: `DIALOG.*`, `ENTER`, `PAUSE`, `STOP`, `SCREEN.WAIT`.

## CMM Design Pattern

Prefer small scripts with one responsibility:

```text
; probe_status.cmm
; collect state and write evidence, without changing target memory/registers
PRIVATE &LOG
ENTRY &LOG

OPEN #1 "&LOG" /Create
WRITE #1 "state_run=" STATE.RUN()
WRITE #1 "pc=" Register(PC)
CLOSE #1

ENDDO
```

For control scripts, include:

- explicit timeout macro;
- bounded wait;
- evidence write on both success and timeout;
- no interactive prompt;
- clear return artifact for Python to parse.

## CMM Review Checklist

- Does the script end with `ENDDO`?
- Are all loops bounded?
- Are all waits tied to a condition or timeout?
- Does it write enough evidence before exiting?
- Does it avoid dialogs and prompts?
- Are target-mutating commands isolated behind approval?
- Is the script safe in `SCREEN=OFF` or hidden CI mode?

