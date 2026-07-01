---
title: Codex App-Server Harness Adapter
summary: >-
  The Python Codex harness adapter runs CodeAlmanac lifecycle tasks through
  `codex app-server --listen stdio://`, maps provider notifications into
  normalized harness events, and keeps changed-file accounting around the run.
topics:
  - agents
  - provider-harness
  - systems
sources:
  - id: codex-adapter
    type: file
    path: src/codealmanac/integrations/harnesses/codex/adapter.py
    note: Defines Codex readiness checks, app-server delegation, and changed-file reporting.
  - id: app-server-client
    type: file
    path: src/codealmanac/integrations/harnesses/codex/app_server.py
    note: Owns Codex app-server run startup, noninteractive request responses, sandbox policy, turn completion, and result projection.
  - id: app-server-rpc
    type: file
    path: src/codealmanac/integrations/harnesses/codex/rpc.py
    note: Owns the line-oriented JSON-RPC subprocess boundary for `codex app-server`.
  - id: app-server-events
    type: file
    path: src/codealmanac/integrations/harnesses/codex/events.py
    note: Maps Codex app-server notifications into normalized `HarnessEvent` values.
  - id: app-server-display
    type: file
    path: src/codealmanac/integrations/harnesses/codex/display.py
    note: Maps Codex item payloads into structured tool display records.
  - id: harness-models
    type: file
    path: src/codealmanac/services/harnesses/models.py
    note: Defines normalized run, event, actor, tool display, usage, and failure models.
  - id: default-adapters
    type: file
    path: src/codealmanac/integrations/harnesses/__init__.py
    note: Wires the default Claude CLI and Codex app-server harness adapters.
  - id: codex-adapter-tests
    type: file
    path: tests/test_codex_adapter.py
    note: Covers readiness, default app wiring, and changed-file accounting around an app-server run.
  - id: codex-app-server-tests
    type: file
    path: tests/test_codex_app_server_adapter.py
    note: Covers the fake app-server handshake, noninteractive responses, event mapping, helper-turn handling, usage, and timeouts.
---

# Codex App-Server Harness Adapter

`CodexAppServerHarnessAdapter` is the Python rewrite's Codex implementation of the [[harness-providers]] adapter contract. The adapter advertises `HarnessKind.CODEX`, is included in `default_harness_adapters()` with the Claude CLI adapter, and delegates execution to `CodexAppServerClient`. [@codex-adapter] [@harness-models] [@default-adapters]

Readiness is still a local CLI check. `check()` runs `codex login status` from `Path.cwd()` with a 10-second timeout, reports `codex not found on PATH` for `FileNotFoundError`, reports `codex login status timed out` for timeout, and otherwise uses the first non-empty status line as the readiness message. [@codex-adapter]

Runs use `codex app-server --config mcp_servers={} --listen stdio://`, not `codex exec`. The client sends `initialize`, then `thread/start` with `approvalPolicy: "never"`, `sandbox: "workspace-write"`, and `ephemeral: true`, then `turn/start` with the CodeAlmanac prompt as a text input item and `sandboxPolicy.networkAccess: false`. [@app-server-client] [@app-server-rpc] [@codex-app-server-tests]

Server-initiated requests are handled noninteractively so lifecycle jobs do not block. Command and file-change approval requests are declined, user-input and elicitation requests get empty/declined responses, permission requests get an empty turn-scoped grant, and ChatGPT auth-token refresh gets a JSON-RPC error because CodeAlmanac does not manage Codex auth tokens. [@app-server-client] [@codex-app-server-tests]

The inspectable transcript surface is the normalized event stream. App-server notifications map text deltas, final text, tool starts/results, warnings, errors, usage updates, provider sessions, root/helper actors, helper-agent trace events, and final done events into `HarnessEvent` values. Base64 command output deltas are decoded before they are shown as tool summaries. [@app-server-events] [@app-server-display] [@harness-models] [@codex-app-server-tests]

Changed-file reporting is based on Git status snapshots around the app-server run. The adapter records `git status --porcelain=v1 -z --untracked-files=all` before and after the run, returns only paths added to the status set, and includes those paths regardless of whether the provider result succeeded or failed. [@codex-adapter] [@codex-adapter-tests]
