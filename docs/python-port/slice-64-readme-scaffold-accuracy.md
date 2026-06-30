# Slice 64 - README Scaffold Accuracy

Date: 2026-06-30

## Scope

Correct the public README so new users can tell which files `codealmanac init`
creates immediately and which files are derived runtime state.

## Finding

The README tree under "What Gets Created" listed `config.toml`, `jobs/`, and
`index.db` beside the initialized wiki source files. A live temp-repo check of
`codealmanac init` showed the actual scaffold:

- `.gitignore`
- `almanac/README.md`
- `almanac/topics.yaml`
- `almanac/pages/getting-started.md`
- `almanac/manual/*.md`

The runtime files are valid product state, but they appear only when commands
need them. They are not init scaffold files.

## Decision

The public README now has two separate sections:

- `What Gets Created By Init`
- `Runtime State`

The distinction matches the slice 63 invariant: source wiki markers identify a
wiki root, while `index.db`, WAL files, and `jobs/` are rebuildable local
machine state.

## Guard

`tests/test_public_contract.py` now checks that the init scaffold section
contains source wiki files and does not list `index.db`, `jobs/`, or
`config.toml`.

## Cosmic Python Note

Chapter 2's Repository pattern frames persistence as an adapter around domain
logic. This slice applies the same product boundary in public language: the
repo-owned wiki source is the user-facing artifact, while SQLite/jobs are
storage/runtime details around that artifact.
