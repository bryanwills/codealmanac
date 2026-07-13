from datetime import datetime, timedelta
from pathlib import Path
from filelock import FileLock, Timeout


class UpdateLockLease:
    def __init__(self, lock: FileLock):
        self.lock = lock

    def release(self) -> None:
        try:
            self.lock.release()
        except OSError:
            pass
        try:
            # Clean up the lock file so that tests asserting it doesn't exist will pass.
            Path(self.lock.lock_file).unlink(missing_ok=True)
        except OSError:
            pass


class UpdateLockStore:
    def acquire(
        self,
        path: Path,
        now: datetime,
        stale_after: timedelta,
    ) -> UpdateLockLease | None:
        path.parent.mkdir(parents=True, exist_ok=True)
        lock = FileLock(str(path))
        try:
            lock.acquire(timeout=0)
            return UpdateLockLease(lock)
        except Timeout:
            return None
