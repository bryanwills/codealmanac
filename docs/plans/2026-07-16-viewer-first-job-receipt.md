# Viewer-First Job Receipt

**Goal:** Make lifecycle queue output clearly teach users how to follow work in
the local viewer's Jobs section instead of burying that action among metadata.

## Scope

- Redesign the human receipt shared by `init`, `ingest`, and `garden`.
- Give each operation a plain-language background-work headline.
- Put `codealmanac serve` and “Jobs in the sidebar” together inside a large,
  blue bordered next-action box.
- Keep `codealmanac jobs attach <run-id>` as the terminal alternative.
- Move the job id and repository name to quiet metadata at the bottom.
- Preserve the existing `--json` receipt exactly, including `runs_ahead` and
  `child_pid`.

## Output Shape

```text
◆ Building your CodeAlmanac in the background

  ╭──────────────────────────────────────────────────────────────╮
  │                                                              │
  │  Follow progress in the CodeAlmanac viewer                   │
  │                                                              │
  │    codealmanac serve                                         │
  │                                                              │
  │  Then select Jobs in the sidebar.                            │
  │                                                              │
  ╰──────────────────────────────────────────────────────────────╯

  Prefer the terminal?
    codealmanac jobs attach <run-id>

  Job: <run-id> · Repo: <name>
```

Ingest uses “Adding knowledge to your CodeAlmanac…” and Garden uses “Improving
your CodeAlmanac…”. The shared viewer and terminal instructions remain
identical.

## Files

- `src/codealmanac/cli/render/run_commands.py`: replace the metadata-first
  receipt and operation quips with the boxed viewer-first hierarchy.
- `tests/test_cli.py`: assert the three operation headlines, viewer guidance,
  terminal command, and quiet metadata.
- `README.md`: describe both viewer and terminal job-following paths.
- `almanac/architecture/cli/terminal-output.md`: preserve the output rationale.

## Verification

- Focused lifecycle CLI tests.
- `uv run pytest`.
- `uv run ruff check .`.
- `codealmanac validate`.

## Read Before Coding

- `MANUAL.md`
- `almanac/architecture/cli/terminal-output.md`
- `almanac/reference/cli/json-output-contract.md`
- `almanac/concepts/run-ledger.md`
