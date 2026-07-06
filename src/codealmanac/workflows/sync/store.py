from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from pydantic import ValidationError

from codealmanac.workflows.sync.models import SyncLedger

SYNC_LEDGER_VERSION = 1


class SyncLedgerStore:
    def load(self, runtime_path: Path) -> SyncLedger:
        path = sync_ledger_path(runtime_path)
        try:
            return SyncLedger.model_validate_json(path.read_text(encoding="utf-8"))
        except (OSError, ValidationError, ValueError):
            return empty_ledger()

    def save(
        self,
        runtime_path: Path,
        ledger: SyncLedger,
        now: datetime,
    ) -> SyncLedger:
        updated = ledger.model_copy(update={"updated_at": now})
        path = sync_ledger_path(runtime_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
        try:
            temporary.write_text(
                updated.model_dump_json(indent=2),
                encoding="utf-8",
            )
            temporary.replace(path)
        finally:
            if temporary.exists():
                temporary.unlink()
        return updated


def sync_ledger_path(runtime_path: Path) -> Path:
    return runtime_path / "runs" / "sync-ledger.json"


def empty_ledger() -> SyncLedger:
    return SyncLedger(
        version=SYNC_LEDGER_VERSION,
        updated_at=datetime.fromtimestamp(0, UTC),
        sessions={},
    )
