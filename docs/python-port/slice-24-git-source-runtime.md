# Slice 24 - Git Source Runtime

## Scope

Make existing Git source refs useful to Ingest:

```text
codealmanac ingest git:diff
codealmanac ingest git:diff:<target>
codealmanac ingest git:range:<range>
```

This slice adds runtime source snapshots for local Git refs. It does not fetch
GitHub PRs or issues yet.

## Design

The source model now has four layers:

```text
SourceAddress -> SourceRef -> SourceBrief -> SourceRuntime
```

`SourceBrief` remains the operation-facing identity and provenance hint.
`SourceRuntime` is bounded readable material gathered before the harness runs.
For Git, that material is commit lists, status, stats, and diffs.

`services/sources/ports.py` owns `SourceRuntimeAdapter`. `SourcesService`
selects the first adapter that supports a ref. `app.py` wires the default Git
runtime adapter.

The Git adapter uses the Git CLI through the existing `CommandRunner` seam. We
looked at GitPython and Dulwich, but the local product needs exact porcelain
behavior for `git diff`, `git diff --cached`, and revision ranges. Using the
Git CLI keeps semantics aligned with the user's repository and avoids a partial
Git object model in CodeAlmanac.

Cosmic Python shaped the boundary: chapter 13 treats multi-operation external
dependencies as proper adapters with fakes in tests, and chapter 4 keeps the
service layer dependent on abstractions rather than details.

## Runtime Shapes

`git:diff` captures:

- `git status --short`
- unstaged `git diff --stat`
- unstaged `git diff --no-ext-diff`
- staged `git diff --cached --stat`
- staged `git diff --cached --no-ext-diff`

`git:diff:<target>` captures:

- `git diff --stat <target>`
- `git diff --no-ext-diff <target>`

`git:range:<range>` captures:

- `git log --oneline --decorate <range>`
- `git diff --stat <range>`
- `git diff --no-ext-diff <range>`

Snapshots are capped at 60,000 characters and mark `truncated: true` when the
cap is hit.

## Tests

- `tests/test_sources_service.py` covers the Git runtime adapter through a fake
  command runner.
- `tests/test_ingest_workflow.py` covers prompt inclusion through a fake
  `SourceRuntimeAdapter`.
- Focused tests include the architecture guard so source runtime does not make
  services import integrations.

## Deferred

GitHub PR and issue source runtime remains the next source-runtime gap. It
should use the same `SourceRuntimeAdapter` port, likely through authenticated
`gh` CLI commands in local v1.
