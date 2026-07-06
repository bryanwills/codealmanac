# Generous Lifecycle Mutation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Allow explicit lifecycle runs to start when `almanac/` already has user edits, while still rejecting agent-created changes outside `almanac/`.

**Architecture:** `LifecycleMutationPolicy` remains the product boundary for mutation safety. Preflight records the before snapshot and verifies Git tracking is available; validation compares the before and after snapshots to find actual changes made during the run. `PageRunWorkflow` keeps the existing order: record harness output/events, validate mutation safety, validate harness status, refresh index, validate wiki, finish run.

**Tech Stack:** Python services/workflows, Pydantic workflow models, Git-backed workspace snapshots, pytest lifecycle workflow tests.

---

### Task 1: Make Preflight Snapshot-Only

**Files:**
- Modify: `src/codealmanac/workflows/lifecycle_mutation.py`
- Modify: `src/codealmanac/workflows/page_run/service.py`
- Test: `tests/test_ingest_workflow.py`

**Steps:**

1. Change `LifecycleMutationPolicy.preflight(...)` so it no longer rejects dirty paths under `almanac/`.
2. Keep `validate_snapshot_available(...)`; lifecycle runs still require readable Git status.
3. Keep `almanac_prefix` in `LifecycleMutationPreflight`; validation still needs the allowed mutation boundary.
4. Change the preflight run event from "verified clean almanac preflight" to "captured almanac mutation preflight".
5. Update any test assertion that depended on the old event text.

### Task 2: Preserve Before/After Safety

**Files:**
- Modify: `src/codealmanac/workflows/lifecycle_mutation.py`
- Test: `tests/test_ingest_workflow.py`
- Test: `tests/test_garden_workflow.py`

**Steps:**

1. Keep `changed_paths(before, after)` as the source of truth.
2. Keep rejecting any path whose identity changed during the run and is not under `almanac/`.
3. Keep validating harness-reported changed files are inside `almanac/`; this catches providers that report an unsafe change even if Git status misses it.
4. Keep returning only changed `almanac/` paths in `LifecycleMutationReport.changed_files`.

### Task 3: Add Product Tests

**Files:**
- Modify: `tests/test_ingest_workflow.py`
- Modify: `tests/test_garden_workflow.py`

**Steps:**

1. Replace the dirty-almanac rejection test with a test that pre-existing dirty `almanac/` edits are allowed.
2. Assert the safety report includes both the pre-existing dirty page when the agent changes it and the new/changed wiki page.
3. Keep the existing tests that pre-existing dirty source files are allowed when unchanged.
4. Keep the existing tests that agent-created or agent-modified source files fail.
5. Add or update a garden test so both lifecycle operations share the same policy.

### Task 4: Verify

Run:

```bash
uv run pytest tests/test_ingest_workflow.py tests/test_garden_workflow.py
uv run pytest tests/test_run_queue_workflow.py tests/test_validate.py
uv run ruff check .
uv run pytest
uv run codealmanac validate
```
