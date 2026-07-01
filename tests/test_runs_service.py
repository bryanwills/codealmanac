import os
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from pydantic import ValidationError

from codealmanac.app import create_app
from codealmanac.core.errors import ConflictError
from codealmanac.core.models import AppConfig
from codealmanac.services.harnesses.models import (
    HarnessEvent,
    HarnessEventKind,
    HarnessKind,
    HarnessTranscriptRef,
)
from codealmanac.services.runs.models import (
    RunEventKind,
    RunOperation,
    RunSpec,
    RunStatus,
)
from codealmanac.services.runs.requests import (
    AcquireRunWorkerLockRequest,
    AttachRunRequest,
    CancelRunRequest,
    FinishRunRequest,
    ListRunsRequest,
    MarkRunRunningRequest,
    NextQueuedRunRequest,
    QueueRunRequest,
    ReadRunLogRequest,
    ReadRunSpecRequest,
    RecordRunEventRequest,
    RecordRunHarnessTranscriptRequest,
    ShowRunRequest,
    StartRunRequest,
)
from codealmanac.services.workspaces.requests import InitializeWorkspaceRequest


def test_runs_service_records_job_and_events(
    tmp_path: Path,
    isolated_home: Path,
):
    repo = tmp_path / "repo"
    repo.mkdir()
    app = create_app(
        AppConfig(registry_path=isolated_home / ".codealmanac/registry.json")
    )
    app.workflows.build.initialize(InitializeWorkspaceRequest(path=repo))

    record = app.runs.start(
        StartRunRequest(
            cwd=repo,
            operation=RunOperation.INGEST,
            title="Digest design note",
        )
    )
    running = app.runs.mark_running(
        MarkRunRunningRequest(cwd=repo, run_id=record.run_id)
    )
    event = app.runs.record_event(
        RecordRunEventRequest(
            cwd=repo,
            run_id=record.run_id,
            kind=RunEventKind.MESSAGE,
            message="read design note",
        )
    )
    harness_log = app.runs.record_event(
        RecordRunEventRequest(
            cwd=repo,
            run_id=record.run_id,
            kind=RunEventKind.TOOL,
            message="codex provider session provider-thread-1",
            harness_event=HarnessEvent(
                kind=HarnessEventKind.PROVIDER_SESSION,
                message="codex provider session provider-thread-1",
                provider_session_id="provider-thread-1",
            ),
        )
    )
    transcript = HarnessTranscriptRef(
        kind=HarnessKind.CODEX,
        session_id="codex-session-1",
        transcript_path=Path("/tmp/codex-session.jsonl"),
    )
    attached = app.runs.record_harness_transcript(
        RecordRunHarnessTranscriptRequest(
            cwd=repo,
            run_id=record.run_id,
            transcript=transcript,
        )
    )
    finished = app.runs.finish(
        FinishRunRequest(
            cwd=repo,
            run_id=record.run_id,
            status=RunStatus.DONE,
            summary="updated wiki",
        )
    )
    listed = app.runs.list(ListRunsRequest(cwd=repo))
    shown = app.runs.show(ShowRunRequest(cwd=repo, run_id=record.run_id))
    log = app.runs.log(ReadRunLogRequest(cwd=repo, run_id=record.run_id))

    assert record.status == RunStatus.QUEUED
    assert running.status == RunStatus.RUNNING
    assert running.started_at is not None
    assert event.sequence == 3
    assert event.harness_event is None
    assert harness_log.sequence == 4
    assert harness_log.harness_event is not None
    assert harness_log.harness_event.provider_session_id == "provider-thread-1"
    assert attached.harness_transcript == transcript
    assert finished.status == RunStatus.DONE
    assert finished.started_at == running.started_at
    assert finished.harness_transcript == transcript
    assert finished.summary == "updated wiki"
    assert [run.run_id for run in listed] == [record.run_id]
    assert shown.status == RunStatus.DONE
    assert shown.log_path == Path("almanac/jobs") / f"{record.run_id}.jsonl"
    assert tuple(entry.kind for entry in log) == (
        RunEventKind.STATUS,
        RunEventKind.STATUS,
        RunEventKind.MESSAGE,
        RunEventKind.TOOL,
        RunEventKind.STATUS,
    )
    assert log[2].harness_event is None
    assert log[3].harness_event is not None
    assert log[3].harness_event.provider_session_id == "provider-thread-1"
    assert (repo / "almanac/jobs" / f"{record.run_id}.json").is_file()
    assert (repo / "almanac/jobs" / f"{record.run_id}.jsonl").is_file()


