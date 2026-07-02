# Slice 32 Hosted Run Events Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add SQL-backed hosted run events so cloud runs have the same `runs` + `run_events` spine as local CodeAlmanac.

**Architecture:** The hosted `runs` row remains the run summary/read model. A new `run_events` table records ordered lifecycle events for a run. `UpdatesStore` owns the persistence because it already owns run status transitions; services keep calling `create_run`, `mark_running`, `mark_delivered`, and `mark_failed` without learning a second event writer.

**Tech Stack:** Python 3.12, SQLModel/SQLAlchemy, Pydantic models, Supabase SQL migration, pytest, Ruff.

**Status:** Planned on 2026-07-02.

---

## Decisions

- Add the cloud `run_events` table now, but do not expose a dashboard/API route
  in this slice. Storage comes first; UI can read it later through a DTO.
- Keep events small and normalized:
  - `run_id`
  - `sequence`
  - `timestamp`
  - `kind`
  - `message`
  - optional `payload_json`
- Use the existing local event vocabulary where it applies:
  `status`, `message`, `tool`, `output`, and `error`.
- Record lifecycle status events from `UpdatesStore` transition methods:
  queued, running, delivered, and failed.
- Include transition-specific payload by reference/value only for metadata:
  `worker_call_id`, `commit_sha`, `files_changed`, `summary`, and `error`.
  Do not store source body text or model transcript contents in `run_events`.
- Do not change delivery behavior in this slice. Expected-head delivery
  hardening remains a later hosted delivery slice.

## Task 1: Add Hosted Run Event Models And Table

Files:

- Modify `backend/src/almanac/services/updates/models.py`
- Modify `backend/src/almanac/services/updates/tables.py`
- Modify `backend/src/almanac/services/updates/records.py`
- Modify `supabase/migrations/20260620000000_init.sql`

Steps:

1. Add `RunEventKind` enum with `status`, `message`, `tool`, `output`, and
   `error`.
2. Add `RunEvent` model with run id, sequence, timestamp, kind, message, and
   optional `payload_json`.
3. Add `RunEventRow` SQLModel table with primary key `(run_id, sequence)` and
   foreign key `run_id -> runs.id`.
4. Add migration SQL for `run_events` plus indexes for `(run_id, sequence)` and
   `(run_id, timestamp desc)`.
5. Add `run_event_from_row(row)`.

## Task 2: Write And List Run Events In UpdatesStore

Files:

- Modify `backend/src/almanac/services/updates/store.py`
- Add `backend/tests/test_update_run_events_contract.py`
- Modify `backend/tests/test_architecture_contract.py`

Steps:

1. Add `append_run_event(session, run_id, kind, message, payload_json=None,
   timestamp=None)`.
2. Sequence events by max existing sequence for the run plus one.
3. Add `list_run_events(session, run_id)`.
4. Call `append_run_event` from:
   - `create_run` after inserting the queued run
   - `mark_running` after updating worker call id
   - `mark_delivered` after terminal delivered update
   - `mark_failed` after terminal failed update
5. Add focused tests for event sequencing, payload persistence, and ordered
   listing. Use a minimal SQLite table setup for `run_events`; do not force the
   existing Postgres `runs.files_changed text[]` table through SQLite.
6. Add architecture checks that `run_events` exists in the migration/table
   contract and that event writing stays in `UpdatesStore`.

## Task 3: Verify Slice 32

Commands:

```bash
cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend
uv run pytest tests/test_update_run_events_contract.py tests/test_updates_contract.py tests/test_architecture_contract.py -q
uv run ruff check .
uv run ruff format --check .
cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence
python -m compileall backend/src backend/modal_app -q
git diff --check
```

Full gate:

```bash
cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend
uv run pytest -q
```

## Task 4: Update Launch Steering Docs

Files:

- Modify `docs/codealmanac-launch/worklog.md`
- Modify `docs/codealmanac-launch/progress.md`
- Modify `docs/codealmanac-launch/verification-matrix.md`
- Modify `docs/codealmanac-launch/next-agent-brief.md`

Steps:

1. Record hosted SQL-backed `run_events` as the cloud parallel to local
   run-event storage.
2. Record that the events are normalized lifecycle metadata only, not source
   transcript/model content.
3. Leave remaining risk on expected-head delivery hardening and frontend
   run-event display.
