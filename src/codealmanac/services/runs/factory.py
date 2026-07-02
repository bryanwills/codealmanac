from datetime import datetime
from pathlib import Path
from uuid import uuid4

from codealmanac.services.runs.models import RunOperation, RunRecord, RunStatus
from codealmanac.services.runs.paths import run_log_reference_path


def new_run_id(operation: RunOperation, now: datetime) -> str:
    stamp = now.strftime("%Y%m%d%H%M%S")
    return f"{operation.value}-{stamp}-{uuid4().hex[:8]}"


def new_run_record(
    run_id: str,
    workspace_id: str,
    operation: RunOperation,
    title: str | None,
    now: datetime,
    log_reference_dir: Path,
) -> RunRecord:
    return RunRecord(
        run_id=run_id,
        workspace_id=workspace_id,
        operation=operation,
        status=RunStatus.QUEUED,
        title=title,
        created_at=now,
        updated_at=now,
        log_path=run_log_reference_path(log_reference_dir, run_id),
    )