def test_runs_service_targets_registered_wiki(
    tmp_path: Path,
    isolated_home: Path,
):
    first = tmp_path / "first"
    second = tmp_path / "second"
    first.mkdir()
    second.mkdir()
    app = create_app(
        AppConfig(registry_path=isolated_home / ".codealmanac/registry.json")
    )
    app.workflows.build.initialize(InitializeWorkspaceRequest(path=first, name="first"))
    app.workflows.build.initialize(
        InitializeWorkspaceRequest(path=second, name="second")
    )

    record = app.runs.start(
        StartRunRequest(cwd=second, wiki="first", operation=RunOperation.GARDEN)
    )

    assert (first / "almanac/jobs" / f"{record.run_id}.json").is_file()
    assert app.runs.list(ListRunsRequest(cwd=second, wiki="first"))[0].run_id == (
        record.run_id
    )


def test_runs_service_refuses_running_transition_after_terminal_status(
    tmp_path: Path,
    isolated_home: Path,
):
    repo = tmp_path / "repo"
    repo.mkdir()
    app = create_app(
        AppConfig(registry_path=isolated_home / ".codealmanac/registry.json")
    )
    app.workflows.build.initialize(InitializeWorkspaceRequest(path=repo))
    record = app.runs.start(StartRunRequest(cwd=repo, operation=RunOperation.INGEST))
    app.runs.finish(
        FinishRunRequest(
            cwd=repo,
            run_id=record.run_id,
            status=RunStatus.FAILED,
            error="failed before running",
        )
    )

    with pytest.raises(ConflictError):
        app.runs.mark_running(MarkRunRunningRequest(cwd=repo, run_id=record.run_id))


def test_runs_service_cancels_queued_run_and_attaches_log(
    tmp_path: Path,
    isolated_home: Path,
):
    repo = tmp_path / "repo"
    repo.mkdir()
    app = create_app(
        AppConfig(registry_path=isolated_home / ".codealmanac/registry.json")
    )
    app.workflows.build.initialize(InitializeWorkspaceRequest(path=repo))
    record = app.runs.start(StartRunRequest(cwd=repo, operation=RunOperation.GARDEN))

    result = app.runs.cancel(CancelRunRequest(cwd=repo, run_id=record.run_id))
    snapshot = app.runs.attach(AttachRunRequest(cwd=repo, run_id=record.run_id))

    assert result.changed is True
    assert result.record.status == RunStatus.CANCELLED
    assert result.record.started_at is None
    assert result.record.finished_at is not None
    assert snapshot.record.status == RunStatus.CANCELLED
    assert snapshot.terminal is True
    assert tuple(entry.message for entry in snapshot.events) == (
        "queued garden",
        "cancelled",
    )


def test_runs_service_cancel_is_idempotent_for_terminal_run(
    tmp_path: Path,
    isolated_home: Path,
):
    repo = tmp_path / "repo"
    repo.mkdir()
    app = create_app(
        AppConfig(registry_path=isolated_home / ".codealmanac/registry.json")
    )
    app.workflows.build.initialize(InitializeWorkspaceRequest(path=repo))
    record = app.runs.start(StartRunRequest(cwd=repo, operation=RunOperation.GARDEN))
    app.runs.finish(
        FinishRunRequest(
            cwd=repo,
            run_id=record.run_id,
            status=RunStatus.FAILED,
            error="already failed",
        )
    )

    result = app.runs.cancel(CancelRunRequest(cwd=repo, run_id=record.run_id))
    log = app.runs.log(ReadRunLogRequest(cwd=repo, run_id=record.run_id))

    assert result.changed is False
    assert result.record.status == RunStatus.FAILED
    assert tuple(entry.message for entry in log) == (
        "queued garden",
        "failed",
    )


