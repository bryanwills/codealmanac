from datetime import UTC, datetime
from pathlib import Path

from pydantic import ValidationError

from codealmanac.workflows.sync.models import SyncLedger

SYNC_LEDGER_VERSION = 1


class SyncLedgerStore:
    def load(self, almanac_path: Path) -> SyncLedger:
        path = sync_ledger_path(almanac_path)
        try:
            return SyncLedger.model_validate_json(path.read_text(encoding="utf-8"))
        except (OSError, ValidationError, ValueError):
            return empty_ledger()


def sync_ledger_path(almanac_path: Path) -> Path:
    return almanac_path / "jobs" / "sync-ledger.json"


def empty_ledger() -> SyncLedger:
    return SyncLedger(
        version=SYNC_LEDGER_VERSION,
        updated_at=datetime.fromtimestamp(0, UTC),
        sessions={},
    )
