# Slice 66 - README Lifecycle Source Examples

Date: 2026-06-30

## Scope

Make the README lifecycle examples match source-resolution behavior in this
repository.

## Finding

The README used:

```bash
codealmanac ingest docs/adr.md --using codex
```

The command parses, but `docs/adr.md` does not exist in this checkout. A
release-surface dogfood pass resolved it as `path.unknown`, which makes the
example a missing-path example rather than a clean local-file example.

## Decision

The README now uses:

```bash
codealmanac ingest README.md --using codex
```

`README.md` exists in this repo and resolves as `SourceKind.PATH_FILE`. The
GitHub example remains `github:pr:123` because the source grammar explicitly
supports `github:pr:<number>`.

## Guard

`tests/test_public_contract.py` parses the README lifecycle examples and
resolves `README.md` plus `github:pr:123` through `SourcesService`.

## Cosmic Python Note

Chapter 3's abstraction chapter shows why testable boundaries matter around
messy I/O. This slice applies that idea to public examples: instead of checking
only text, the guard uses the source abstraction to verify that the documented
local-file input resolves as the intended source kind.
