from pathlib import Path
from uuid import uuid4

from pydantic import ValidationError

from codealmanac.services.runs.models import RunLogEvent, RunRecord, RunSpec
from codealmanac.services.runs.paths import (
    run_log_path,
    run_record_path,
    run_spec_path,
    runs_dir,
)


class RunLedgerIO:
    def write_record(self, runtime_path: Path, record: RunRecord) -> None:
        path = run_record_path(runtime_path, record.run_id)
        write_json_atomically(path, record.model_dump_json(indent=2))

    def delete_record(self, runtime_path: Path, run_id: str) -> None:
        path = run_record_path(runtime_path, run_id)
        path.unlink(missing_ok=True)

    def write_spec(self, runtime_path: Path, run_id: str, spec: RunSpec) -> None:
        path = run_spec_path(runtime_path, run_id)
        write_json_atomically(path, spec.model_dump_json(indent=2))

    def delete_spec(self, runtime_path: Path, run_id: str) -> None:
        path = run_spec_path(runtime_path, run_id)
        path.unlink(missing_ok=True)

    def read_record(self, runtime_path: Path, run_id: str) -> RunRecord | None:
        path = run_record_path(runtime_path, run_id)
        if not path.is_file():
            return None
        try:
            return RunRecord.model_validate_json(path.read_text(encoding="utf-8"))
        except (OSError, ValidationError, ValueError):
            return None

    def read_spec(self, runtime_path: Path, run_id: str) -> RunSpec | None:
        path = run_spec_path(runtime_path, run_id)
        if not path.is_file():
            return None
        try:
            return RunSpec.model_validate_json(path.read_text(encoding="utf-8"))
        except (OSError, ValidationError, ValueError):
            return None

    def iter_records(self, runtime_path: Path) -> tuple[RunRecord, ...]:
        directory = runs_dir(runtime_path)
        if not directory.is_dir():
            return ()
        records: list[RunRecord] = []
        for path in sorted(directory.glob("*.json")):
            if path.name.endswith(".spec.json"):
                continue
            try:
                record = self.read_record(runtime_path, path.stem)
            except ValidationError:
                continue
            if record is not None:
                records.append(record)
        return tuple(records)

    def append_event(self, runtime_path: Path, event: RunLogEvent) -> None:
        path = run_log_path(runtime_path, event.run_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as file:
            file.write(event.model_dump_json(exclude_none=True))
            file.write("\n")

    def iter_events(self, runtime_path: Path, run_id: str) -> tuple[RunLogEvent, ...]:
        path = run_log_path(runtime_path, run_id)
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

    def next_sequence(self, runtime_path: Path, run_id: str) -> int:
        return len(self.iter_events(runtime_path, run_id)) + 1


def write_json_atomically(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
    try:
        temporary.write_text(payload, encoding="utf-8")
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()
