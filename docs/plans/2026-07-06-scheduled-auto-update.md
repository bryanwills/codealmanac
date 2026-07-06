# Scheduled Auto-Update Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Keep CodeAlmanac updated automatically through a separate scheduled update task.

**Architecture:** `services/automation` owns scheduler job definitions for `sync`, `garden`, and `update`. `services/updates` owns package-update execution, scheduled-run policy, global update locking, active lifecycle-run detection, output logging, and smoke checks. Integrations stay thin: the package runner only runs commands, and launchd only installs scheduled jobs.

**Tech Stack:** Pydantic request/result models, launchd scheduled jobs, local filesystem lock/log files under `~/.codealmanac/`, existing uv/pip package update runner, pytest and ruff gates.

---

### Task 1: Add The Update Automation Task

**Files:**
- Modify: `src/codealmanac/services/automation/models.py`
- Modify: `src/codealmanac/services/automation/defaults.py`
- Modify: `src/codealmanac/services/automation/definitions.py`
- Modify: `src/codealmanac/services/automation/jobs.py`
- Modify: `src/codealmanac/services/automation/selection.py`
- Test: `tests/test_automation_service.py`
- Test: `tests/test_cli.py`

**Steps:**

1. Add `AutomationTask.UPDATE = "update"`.
2. Add `DEFAULT_UPDATE_INTERVAL = timedelta(days=1)` and `UPDATE_LABEL = "com.codealmanac.update"`.
3. Add an update task definition with no working directory and `update.out.log` / `update.err.log`.
4. Make the scheduled command `python -m codealmanac.cli.main update --scheduled`.
5. Include update in default install/status/uninstall selections.
6. Keep `--garden-off` scoped to Garden only.

### Task 2: Install Update Automation During Setup

**Files:**
- Modify: `src/codealmanac/services/setup/planning.py`
- Modify: `src/codealmanac/services/setup/automation.py`
- Modify: `tests/test_setup_service.py`
- Modify: `tests/test_cli.py`

**Steps:**

1. Make setup recommendations include update automation by default.
2. Make `setup --yes` install sync, garden, and update automation.
3. Make uninstall remove sync, garden, and update by default.
4. Keep explicit task requests explicit: `automation install update` installs only update.

### Task 3: Add Scheduled Update Policy

**Files:**
- Modify: `src/codealmanac/services/updates/models.py`
- Modify: `src/codealmanac/services/updates/requests.py`
- Modify: `src/codealmanac/services/updates/service.py`
- Create: `src/codealmanac/services/updates/lock.py`
- Create: `src/codealmanac/services/updates/activity.py`
- Test: `tests/test_update_service.py`

**Steps:**

1. Add scheduled-mode fields to `RunUpdateRequest`.
2. Add `UpdateStatus.SKIPPED`.
3. Add an atomic file lock at `~/.codealmanac/update.lock`.
4. Treat stale update locks as removable after 30 minutes.
5. Scan `~/.codealmanac/repos/*/runs/*.json` for queued or running run records.
6. In scheduled mode, skip unsupported editable/source installs without failing the scheduled job.
7. In scheduled mode, skip when another update holds the lock or lifecycle runs are active.

### Task 4: Add Logging And Smoke Checks

**Files:**
- Modify: `src/codealmanac/services/updates/service.py`
- Modify: `src/codealmanac/services/updates/models.py`
- Modify: `src/codealmanac/integrations/updates/package.py`
- Test: `tests/test_update_service.py`

**Steps:**

1. Log scheduled update output under `~/.codealmanac/logs/`.
2. Run smoke commands after a successful scheduled package update:
   - `codealmanac --version`
   - `codealmanac doctor --json`
3. Record smoke command outputs in the scheduled update result.
4. Fix `codealmanac --version` if the current parser bug remains reproducible.

### Task 5: Add The CLI Surface

**Files:**
- Modify: `src/codealmanac/cli/parser/updates.py`
- Modify: `src/codealmanac/cli/dispatch/updates.py`
- Modify: `src/codealmanac/cli/render/updates.py`
- Test: `tests/test_cli.py`
- Test: `tests/test_public_contract.py`

**Steps:**

1. Add hidden `codealmanac update --scheduled`.
2. Make scheduled skip statuses exit `0`.
3. Keep manual unsupported update behavior as a non-zero exit.
4. Preserve public local-only command contract.

### Task 6: Documentation And Verification

**Files:**
- Modify: `README.md`
- Modify: `docs/python-port-live-agreement.md`
- Modify: `almanac/architecture/lifecycle-runs.md` or add/update an automation page if needed.
- Modify: `implementation-tickets.md` only for stale config wording if needed.

**Steps:**

1. Document that setup installs update automation by default.
2. Document logs and scheduled task names.
3. Run:

```bash
uv run pytest tests/test_automation_service.py tests/test_update_service.py tests/test_setup_service.py tests/test_cli.py tests/test_public_contract.py tests/test_architecture.py
uv run ruff check .
uv run pytest
uv run codealmanac validate
git diff --check
```
