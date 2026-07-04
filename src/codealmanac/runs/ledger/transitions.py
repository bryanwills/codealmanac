from datetime import datetime
from pathlib import Path

from codealmanac.engine.harnesses.models import HarnessEvent
from codealmanac.runs.ledger.io import RunLedgerIO
from codealmanac.runs.ledger.models import (
    RunEventKind,
    RunLogEvent,
    RunRecord,
)


class RunTransitionWriter:
    def __init__(self, ledger: RunLedgerIO):
        self.ledger = ledger

    def write_queued_record(
        self,
        run_dir: Path,
        record: RunRecord,
        timestamp: datetime,
    ) -> None:
        event = self.new_event(
            run_dir,
            record.run_id,
            timestamp,
            RunEventKind.STATUS,
            f"queued {record.kind.value}",
        )
        self.write_record_with_event(
            run_dir,
            previous=None,
            record=record,
            event=event,
        )

    def write_status_transition(
        self,
        run_dir: Path,
        previous: RunRecord,
        record: RunRecord,
        timestamp: datetime,
        message: str,
    ) -> None:
        event = self.new_event(
            run_dir,
            record.run_id,
            timestamp,
            RunEventKind.STATUS,
            message,
        )
        self.write_record_with_event(
            run_dir,
            previous=previous,
            record=record,
            event=event,
        )

    def write_record_with_event(
        self,
        run_dir: Path,
        previous: RunRecord | None,
        record: RunRecord,
        event: RunLogEvent,
    ) -> None:
        self.ledger.write_record(run_dir, record)
        try:
            self.ledger.append_event(run_dir, event)
        except Exception:
            self.restore_record(run_dir, previous, record.run_id)
            raise

    def new_event(
        self,
        run_dir: Path,
        run_id: str,
        timestamp: datetime,
        kind: RunEventKind,
        message: str,
        harness_event: HarnessEvent | None = None,
    ) -> RunLogEvent:
        return RunLogEvent(
            run_id=run_id,
            sequence=self.ledger.next_sequence(run_dir, run_id),
            timestamp=timestamp,
            kind=kind,
            message=message,
            harness_event=harness_event,
        )

    def restore_record(
        self,
        run_dir: Path,
        previous: RunRecord | None,
        run_id: str,
    ) -> None:
        if previous is None:
            self.ledger.delete_record(run_dir, run_id)
            return
        self.ledger.write_record(run_dir, previous)
