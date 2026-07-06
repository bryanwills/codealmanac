from pathlib import Path

from pydantic import ValidationError

from codealmanac.services.runs.models import RunRecord, RunStatus

ACTIVE_RUN_STATUSES = frozenset((RunStatus.QUEUED, RunStatus.RUNNING))


def active_run_count(state_dir: Path) -> int:
    count = 0
    repos_dir = state_dir / "repos"
    if not repos_dir.is_dir():
        return count
    for path in sorted(repos_dir.glob("*/runs/*.json")):
        if path.name.endswith(".spec.json"):
            continue
        record = read_run_record(path)
        if record is not None and record.status in ACTIVE_RUN_STATUSES:
            count += 1
    return count


def read_run_record(path: Path) -> RunRecord | None:
    try:
        return RunRecord.model_validate_json(path.read_text(encoding="utf-8"))
    except (OSError, ValidationError, ValueError):
        return None
