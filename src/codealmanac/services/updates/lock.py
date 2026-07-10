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
        record = UpdateLockRecord(pid=os.getpid(), created_at=now)
        payload = record.model_dump_json()

        # Fast path: no existing lock — atomic exclusive create.
        try:
            with path.open("x", encoding="utf-8") as handle:
                handle.write(payload)
            return UpdateLockLease(path)
        except FileExistsError:
            pass

        # Stale lock: atomically replace it so there's no window between
        # unlinking and recreating. os.replace() is atomic on all platforms.
        # If we lose the race (different PID in the file after replace),
        # we back off — only one winner.
        if not stale_lock(path, now, stale_after):
            return None

        tmp = path.with_suffix(f".{os.getpid()}.tmp")
        try:
            tmp.write_text(payload, encoding="utf-8")
            os.replace(tmp, path)
            owned = read_lock(path)
            if owned is not None and owned.pid == os.getpid():
                return UpdateLockLease(path)
            return None
        except OSError:
            return None
        finally:
            tmp.unlink(missing_ok=True)


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
