from hashlib import sha256
from uuid import uuid4

from codealmanac.database import SQLiteRow
from codealmanac.services.control.models import (
    BranchRecord,
    RepositoryRecord,
    TriggerEventRecord,
)


def repository_id_for(provider: str, full_name: str) -> str:
    return stable_control_id("repo", provider, full_name)


def branch_id_for(repository_id: str, name: str) -> str:
    return stable_control_id("branch", repository_id, name)


def trigger_event_id() -> str:
    return f"trigger_{uuid4().hex}"


def stable_control_id(prefix: str, *parts: str) -> str:
    digest = sha256("\0".join(part.casefold() for part in parts).encode()).hexdigest()
    return f"{prefix}_{digest[:16]}"


def repository_from_row(row: SQLiteRow) -> RepositoryRecord:
    return RepositoryRecord.model_validate(dict(row))


def branch_from_row(row: SQLiteRow) -> BranchRecord:
    return BranchRecord.model_validate(dict(row))


def trigger_event_from_row(row: SQLiteRow) -> TriggerEventRecord:
    return TriggerEventRecord.model_validate(dict(row))
