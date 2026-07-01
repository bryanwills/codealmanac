from datetime import datetime
from pathlib import Path

from codealmanac.services.harnesses.models import HarnessEvent
from codealmanac.services.runs.io import RunLedgerIO
from codealmanac.services.runs.models import (
    RunEventKind,
    RunLogEvent,
    RunRecord,
)


class RunTransitionWriter:
    def __init__(self, ledger: RunLedgerIO):
        self.ledger = ledger

    def write_queued_record(
        self,
        almanac_path: Path,
        record: RunRecord,
        timestamp: datetime,
    ) -> None:
        event = self.new_event(
            almanac_path,
            record.run_id,
            timestamp,
            RunEventKind.STATUS,
            f"queued {record.operation.value}",
        )
        self.write_record_with_event(
            almanac_path,
            previous=None,
            record=record,
            event=event,
        )

    def write_status_transition(
        self,
        almanac_path: Path,
        previous: RunRecord,
        record: RunRecord,
        timestamp: datetime,
        message: str,
    ) -> None:
        event = self.new_event(
            almanac_path,
            record.run_id,
            timestamp,
            RunEventKind.STATUS,
            message,
        )
        self.write_record_with_event(
            almanac_path,
            previous=previous,
            record=record,
            event=event,
        )

    def write_record_with_event(
        self,
        almanac_path: Path,
        previous: RunRecord | None,
        record: RunRecord,
        event: RunLogEvent,
    ) -> None:
        self.ledger.write_record(almanac_path, record)
        try:
            self.ledger.append_event(almanac_path, event)
        except Exception:
            self.restore_record(almanac_path, previous, record.run_id)
            raise

    def new_event(
        self,
        almanac_path: Path,
        run_id: str,
        timestamp: datetime,
        kind: RunEventKind,
        message: str,
        harness_event: HarnessEvent | None = None,
    ) -> RunLogEvent:
        return RunLogEvent(
            run_id=run_id,
            sequence=self.ledger.next_sequence(almanac_path, run_id),
            timestamp=timestamp,
            kind=kind,
            message=message,
            harness_event=harness_event,
        )

    def restore_record(
        self,
        almanac_path: Path,
        previous: RunRecord | None,
        run_id: str,
    ) -> None:
        if previous is None:
            self.ledger.delete_record(almanac_path, run_id)
            return
        self.ledger.write_record(almanac_path, previous)
