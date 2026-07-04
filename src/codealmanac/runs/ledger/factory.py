from datetime import datetime
from pathlib import Path
from uuid import uuid4

from codealmanac.runs.ledger.models import RunKind, RunRecord, RunStatus
from codealmanac.runs.ledger.paths import run_log_reference_path


def new_run_id(kind: RunKind, now: datetime) -> str:
    stamp = now.strftime("%Y%m%d%H%M%S")
    return f"{kind.value}-{stamp}-{uuid4().hex[:8]}"


def new_run_record(
    run_id: str,
    workspace_id: str,
    kind: RunKind,
    title: str | None,
    now: datetime,
    log_reference_dir: Path,
) -> RunRecord:
    return RunRecord(
        run_id=run_id,
        workspace_id=workspace_id,
        kind=kind,
        status=RunStatus.QUEUED,
        title=title,
        created_at=now,
        updated_at=now,
        log_path=run_log_reference_path(log_reference_dir, run_id),
    )
