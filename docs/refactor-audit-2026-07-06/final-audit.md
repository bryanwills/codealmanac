# Final Refactor Audit

Baseline: `f2eb2c7a1ac56c913d4a44ab24d5c3a2b553007c`

Branch: `codex/macro-refactor-from-f2eb2c7`

## Result

This pass stops after five behavior-preserving refactor commits. The branch
keeps the existing product surface and improves the parts with clear boundary
pressure:

- setup rendering no longer hides a terminal toolkit in one command renderer;
- app composition reads as grouped manual dependency wiring;
- sync execution no longer repeats ledger write mechanics across foreground and
  background paths;
- raw parser and validator boundaries no longer use production `Any`;
- Codex app-server notification dispatch no longer owns event-construction
  details.

## Verification

Every committed code batch passed:

- `uv run pytest`
- `uv run ruff check .`
- `git diff --check`

The final code batch passed `402` tests.

## Remaining Large Files

The largest remaining classes and files are not automatic refactor targets.
They are mostly documented facades, orchestration services, or provider
adapters:

- `services/runs/store.py`
- `services/topics/mutations.py`
- `services/viewer/service.py`
- `workflows/page_run/service.py`
- `workflows/sync/evaluation.py`
- `integrations/harnesses/codex/app_server.py`

Further splitting these now would be mostly taste unless a new feature exposes
a specific reason-to-change problem.

## Product Questions Preserved

Behavior that may be product slop remains recorded in `product-slop.md`.
No behavior was changed to simplify architecture.

## Stop Rationale

The branch has reached the point where the next obvious moves are smaller
local preferences, not macro architecture improvements. The codebase now has
stronger boundaries around the areas that were actively hard to scan or extend,
and the remaining complexity appears tied to actual product behavior.
