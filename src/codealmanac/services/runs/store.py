from datetime import UTC, datetime, timedelta
from pathlib import Path

from codealmanac.core.errors import ConflictError, NotFoundError
from codealmanac.engine.harnesses.models import HarnessEvent, HarnessTranscriptRef
from codealmanac.services.runs.factory import new_run_id, new_run_record
from codealmanac.services.runs.io import RunLedgerIO
from codealmanac.services.runs.locks import RunWorkerLease, acquire_worker_lock
from codealmanac.services.runs.models import (
    TERMINAL_RUN_STATUSES,
    QueuedRun,
    RunAttachSnapshot,
    RunCancelResult,
    RunEventKind,
    RunLogEvent,
    RunOperation,
    RunRecord,
    RunSpec,
    RunStatus,
)
from codealmanac.services.runs.queries import (
    list_run_records,
    next_spec_backed_queued_run,
)
from codealmanac.services.runs.transitions import RunTransitionWriter


class RunStore:
    def __init__(
        self,
        ledger: RunLedgerIO | None = None,
        transitions: RunTransitionWriter | None = None,
    ):
        self.ledger = ledger or RunLedgerIO()
        self.transitions = transitions or RunTransitionWriter(self.ledger)

    def create(
        self,
        run_dir: Path,
        log_reference_dir: Path,
        workspace_id: str,
        operation: RunOperation,
        title: str | None,
    ) -> RunRecord:
        now = datetime.now(UTC)
        run_id = new_run_id(operation, now)
        record = new_run_record(
            run_id, workspace_id, operation, title, now,
            log_reference_dir,
        )
        self.transitions.write_queued_record(run_dir, record, now)
        return record

    def queue(
        self,
        run_dir: Path,
        log_reference_dir: Path,
        workspace_id: str,
        spec: RunSpec,
        title: str | None,
    ) -> RunRecord:
        now = datetime.now(UTC)
        run_id = new_run_id(spec.operation, now)
        record = new_run_record(
            run_id, workspace_id, spec.operation, title or spec.title, now,
            log_reference_dir,
        )
        self.ledger.write_spec(run_dir, record.run_id, spec)
        try:
            self.transitions.write_queued_record(run_dir, record, now)
        except Exception:
            self.ledger.delete_spec(run_dir, record.run_id)
            raise
        return record

    def list(self, run_dir: Path, limit: int | None) -> tuple[RunRecord, ...]:
        return list_run_records(self.ledger, run_dir, limit)

    def exists(self, run_dir: Path, run_id: str) -> bool:
        return self.ledger.read_record(run_dir, run_id) is not None

    def read(self, run_dir: Path, run_id: str) -> RunRecord:
        record = self.ledger.read_record(run_dir, run_id)
        if record is None:
            raise NotFoundError("run", run_id)
        return record

    def read_spec(self, run_dir: Path, run_id: str) -> RunSpec | None:
        self.read(run_dir, run_id)
        return self.ledger.read_spec(run_dir, run_id)

    def next_queued(self, run_dir: Path) -> QueuedRun | None:
        return next_spec_backed_queued_run(self.ledger, run_dir)

    def acquire_worker_lock(
        self,
        run_dir: Path,
        owner: str,
        pid: int,
        now: datetime,
        stale_after: timedelta,
    ) -> RunWorkerLease | None:
        return acquire_worker_lock(run_dir, owner, pid, now, stale_after)

    def log(self, run_dir: Path, run_id: str) -> tuple[RunLogEvent, ...]:
        self.read(run_dir, run_id)
        return self.ledger.iter_events(run_dir, run_id)

    def attach(self, run_dir: Path, run_id: str) -> RunAttachSnapshot:
        record = self.read(run_dir, run_id)
        return RunAttachSnapshot(
            record=record,
            events=self.ledger.iter_events(run_dir, run_id),
            terminal=record.status in TERMINAL_RUN_STATUSES,
        )

    def append(
        self,
        run_dir: Path,
        run_id: str,
        kind: RunEventKind,
        message: str,
        harness_event: HarnessEvent | None = None,
    ) -> RunLogEvent:
        record = self.read(run_dir, run_id)
        now = datetime.now(UTC)
        event = self.transitions.new_event(
            run_dir,
            run_id,
            now,
            kind,
            message,
            harness_event,
        )
        updated = record.model_copy(update={"updated_at": event.timestamp})
        self.transitions.write_record_with_event(
            run_dir,
            previous=record,
            record=updated,
            event=event,
        )
        return event

    def mark_running(self, run_dir: Path, run_id: str) -> RunRecord:
        record = self.read(run_dir, run_id)
        if record.status == RunStatus.RUNNING:
            return record
        if record.status != RunStatus.QUEUED:
            raise ConflictError(
                f"run {run_id} cannot start from {record.status.value}"
            )
        now = datetime.now(UTC)
        running = record.model_copy(
            update={
                "status": RunStatus.RUNNING,
                "updated_at": now,
                "started_at": now,
            }
        )
        self.transitions.write_status_transition(
            run_dir,
            previous=record,
            record=running,
            timestamp=now,
            message=RunStatus.RUNNING.value,
        )
        return running

    def record_harness_transcript(
        self,
        run_dir: Path,
        run_id: str,
        transcript: HarnessTranscriptRef,
    ) -> RunRecord:
        record = self.read(run_dir, run_id)
        updated = record.model_copy(
            update={
                "harness_transcript": transcript,
                "updated_at": datetime.now(UTC),
            }
        )
        self.ledger.write_record(run_dir, updated)
        return updated

    def finish(
        self,
        run_dir: Path,
        run_id: str,
        status: RunStatus,
        summary: str | None,
        error: str | None,
    ) -> RunRecord:
        record = self.read(run_dir, run_id)
        if record.status == RunStatus.CANCELLED:
            return record
        now = datetime.now(UTC)
        finished = record.model_copy(
            update={
                "status": status,
                "summary": summary,
                "error": error,
                "updated_at": now,
                "finished_at": now,
            }
        )
        self.transitions.write_status_transition(
            run_dir,
            previous=record,
            record=finished,
            timestamp=now,
            message=status.value,
        )
        return finished

    def cancel(self, run_dir: Path, run_id: str) -> RunCancelResult:
        record = self.read(run_dir, run_id)
        if record.status in TERMINAL_RUN_STATUSES:
            return RunCancelResult(record=record, changed=False)
        now = datetime.now(UTC)
        cancelled = record.model_copy(
            update={
                "status": RunStatus.CANCELLED,
                "updated_at": now,
                "finished_at": now,
                "summary": record.summary,
                "error": record.error,
            }
        )
        self.transitions.write_status_transition(
            run_dir,
            previous=record,
            record=cancelled,
            timestamp=now,
            message=RunStatus.CANCELLED.value,
        )
        return RunCancelResult(record=cancelled, changed=True)
