# Slice 17: Codex CLI Harness Adapter

## Scope

Add Codex as the second concrete implementation of the `HarnessAdapter` port.

The public CLI shape does not change:

```text
codealmanac ingest <inputs...> --using codex
```

The CLI still adapts argv into `RunIngestRequest`. The adapter lives under
`integrations/harnesses/codex/` and is wired by `create_app()` through
`default_harness_adapters()`.

## Architecture

The Python v1 adapter uses `codex exec`, not the archived TypeScript
app-server adapter.

```python
result = runner.run(
    "codex",
    (
        "exec",
        "--config",
        "mcp_servers={}",
        "--config",
        'approval_policy="never"',
        "--cd",
        str(cwd),
        "--ephemeral",
        "--sandbox",
        "workspace-write",
        "--ignore-rules",
        "--color",
        "never",
        "--output-last-message",
        str(output_path),
        "-",
    ),
    cwd,
    timeout,
    prompt,
)
```

`--output-last-message` is the result boundary. The adapter treats stdout and
stderr as diagnostics, reads the final assistant message from a temporary file,
and returns that text as `HarnessRunResult.output_text`.

`codex login status` is the readiness probe.

Shared subprocess and Git-status helpers now live in
`integrations/harnesses/command.py` and `integrations/harnesses/git_status.py`
instead of inside the Claude adapter. Claude and Codex share the same
changed-file reporting helper.

## Why Not App-Server Yet

The archived TypeScript adapter used Codex app-server because that product
needed streaming events, approval request handling, token usage, structured
tool display, actor traces, and app-server lifecycle cleanup.

The current Python harness contract is smaller: readiness, one prompt run,
final text, run status, and changed files. `codex exec` supports the needed
contract with stdin prompts, ephemeral sessions, workspace sandboxing, config
overrides, and final-message file output. App-server remains the upgrade path
if a later slice needs richer runtime events or provider-owned structured
output.

## Codex CLI Findings

The installed Codex help advertises approval flags, but `codex exec` rejects
`--ask-for-approval` and `-a` in this environment. The adapter therefore uses
the config override:

```text
--config approval_policy="never"
```

This was verified with a real `codex exec` smoke before CLI dogfood.

## Cosmic Python Translation

Chapter 2 defines the port as the application-facing interface and the adapter
as the concrete implementation behind it. It also says hard-to-write fakes are
design feedback. The `HarnessAdapter` port stayed stable; `CodexCliHarnessAdapter`
only translates Codex CLI behavior into service-owned models. Tests fake the
command runner, not Codex internals.

## Tests And Dogfood

- `tests/test_codex_adapter.py` covers readiness, missing executable, command
  construction, final-message absence, timeouts, changed files, and default app
  wiring.
- `tests/test_claude_adapter.py` now imports shared command/Git helpers so
  Claude no longer owns harness-wide subprocess machinery.
- The missing-harness ingest test injects `harness_adapters=()` so unit tests do
  not accidentally invoke real providers.
- Ingest now validates the post-harness Git snapshot before checking harness
  success. A failed provider run that mutates application files is reported as
  a mutation-safety failure, not hidden behind the provider failure.
- Focused adapter, ingest, harness, CLI, and architecture tests pass.
- Full `pytest`, full `ruff`, and `git diff --check` pass.
- Real `codex exec` smoke returned `ok` through `--output-last-message`.
- Real temp-repo `codealmanac ingest note.md --using codex` created
  `.almanac/pages/codex-adapter.md`; search found `codex-adapter`; Git status
  showed only that wiki page changed.
