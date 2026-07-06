# Agent Notes

This repository contains TRACE32 automation guidance and examples.

Rules for future agents:

- Keep generic examples read-only or bounded-control only.
- Do not add executable reset, flash, register-write, watchdog-disable, or
  terminal-injection commands without a board-specific approval document.
- Validate CMM examples with `python scripts/validate_repo.py`.
- Keep public docs free of proprietary target details, firmware dumps, license
  data, or lab hostnames.
- Prefer official Lauterbach docs for command semantics.

