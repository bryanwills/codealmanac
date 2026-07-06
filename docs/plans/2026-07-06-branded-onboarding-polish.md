# Branded Onboarding Polish Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make Ticket 12's setup screen show the archive-inspired color, permission, feel, and language clearly.

**Architecture:** Keep `SetupService` as the machine-level setup verb. Keep interactivity in `src/codealmanac/cli/dispatch/setup.py` and terminal presentation in `src/codealmanac/cli/render/setup.py`.

**Tech Stack:** Python, Rich, pytest.

---

### Task 1: Make Permission Explicit

**Files:**
- Modify: `src/codealmanac/cli/dispatch/setup.py`
- Test: `tests/test_cli.py`

Steps:

1. Change the interactive auto-update prompt to mention permission and the local scheduled updater.
2. Keep `--yes`, `--json`, non-TTY, and `--no-auto-update` behavior unchanged.
3. Update the prompt assertion.

### Task 2: Polish Setup Output

**Files:**
- Modify: `src/codealmanac/cli/render/setup.py`
- Modify: `src/codealmanac/services/setup/planning.py`
- Test: `tests/test_cli.py`

Steps:

1. Add named Rich styles for the setup palette.
2. Make the subtitle and badge say local-first CodeAlmanac.
3. Show update automation as permission granted or not granted.
4. Make auto-commit copy say the permission lives in agent instructions.
5. Make next-step labels distinguish machine setup from repo wiki setup.

### Task 3: Verify

Run:

```bash
uv run pytest tests/test_cli.py tests/test_setup_service.py tests/test_automation_service.py
uv run ruff check .
uv run pytest
git diff --check
```
