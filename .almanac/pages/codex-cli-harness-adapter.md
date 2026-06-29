---
title: Codex CLI Harness Adapter
summary: >-
  The Python Codex harness adapter runs one CodeAlmanac agent task through
  `codex exec` with workspace-write sandboxing, disabled user MCP servers, and
  final-message capture through a temporary output file.
topics:
  - agents
  - provider-harness
  - systems
sources:
  - id: codex-adapter
    type: file
    path: src/codealmanac/integrations/harnesses/codex/adapter.py
    note: Defines Codex readiness checks, `codex exec` arguments, run timeout handling, final-message capture, and changed-file reporting.
  - id: harness-models
    type: file
    path: src/codealmanac/services/harnesses/models.py
    note: Defines `HarnessKind.CODEX`, `HarnessRunStatus`, readiness records, and run results.
  - id: harness-service
    type: file
    path: src/codealmanac/services/harnesses/service.py
    note: Routes `RunHarnessRequest` values to adapters by harness kind and rejects duplicate adapter registrations.
  - id: default-adapters
    type: file
    path: src/codealmanac/integrations/harnesses/__init__.py
    note: Wires the default Claude and Codex CLI harness adapters.
  - id: codex-adapter-tests
    type: file
    path: tests/test_codex_adapter.py
    note: Covers readiness, missing executable handling, `codex exec` arguments, final-message failures, timeouts, and default app wiring.
---

# Codex CLI Harness Adapter

`CodexCliHarnessAdapter` is the Python rewrite's Codex implementation of the [[harness-providers]] adapter contract. The adapter advertises `HarnessKind.CODEX`, uses the local `codex` executable, and is included in `default_harness_adapters()` with the Claude CLI adapter. [@codex-adapter] [@harness-models] [@default-adapters]

Readiness is a local CLI check. `check()` runs `codex login status` from `Path.cwd()` with a 10-second timeout, reports `codex not found on PATH` for `FileNotFoundError`, reports `codex login status timed out` for timeout, and otherwise uses the first non-empty status line as the readiness message. [@codex-adapter]

Runs use `codex exec`, not the older app-server path documented for the archived TypeScript implementation. The command includes `--config mcp_servers={}`, `--config approval_policy="never"`, `--cd <cwd>`, `--ephemeral`, `--sandbox workspace-write`, `--ignore-rules`, `--color never`, `--output-last-message <tempfile>`, and `-`; the CodeAlmanac prompt is sent on stdin. [@codex-adapter] [@codex-adapter-tests]

The result boundary is file-based. The adapter creates a temporary directory with the `codealmanac-codex-` prefix, asks Codex to write the final message to `last-message.txt`, trims that file, and fails the run when the file is absent or empty. [@codex-adapter]

Changed-file reporting is based on git status snapshots. The adapter records `git status --porcelain=v1 -z --untracked-files=all` before and after the Codex run, returns only paths added to the status set, and still includes those paths on a nonzero Codex exit when they are available. [@codex-adapter] [@codex-adapter-tests]
