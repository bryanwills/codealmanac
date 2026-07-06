# Full Uninstall Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make `codealmanac uninstall` remove every CodeAlmanac-owned machine artifact while never deleting a repo's committed `almanac/` tree.

**Architecture:** `SetupService` owns the uninstall product verb. Concrete file removal and package-manager commands sit behind setup-owned ports and are wired in `src/codealmanac/app.py`, matching the Cosmic Python service-layer and composition-root guidance.

**Tech Stack:** Python, Pydantic request/result models, pytest, Rich CLI rendering, uv/pip package commands.

---

## Source Of Truth

- `notes.md`: uninstall has one meaning, removes binary/instructions/automation/global state, never deletes repo `almanac/`.
- `implementation-tickets.md` Ticket 11: remove global instructions, sync/Garden/update automation, `~/.codealmanac/`, supported installed tool, and partial uninstall flags.
- `MANUAL.md`: build the seam, keep product decisions in services, wire concrete adapters at the composition root.

## Code Wireframe

```python
result = app.setup.uninstall(RunUninstallRequest(yes=True))

SetupService.uninstall:
    instructions.uninstall(DEFAULT_SETUP_TARGETS)
    automation.uninstall(UninstallAutomationRequest())
    global_state.remove()
    package_uninstaller.uninstall()
```

## Task 1: Lock The Request Shape

**Files:**
- Modify: `src/codealmanac/services/setup/requests.py`
- Modify: `src/codealmanac/services/setup/service.py`
- Test: `tests/test_setup_service.py`

**Steps:**
1. Remove `automation_tasks` from `RunUninstallRequest`.
2. Make `SetupService.uninstall` call `UninstallAutomationRequest(home=request.home)` with no task list.
3. Update tests to assert uninstall always asks automation to remove sync, Garden, and update.
4. Run `uv run pytest tests/test_setup_service.py`.

## Task 2: Add Full Machine-State Removal Ports

**Files:**
- Modify: `src/codealmanac/services/setup/models.py`
- Modify: `src/codealmanac/services/setup/ports.py`
- Create: `src/codealmanac/integrations/setup/uninstall.py`
- Modify: `src/codealmanac/integrations/setup/__init__.py`
- Modify: `src/codealmanac/app.py`
- Test: `tests/test_setup_service.py`

**Steps:**
1. Add `GlobalStateRemovalResult` and `PackageUninstallResult` models.
2. Add setup-owned `GlobalStateRemover` and `PackageUninstaller` protocols.
3. Implement a filesystem remover for `~/.codealmanac/`.
4. Add fake removers in service tests.
5. Assert uninstall removes `~/.codealmanac/` and does not remove a repo `almanac/`.
6. Run `uv run pytest tests/test_setup_service.py`.

## Task 3: Add Supported Package Uninstall

**Files:**
- Modify: `src/codealmanac/integrations/setup/uninstall.py`
- Modify: `src/codealmanac/app.py`
- Test: `tests/test_setup_service.py`
- Test: `tests/test_cli.py`

**Steps:**
1. Use install metadata to choose:
   - uv tool: `uv tool uninstall codealmanac`
   - pip: `<python> -m pip uninstall -y codealmanac`
   - editable/source/unknown: skip with a clear unsupported message.
2. Run the package command only through the injected command runner.
3. Report removed, skipped, or failed in the result model.
4. Add tests for uv, pip, editable/source, and failed command behavior.
5. Run `uv run pytest tests/test_setup_service.py tests/test_cli.py`.

## Task 4: Render And Confirm Safely

**Files:**
- Modify: `src/codealmanac/cli/dispatch/setup.py`
- Modify: `src/codealmanac/cli/render/setup.py`
- Test: `tests/test_cli.py`

**Steps:**
1. Keep `--yes` as the non-interactive path.
2. When a terminal is interactive and `--yes` is absent, ask for confirmation before calling the service.
3. In non-interactive mode without `--yes`, return a non-zero exit before mutating.
4. Render global state and package uninstall results in text and JSON output.
5. Run `uv run pytest tests/test_cli.py`.

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
git add docs/plans/2026-07-06-full-uninstall.md src tests
git commit -m "feat(ticket-11): fully remove machine state"
```
