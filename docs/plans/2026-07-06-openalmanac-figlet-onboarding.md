# OpenAlmanac Figlet Onboarding Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace the setup summary panel with the archive-style installer rhythm and the OpenAlmanac figlet banner.

**Architecture:** Keep setup product behavior in `SetupService`. Keep the visual system inside `src/codealmanac/cli/render/setup.py`; the dispatch layer only owns the interactive auto-update prompt.

**Tech Stack:** Python, Rich, pytest.

---

### Task 1: Port The Figlet Banner

**Files:**
- Modify: `src/codealmanac/cli/render/setup.py`
- Test: `tests/test_cli.py`

Steps:

1. Replace the current ASCII banner with the block-letter logo from `/Users/rohan/Desktop/Projects/openalmanac/mcp/src/setup/tui.ts`.
2. Keep product copy CodeAlmanac/local-first.
3. Keep the `codealmanac` badge.

### Task 2: Restore Archive Setup Rhythm

**Files:**
- Modify: `src/codealmanac/cli/render/setup.py`
- Test: `tests/test_cli.py`

Steps:

1. Render setup steps as `◇` done lines and `○` skipped lines.
2. Show details below each step using the archive vertical bar.
3. Replace the Rich setup panel with the archive-style next-steps box.
4. Leave uninstall panels alone.

### Task 3: Verify

Run:

```bash
uv run pytest tests/test_cli.py tests/test_setup_service.py tests/test_automation_service.py
uv run ruff check .
uv run pytest
git diff --check
```
