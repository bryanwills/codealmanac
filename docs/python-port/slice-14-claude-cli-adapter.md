# Slice 14: Claude CLI Harness Adapter

## Scope

Add the first concrete harness adapter:

```python
app = create_app()
app.harnesses.check()
app.workflows.ingest.run(
    RunIngestRequest(cwd=repo, inputs=("note.md",), harness=HarnessKind.CLAUDE)
)
```

`create_app()` now wires `ClaudeCliHarnessAdapter` by default. Tests can still
pass `harness_adapters=()` or fake adapters to keep boundaries explicit.

## Architecture

The adapter lives under `integrations/harnesses/claude/` and implements the
service-owned `HarnessAdapter` port. `cli/`, `workflows/`, and `services/` do
not import integrations; `app.py` is the composition root that wires concrete
adapters.

```text
workflows/ingest
  -> services/harnesses
    -> HarnessAdapter protocol
      -> integrations/harnesses/claude/ClaudeCliHarnessAdapter
```

Cosmic Python chapter 3 frames abstractions as a way to hide messy external
details. Here, the workflow depends on `HarnessAdapter`; Claude subprocess
flags, auth JSON, output JSON, timeouts, and git changed-file detection stay in
the integration.

## Claude CLI Contract

The adapter uses Claude Code's non-interactive CLI mode:

```text
claude -p --output-format json --no-session-persistence \
  --permission-mode acceptEdits \
  --tools Read,Write,Edit,MultiEdit,Glob,Grep,LS \
  <prompt>
```

Readiness uses `claude auth status`, which returns JSON in the tested local CLI.
Run output uses Pydantic models over Claude's JSON result envelope; the adapter
does not scrape prose.

References:

- https://docs.anthropic.com/en/docs/claude-code/cli-reference
- https://docs.python.org/3/library/subprocess.html#subprocess.run

## Safety

The adapter snapshots `git status --porcelain=v1 -z --untracked-files=all`
before and after the Claude run and reports newly changed paths to the harness
result. `workflows/ingest` rejects reported changes outside `.almanac/`.

This is a first guard, not a complete sandbox. If the repo is already dirty or
not a Git repository, changed-file detection can miss some effects. The next
hardening step is stronger preflight policy before public `codealmanac ingest`.

## Dogfood Result

A real local Claude run on 2026-06-29 created one page in a temp repo:
`.almanac/pages/ingest-calls-services-directly.md`. The ingest workflow marked
the run `done`, refreshed the index to two pages, and `search` found the new
page.

The page used the phrase `almanac CLI`, which violated the product naming
contract. The ingest prompt now explicitly says the public CLI name is
`codealmanac`, never `almanac` or `alm`, and the focused ingest test pins that
prompt invariant.

## Tests

- Claude auth readiness success and missing command
- Claude `--print --output-format json` command construction
- JSON result parsing
- git changed-file path reporting
- invalid JSON and timeout failure handling
- default app wiring for the Claude adapter
- architecture guard preventing CLI/workflows/services from importing
  integrations
