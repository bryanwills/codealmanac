from pathlib import Path

from pydantic import TypeAdapter

from codealmanac.runs.ledger.models import RunId

RUN_ID_ADAPTER = TypeAdapter(RunId)


def runs_dir(almanac_path: Path) -> Path:
    return almanac_path


def run_record_path(almanac_path: Path, run_id: str) -> Path:
    run_id = validate_run_id(run_id)
    return runs_dir(almanac_path) / f"{run_id}.json"


def run_spec_path(almanac_path: Path, run_id: str) -> Path:
    run_id = validate_run_id(run_id)
    return runs_dir(almanac_path) / f"{run_id}.spec.json"


def run_log_path(almanac_path: Path, run_id: str) -> Path:
    run_id = validate_run_id(run_id)
    return runs_dir(almanac_path) / f"{run_id}.jsonl"


def run_log_reference_path(log_reference_dir: Path, run_id: str) -> Path:
    run_id = validate_run_id(run_id)
    return log_reference_dir / f"{run_id}.jsonl"


def worker_lock_path(almanac_path: Path) -> Path:
    return runs_dir(almanac_path) / "worker.lock"


def worker_lock_owner_path(lock_path: Path) -> Path:
    return lock_path / "owner.json"


def validate_run_id(run_id: str) -> RunId:
    return RUN_ID_ADAPTER.validate_python(run_id)
