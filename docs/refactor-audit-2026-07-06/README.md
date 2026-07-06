# CodeAlmanac Macro Refactor Audit

Date: 2026-07-06

Branch: `codex/macro-refactor-from-f2eb2c7`

Baseline commit: `f2eb2c7a1ac56c913d4a44ab24d5c3a2b553007c`

Source of truth: this baseline commit is the exclusive product and behavior
reference for this refactor branch.

## Goal

Refactor the Python CodeAlmanac codebase without changing product behavior.
The refactor should improve names, boundaries, extension points, and the
overall code shape until further changes are mostly diminishing returns.

## Rules For This Run

- Keep behavior stable against the baseline commit.
- Commit only to this refactor branch.
- Do not merge into the baseline branch.
- Follow `MANUAL.md`, `almanac/style/`, `docs/python-port-live-agreement.md`,
  and the local Cosmic Python references.
- Keep product questions separate from implementation changes.

## Baseline Evidence

- `uv run pytest`: 401 passed on 2026-07-06.
- `uv run ruff check .`: passed on 2026-07-06.
- `uv run codealmanac --help`: command surface includes `init`, `ingest`,
  `garden`, `sync`, read commands, `config`, `setup`, `uninstall`, `doctor`,
  `update`, `jobs`, and `automation`.

## Current Hypothesis

The repo is not in need of a full top-level rewrite. The broad folders still
match the intended shape:

```text
cli/server -> app -> workflows -> services -> ports/stores -> integrations
```

The likely refactor work is local and architectural:

- split large mixed modules where the reason to change is no longer singular;
- keep intentional facades only where they protect a stable service boundary;
- move terminal UI machinery out of command-result rendering modules where it
  obscures product output behavior;
- make composition wiring easier to scan without hiding business logic;
- update architecture tests when the target architecture changes for a real
  reason.

## Files In This Audit

- `worklog.md`: running notes and evidence.
- `source-map.md`: current architecture map.
- `smells.md`: strongest code-shape findings.
- `product-slop.md`: behavior that looks architecturally costly but may be a
  product decision.
- `target-architecture.md`: desired end shape.
- `refactor-roadmap.md`: ordered implementation batches.
