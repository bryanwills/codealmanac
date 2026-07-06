import os
from datetime import UTC, datetime, timedelta
from pathlib import Path

from pydantic import ValidationError

from codealmanac.core.models import CodeAlmanacModel


class UpdateLockRecord(CodeAlmanacModel):
    pid: int
    created_at: datetime


class UpdateLockLease:
    def __init__(self, path: Path):
        self.path = path

    def release(self) -> None:
        self.path.unlink(missing_ok=True)


class UpdateLockStore:
    def acquire(
        self,
        path: Path,
        now: datetime,
        stale_after: timedelta,
    ) -> UpdateLockLease | None:
        path.parent.mkdir(parents=True, exist_ok=True)
        for attempt in range(2):
            try:
                with path.open("x", encoding="utf-8") as handle:
                    record = UpdateLockRecord(
                        pid=os.getpid(),
                        created_at=now,
                    )
                    handle.write(record.model_dump_json())
                return UpdateLockLease(path)
            except FileExistsError:
                if attempt > 0 or not stale_lock(path, now, stale_after):
                    return None
                path.unlink(missing_ok=True)
        return None


def stale_lock(path: Path, now: datetime, stale_after: timedelta) -> bool:
    record = read_lock(path)
    if record is not None:
        age = now - record.created_at
        return age > stale_after
    try:
        modified_at = datetime.fromtimestamp(path.stat().st_mtime, tz=UTC)
    except OSError:
        return True
    return now - modified_at > stale_after


def read_lock(path: Path) -> UpdateLockRecord | None:
    try:
        return UpdateLockRecord.model_validate_json(path.read_text(encoding="utf-8"))
    except (OSError, ValidationError, ValueError):
        return None
