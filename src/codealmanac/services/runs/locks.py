import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path

from pydantic import ValidationError

from codealmanac.services.runs.models import RunWorkerLockOwner
from codealmanac.services.runs.paths import worker_lock_owner_path, worker_lock_path


class RunWorkerLease:
    def __init__(self, lock_path: Path, owner: RunWorkerLockOwner):
        self.lock_path = lock_path
        self.owner = owner

    def release(self) -> None:
        current = read_worker_lock_owner(self.lock_path)
        if current != self.owner:
            return
        shutil.rmtree(self.lock_path, ignore_errors=True)


def acquire_worker_lock(
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
