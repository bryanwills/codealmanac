from pathlib import Path

from pydantic import TypeAdapter

from codealmanac.services.runs.models import RunId

RUN_ID_ADAPTER = TypeAdapter(RunId)


def runs_dir(runtime_path: Path) -> Path:
    return runtime_path / "runs"


def run_record_path(runtime_path: Path, run_id: str) -> Path:
    run_id = validate_run_id(run_id)
    return runs_dir(runtime_path) / f"{run_id}.json"


def run_spec_path(runtime_path: Path, run_id: str) -> Path:
    run_id = validate_run_id(run_id)
    return runs_dir(runtime_path) / f"{run_id}.spec.json"


def run_log_path(runtime_path: Path, run_id: str) -> Path:
    run_id = validate_run_id(run_id)
    return runs_dir(runtime_path) / f"{run_id}.jsonl"


def run_log_reference_path(run_id: str) -> Path:
    run_id = validate_run_id(run_id)
    return Path("runs") / f"{run_id}.jsonl"


def worker_lock_path(runtime_path: Path) -> Path:
    return runs_dir(runtime_path) / "worker.lock"


def worker_lock_owner_path(lock_path: Path) -> Path:
    return lock_path / "owner.json"


def validate_run_id(run_id: str) -> RunId:
    return RUN_ID_ADAPTER.validate_python(run_id)