def test_runs_service_finish_preserves_cancelled_run(
    tmp_path: Path,
    isolated_home: Path,
):
    repo = tmp_path / "repo"
    repo.mkdir()
    app = create_app(
        AppConfig(registry_path=isolated_home / ".codealmanac/registry.json")
    )
    app.workflows.build.initialize(InitializeWorkspaceRequest(path=repo))
    record = app.runs.start(StartRunRequest(cwd=repo, operation=RunOperation.GARDEN))
    app.runs.mark_running(MarkRunRunningRequest(cwd=repo, run_id=record.run_id))
    cancelled = app.runs.cancel(CancelRunRequest(cwd=repo, run_id=record.run_id))

    finished = app.runs.finish(
        FinishRunRequest(
            cwd=repo,
            run_id=record.run_id,
            status=RunStatus.DONE,
            summary="should not win",
        )
    )
    log = app.runs.log(ReadRunLogRequest(cwd=repo, run_id=record.run_id))

    assert cancelled.changed is True
    assert finished.status == RunStatus.CANCELLED
    assert finished.summary is None
    assert tuple(entry.message for entry in log) == (
        "queued garden",
        "running",
        "cancelled",
    )


def test_runs_service_persists_queue_specs_and_selects_oldest_background_run(
    tmp_path: Path,
    isolated_home: Path,
):
    repo = tmp_path / "repo"
    repo.mkdir()
    app = create_app(
        AppConfig(registry_path=isolated_home / ".codealmanac/registry.json")
    )
    app.workflows.build.initialize(InitializeWorkspaceRequest(path=repo))
    foreground = app.runs.start(
        StartRunRequest(cwd=repo, operation=RunOperation.INGEST)
    )
    first = app.runs.queue(
        QueueRunRequest(
            cwd=repo,
            title="Ingest first note",
            spec=RunSpec(
                operation=RunOperation.INGEST,
                cwd=repo,
                harness=HarnessKind.CODEX,
                inputs=("first.md",),
            ),
        )
    )
    second = app.runs.queue(
        QueueRunRequest(
            cwd=repo,
            title="Garden later",
            spec=RunSpec(
                operation=RunOperation.GARDEN,
                cwd=repo,
                harness=HarnessKind.CODEX,
            ),
        )
    )

    spec = app.runs.read_spec(ReadRunSpecRequest(cwd=repo, run_id=first.run_id))
    queued = app.runs.next_queued(NextQueuedRunRequest(cwd=repo))
    listed = app.runs.list(ListRunsRequest(cwd=repo))

    assert foreground.status == RunStatus.QUEUED
    assert spec is not None
    assert spec.inputs == ("first.md",)
    assert queued is not None
    assert queued.record.run_id == first.run_id
    assert queued.spec == spec
    assert {record.run_id for record in listed} == {
        foreground.run_id,
        first.run_id,
        second.run_id,
    }
    assert (repo / "almanac/jobs" / f"{first.run_id}.spec.json").is_file()


def test_runs_service_worker_lock_is_exclusive_and_recovers_stale_owner(
    tmp_path: Path,
    isolated_home: Path,
):
    repo = tmp_path / "repo"
    repo.mkdir()
    app = create_app(
        AppConfig(registry_path=isolated_home / ".codealmanac/registry.json")
    )
    app.workflows.build.initialize(InitializeWorkspaceRequest(path=repo))
    now = datetime(2026, 7, 1, 12, 0, tzinfo=UTC)

    first = app.runs.acquire_worker_lock(
        AcquireRunWorkerLockRequest(
            cwd=repo,
            owner="first-worker",
            pid=os.getpid(),
            now=now,
            stale_after=timedelta(minutes=10),
        )
    )
    blocked = app.runs.acquire_worker_lock(
        AcquireRunWorkerLockRequest(
            cwd=repo,
            owner="second-worker",
            pid=os.getpid(),
            now=now + timedelta(minutes=1),
            stale_after=timedelta(minutes=10),
        )
    )
    recovered = app.runs.acquire_worker_lock(
        AcquireRunWorkerLockRequest(
            cwd=repo,
            owner="second-worker",
            pid=os.getpid(),
            now=now + timedelta(minutes=11),
            stale_after=timedelta(minutes=10),
        )
    )

    assert first is not None
    assert blocked is None
    assert recovered is not None
    assert recovered.owner.owner == "second-worker"

    first.release()
    assert (repo / "almanac/jobs/worker.lock").is_dir()
    recovered.release()
    assert not (repo / "almanac/jobs/worker.lock").exists()


def test_finish_run_request_requires_terminal_status(tmp_path: Path):
    with pytest.raises(ValidationError):
        FinishRunRequest(
            cwd=tmp_path,
            run_id="run-1",
            status=RunStatus.RUNNING,
        )
