# Branded Onboarding Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Restore the archive-style branded setup experience for the Python local-first product.

**Architecture:** `SetupService` remains the service-layer command for machine-level setup. The CLI edge resolves interactive choices and the renderer owns terminal presentation; setup never initializes, detects, registers, or mutates a repo `almanac/` tree.

**Tech Stack:** Python, Rich terminal rendering, Pydantic result models, pytest, uv, ruff.

---

## Source Of Truth

- `notes.md`: setup is computer-level onboarding and does not touch repo `almanac/`.
- `implementation-tickets.md` Ticket 12: restore archive setup feel with banner, badge, step rhythm, interactive questions, next-steps box, `--yes`, non-TTY support, and JSON output.
- `MANUAL.md`: keep product decisions in services and presentation at the CLI edge.
- Cosmic Python: command-shaped request objects and service-layer tests keep the workflow stable while the renderer changes.

## Code Wireframe

```python
auto_update = resolve_setup_auto_update(args)
result = app.setup.run(RunSetupRequest(auto_update=auto_update, ...))
render_setup_result(result, json_output=args.json)
```

`resolve_setup_auto_update` is CLI-edge behavior:

- `--no-auto-update` -> false
- `--yes` -> true
- non-TTY -> true
- `--json` -> true unless explicitly disabled
- interactive TTY -> ask "Do you want to keep CodeAlmanac up to date automatically?"

`SetupService.run` stays machine-level:

- install global agent instructions,
- set global auto-commit config,
- install sync/Garden/update automation according to request,
- return shaped setup result.

## Task 1: Correct The Product Boundary

**Files:**
- Modify: `notes.md`
- Modify: `implementation-tickets.md`

**Steps:**
1. Remove the repo init/detect requirement from Ticket 12.
2. Add the rule that `codealmanac setup` is computer-level onboarding.
3. Verify no plan/code change makes setup initialize repo `almanac/`.

## Task 2: Add Interactive Auto-Update Resolution

**Files:**
- Modify: `src/codealmanac/cli/dispatch/setup.py`
- Test: `tests/test_cli.py`

**Steps:**
1. Add `resolve_setup_auto_update(args)`.
2. Prompt only when stdin is TTY, `--yes` is absent, `--json` is absent, and `--no-auto-update` is absent.
3. Use default yes.
4. Keep non-TTY and `--yes` on the happy path.
5. Add tests for yes/default, explicit no, non-TTY, JSON, and `--no-auto-update`.

## Task 3: Restore The Branded Renderer

**Files:**
- Modify: `src/codealmanac/cli/render/setup.py`
- Test: `tests/test_cli.py`

**Steps:**
1. Replace the plain setup panel sequence with:
   - ASCII `CODEALMANAC` banner,
   - small `codealmanac` badge,
   - step table with status markers,
   - next-steps box.
2. Show these setup steps:
   - agent instructions,
   - sync automation,
   - Garden automation,
   - update automation,
   - auto-commit.
3. Keep uninstall rendering clear but do not make uninstall a second onboarding flow.
4. Add snapshot-style output assertions for stable user-facing text.

## Task 4: Preserve JSON And Script Behavior

**Files:**
- Modify: `src/codealmanac/cli/dispatch/setup.py`
- Modify: `src/codealmanac/cli/render/setup.py`
- Test: `tests/test_cli.py`
- Test: `tests/test_setup_service.py`

**Steps:**
1. Keep JSON output as the existing `SetupResult` model.
2. Ensure JSON setup does not prompt.
3. Ensure setup `--yes` installs update automation by default.
4. Ensure setup `--no-auto-update` skips only update automation.
5. Ensure no setup path creates or modifies repo `almanac/`.

## Task 5: Verify And Commit

**Commands:**

```bash
uv run pytest tests/test_setup_service.py tests/test_cli.py
uv run ruff check .
uv run pytest
git diff --check
```

Commit as:

```bash
git add notes.md implementation-tickets.md docs/plans/2026-07-06-branded-onboarding.md src tests
git commit -m "feat(ticket-12): restore branded onboarding"
```
