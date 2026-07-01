import os
import shutil
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

from pydantic import ValidationError

from codealmanac.core.errors import ConflictError, NotFoundError
from codealmanac.services.harnesses.models import HarnessEvent, HarnessTranscriptRef
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
    RunWorkerLockOwner,
)


class RunWorkerLease:
    def __init__(self, lock_path: Path, owner: RunWorkerLockOwner):
        self.lock_path = lock_path
        self.owner = owner

    def release(self) -> None:
        current = read_worker_lock_owner(self.lock_path)
        if current != self.owner:
            return
        shutil.rmtree(self.lock_path, ignore_errors=True)


class RunStore:
    def create(
        self,
        almanac_path: Path,
        almanac_root: Path,
        workspace_id: str,
        operation: RunOperation,
        title: str | None,
    ) -> RunRecord:
        now = datetime.now(UTC)
        record = new_run_record(almanac_root, workspace_id, operation, title, now)
        write_queued_record(almanac_path, record, now)
        return record

    def queue(
        self,
        almanac_path: Path,
        almanac_root: Path,
        workspace_id: str,
        spec: RunSpec,
        title: str | None,
    ) -> RunRecord:
        now = datetime.now(UTC)
        record = new_run_record(
            almanac_root,
            workspace_id,
            spec.operation,
            title or spec.title,
            now,
        )
        write_spec(almanac_path, record.run_id, spec)
        write_queued_record(almanac_path, record, now)
        return record

    def list(self, almanac_path: Path, limit: int | None) -> tuple[RunRecord, ...]:
        records = sorted(
            iter_records(almanac_path),
            key=lambda record: (record.created_at, record.run_id),
            reverse=True,
        )
        if limit is not None:
            return tuple(records[:limit])
        return tuple(records)

    def read(self, almanac_path: Path, run_id: str) -> RunRecord:
        record = read_record(almanac_path, run_id)
        if record is None:
            raise NotFoundError("run", run_id)
        return record

    def read_spec(self, almanac_path: Path, run_id: str) -> RunSpec | None:
        self.read(almanac_path, run_id)
        return read_spec(almanac_path, run_id)

    def next_queued(self, almanac_path: Path) -> QueuedRun | None:
        records = sorted(
            iter_records(almanac_path),
            key=lambda record: (record.created_at, record.run_id),
        )
        for record in records:
            if record.status != RunStatus.QUEUED:
                continue
            if not run_spec_path(almanac_path, record.run_id).is_file():
                continue
            return QueuedRun(
                record=record,
                spec=read_spec(almanac_path, record.run_id),
            )
        return None

    def acquire_worker_lock(
        self,
        almanac_path: Path,
        owner: str,
        pid: int,
        now: datetime,
        stale_after: timedelta,
    ) -> RunWorkerLease | None:
        path = worker_lock_path(almanac_path)
        lock_owner = RunWorkerLockOwner(owner=owner, pid=pid, acquired_at=now)
        path.parent.mkdir(parents=True, exist_ok=True)
        for _ in range(2):
            try:
                path.mkdir()
            except FileExistsError:
                current = read_worker_lock_owner(path)
                if current is not None and not worker_lock_is_stale(
                    current,
                    now,
                    stale_after,
                ):
                    return None
                shutil.rmtree(path, ignore_errors=True)
                continue
            write_worker_lock_owner(path, lock_owner)
            return RunWorkerLease(path, lock_owner)
        return None

    def log(self, almanac_path: Path, run_id: str) -> tuple[RunLogEvent, ...]:
        self.read(almanac_path, run_id)
        return tuple(iter_events(almanac_path, run_id))

    def attach(self, almanac_path: Path, run_id: str) -> RunAttachSnapshot:
        record = self.read(almanac_path, run_id)
        return RunAttachSnapshot(
            record=record,
            events=tuple(iter_events(almanac_path, run_id)),
            terminal=record.status in TERMINAL_RUN_STATUSES,
        )

    def append(
        self,
        almanac_path: Path,
        run_id: str,
        kind: RunEventKind,
        message: str,
        harness_event: HarnessEvent | None = None,
    ) -> RunLogEvent:
        record = self.read(almanac_path, run_id)
        event = RunLogEvent(
            run_id=run_id,
            sequence=next_sequence(almanac_path, run_id),
            timestamp=datetime.now(UTC),
            kind=kind,
            message=message,
            harness_event=harness_event,
        )
        append_event(almanac_path, event)
        write_record(
            almanac_path,
            record.model_copy(update={"updated_at": event.timestamp}),
        )
        return event

    def mark_running(self, almanac_path: Path, run_id: str) -> RunRecord:
        record = self.read(almanac_path, run_id)
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
        write_record(almanac_path, running)
        append_event(
            almanac_path,
            RunLogEvent(
                run_id=run_id,
                sequence=next_sequence(almanac_path, run_id),
                timestamp=now,
                kind=RunEventKind.STATUS,
                message=RunStatus.RUNNING.value,
            ),
        )
        return running

    def record_harness_transcript(
        self,
        almanac_path: Path,
        run_id: str,
        transcript: HarnessTranscriptRef,
    ) -> RunRecord:
        record = self.read(almanac_path, run_id)
        updated = record.model_copy(
            update={
                "harness_transcript": transcript,
                "updated_at": datetime.now(UTC),
            }
        )
        write_record(almanac_path, updated)
        return updated

    def finish(
        self,
        almanac_path: Path,
        run_id: str,
        status: RunStatus,
        summary: str | None,
        error: str | None,
    ) -> RunRecord:
        record = self.read(almanac_path, run_id)
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
        write_record(almanac_path, finished)
        append_event(
            almanac_path,
            RunLogEvent(
                run_id=run_id,
                sequence=next_sequence(almanac_path, run_id),
                timestamp=now,
                kind=RunEventKind.STATUS,
                message=status.value,
            ),
        )
        return finished

    def cancel(self, almanac_path: Path, run_id: str) -> RunCancelResult:
        record = self.read(almanac_path, run_id)
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
        write_record(almanac_path, cancelled)
        append_event(
            almanac_path,
            RunLogEvent(
                run_id=run_id,
                sequence=next_sequence(almanac_path, run_id),
                timestamp=now,
                kind=RunEventKind.STATUS,
                message=RunStatus.CANCELLED.value,
            ),
        )
        return RunCancelResult(record=cancelled, changed=True)


