# Security

TRACE32 Remote API access can control a live target. Treat port `20000` and
other RCL ports as privileged debug interfaces.

Recommendations:

- bind RCL access to localhost or a trusted lab network;
- avoid exposing RCL ports to the public internet;
- do not commit firmware dumps, target secrets, license files, hostnames, or
  board credentials;
- require human approval for flash, reset, watchdog, register, memory, or
  terminal-injection operations;
- preserve logs when failures occur, but review them for proprietary data
  before publishing.

Please report security concerns privately to the repository owner.

