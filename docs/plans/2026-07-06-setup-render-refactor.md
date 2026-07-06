# Setup Render Refactor Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Split setup terminal rendering into smaller ownership modules without changing setup or uninstall behavior.

**Architecture:** Keep CLI rendering at the edge. `SetupService` still returns typed facts, and `cli/render/` still owns terminal output. The split is by reason to change: brand/banner constants, terminal layout primitives, interactive setup screens, and setup/uninstall result rendering.

**Tech Stack:** Python 3.12, argparse CLI, Rich only inside `cli/render/`, pytest, ruff.

---

## Baseline

- Branch: `codex/macro-refactor-from-f2eb2c7`
- Source of truth: `f2eb2c7a1ac56c913d4a44ab24d5c3a2b553007c`
- `uv run pytest`: 401 passed on 2026-07-06
- `uv run ruff check .`: passed on 2026-07-06

## Boundary Target

Current pressure file:

- `src/codealmanac/cli/render/setup.py` is 612 lines and mixes setup result rendering, uninstall rendering, raw interactive choice screens, ANSI card layout, banner art, wrapping, and Rich panels.

Target files:

- Create `src/codealmanac/cli/render/brand.py` for setup brand constants and banner/badge rendering.
- Create `src/codealmanac/cli/render/terminal.py` for ANSI-aware terminal primitives.
- Create `src/codealmanac/cli/render/setup_screens.py` for interactive setup choice screen rendering.
- Keep `src/codealmanac/cli/render/setup.py` for setup/uninstall result rendering and public render functions.

## Task 1: Guard The Intended Split

**Files:**

- Modify: `tests/test_architecture.py`

**Steps:**

1. Add an architecture assertion that the setup renderer split files exist.
2. Keep the existing rule that Rich imports stay under `cli/render/`.
3. Add a line cap for `cli/render/setup.py` after extraction.
4. Run:
   `uv run pytest tests/test_architecture.py -q`
5. Expected before implementation: fail because the new modules do not exist or `setup.py` is still too large.

## Task 2: Extract Brand Rendering

**Files:**

- Create: `src/codealmanac/cli/render/brand.py`
- Modify: `src/codealmanac/cli/render/setup.py`

**Steps:**

1. Move setup banner art, color constants, brand color mapping, and badge/banner functions into `brand.py`.
2. Import those names from `setup.py`.
3. Run:
   `uv run pytest tests/test_cli.py::test_cli_setup_and_uninstall_codex_instructions -q`
4. Expected after implementation: pass.

## Task 3: Extract Terminal Primitives

**Files:**

- Create: `src/codealmanac/cli/render/terminal.py`
- Modify: `src/codealmanac/cli/render/setup.py`

**Steps:**

1. Move ANSI-aware helpers into `terminal.py`: visible length, terminal width, line writing, wrapping, card rows, box rows, and shell command rendering where shared.
2. Keep names plain and product-neutral.
3. Run:
   `uv run pytest tests/test_cli.py::test_cli_setup_and_uninstall_codex_instructions -q`
4. Expected after implementation: pass.

## Task 4: Extract Interactive Setup Screens

**Files:**

- Create: `src/codealmanac/cli/render/setup_screens.py`
- Modify: `src/codealmanac/cli/render/setup.py`
- Possibly modify: `src/codealmanac/cli/dispatch/setup_tui.py`

**Steps:**

1. Move `SetupChoiceOption`, `SetupChoiceScreen`, and all card-based choice screen rendering into `setup_screens.py`.
2. Preserve the import path used by dispatchers. If callers import the classes from `setup.py`, re-export them during the refactor only if that is needed for stable internal imports.
3. Run:
   `uv run pytest tests/test_cli.py::test_cli_setup_interactive_choices_can_disable_update_and_commits -q`
4. Expected after implementation: pass.

## Task 5: Verify The Whole Batch

**Files:**

- All changed files.

**Steps:**

1. Run:
   `uv run pytest tests/test_cli.py tests/test_setup_service.py tests/test_architecture.py -q`
2. Run:
   `uv run ruff check src/codealmanac/cli/render tests/test_cli.py tests/test_setup_service.py tests/test_architecture.py`
3. Run:
   `uv run pytest`
4. Run:
   `uv run ruff check .`
5. Run:
   `git diff --check`
6. Commit:
   `git add docs/refactor-audit-2026-07-06 docs/plans/2026-07-06-setup-render-refactor.md src/codealmanac/cli/render tests/test_architecture.py`
   `git commit -m "refactor: split setup terminal rendering"`