def new_run_id(operation: RunOperation, now: datetime) -> str:
    stamp = now.strftime("%Y%m%d%H%M%S")
    return f"{operation.value}-{stamp}-{uuid4().hex[:8]}"


def new_run_record(
    almanac_root: Path,
    workspace_id: str,
    operation: RunOperation,
    title: str | None,
    now: datetime,
) -> RunRecord:
    run_id = new_run_id(operation, now)
    return RunRecord(
        run_id=run_id,
        workspace_id=workspace_id,
        operation=operation,
        status=RunStatus.QUEUED,
        title=title,
        created_at=now,
        updated_at=now,
        log_path=run_log_reference_path(almanac_root, run_id),
    )


def write_queued_record(almanac_path: Path, record: RunRecord, now: datetime) -> None:
    write_record(almanac_path, record)
    append_event(
        almanac_path,
        RunLogEvent(
            run_id=record.run_id,
            sequence=1,
            timestamp=now,
            kind=RunEventKind.STATUS,
            message=f"queued {record.operation.value}",
        ),
    )


def runs_dir(almanac_path: Path) -> Path:
    return almanac_path / "jobs"


def run_record_path(almanac_path: Path, run_id: str) -> Path:
    return runs_dir(almanac_path) / f"{run_id}.json"


def run_spec_path(almanac_path: Path, run_id: str) -> Path:
    return runs_dir(almanac_path) / f"{run_id}.spec.json"


def run_log_path(almanac_path: Path, run_id: str) -> Path:
    return runs_dir(almanac_path) / f"{run_id}.jsonl"


def run_log_reference_path(almanac_root: Path, run_id: str) -> Path:
    return almanac_root / "jobs" / f"{run_id}.jsonl"


def write_record(almanac_path: Path, record: RunRecord) -> None:
    path = run_record_path(almanac_path, record.run_id)
    write_json_atomically(path, record.model_dump_json(indent=2))


def write_spec(almanac_path: Path, run_id: str, spec: RunSpec) -> None:
    path = run_spec_path(almanac_path, run_id)
    write_json_atomically(path, spec.model_dump_json(indent=2))


def write_json_atomically(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
    try:
        temporary.write_text(payload, encoding="utf-8")
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()


def read_record(almanac_path: Path, run_id: str) -> RunRecord | None:
    path = run_record_path(almanac_path, run_id)
    if not path.is_file():
        return None
    try:
        return RunRecord.model_validate_json(path.read_text(encoding="utf-8"))
    except (OSError, ValidationError, ValueError):
        return None


def read_spec(almanac_path: Path, run_id: str) -> RunSpec | None:
    path = run_spec_path(almanac_path, run_id)
    if not path.is_file():
        return None
    try:
        return RunSpec.model_validate_json(path.read_text(encoding="utf-8"))
    except (OSError, ValidationError, ValueError):
        return None


def iter_records(almanac_path: Path) -> tuple[RunRecord, ...]:
    directory = runs_dir(almanac_path)
    if not directory.is_dir():
        return ()
    records: list[RunRecord] = []
    for path in sorted(directory.glob("*.json")):
        if path.name.endswith(".spec.json"):
            continue
        run_id = path.stem
        record = read_record(almanac_path, run_id)
        if record is not None:
            records.append(record)
    return tuple(records)


def append_event(almanac_path: Path, event: RunLogEvent) -> None:
    path = run_log_path(almanac_path, event.run_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(event.model_dump_json(exclude_none=True))
        file.write("\n")


def iter_events(almanac_path: Path, run_id: str) -> tuple[RunLogEvent, ...]:
    path = run_log_path(almanac_path, run_id)
    if not path.is_file():
        return ()
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return ()
    events: list[RunLogEvent] = []
    for line in lines:
        if not line.strip():
            continue
        try:
            events.append(RunLogEvent.model_validate_json(line))
        except (ValidationError, ValueError):
            continue
    return tuple(events)


def next_sequence(almanac_path: Path, run_id: str) -> int:
    return len(iter_events(almanac_path, run_id)) + 1


def worker_lock_path(almanac_path: Path) -> Path:
    return runs_dir(almanac_path) / "worker.lock"


def worker_lock_owner_path(lock_path: Path) -> Path:
    return lock_path / "owner.json"


def write_worker_lock_owner(
    lock_path: Path,
    owner: RunWorkerLockOwner,
) -> None:
    worker_lock_owner_path(lock_path).write_text(
        owner.model_dump_json(indent=2),
        encoding="utf-8",
    )


def read_worker_lock_owner(lock_path: Path) -> RunWorkerLockOwner | None:
    path = worker_lock_owner_path(lock_path)
    if not path.is_file():
        return None
    try:
        return RunWorkerLockOwner.model_validate_json(path.read_text(encoding="utf-8"))
    except (OSError, ValidationError, ValueError):
        return None


def worker_lock_is_stale(
    owner: RunWorkerLockOwner,
    now: datetime,
    stale_after: timedelta,
) -> bool:
    if now - owner.acquired_at >= stale_after:
        return True
    return not process_is_alive(owner.pid)


def process_is_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True
