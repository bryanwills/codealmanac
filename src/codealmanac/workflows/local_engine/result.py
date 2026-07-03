from pathlib import Path

from codealmanac.engine.harnesses.models import HarnessRunResult
from codealmanac.engine.lifecycle import first_line
from codealmanac.services.engine_runs.models import (
    COMMIT_SUBJECT_PREFIX,
    EngineChangedFile,
    EngineFileChangeKind,
)

DEFAULT_COMMIT_DESCRIPTION = "update wiki"


def engine_changed_files(
    repo_path: Path,
    harness: HarnessRunResult,
) -> tuple[EngineChangedFile, ...]:
    return tuple(
        EngineChangedFile(
            path=path,
            kind=change_kind_for(repo_path / path),
        )
        for path in harness.changed_files
    )


def change_kind_for(path: Path) -> EngineFileChangeKind:
    if path.exists():
        return EngineFileChangeKind.UPDATED
    return EngineFileChangeKind.DELETED


def commit_subject_from_summary(summary: str | None) -> str:
    description = summary_description(summary)
    if description.startswith(COMMIT_SUBJECT_PREFIX):
        return description
    return f"{COMMIT_SUBJECT_PREFIX} {lowercase_first(description)}"


def summary_description(summary: str | None) -> str:
    if summary is None:
        return DEFAULT_COMMIT_DESCRIPTION
    line = first_line(summary).strip()
    if line == "":
        return DEFAULT_COMMIT_DESCRIPTION
    return line.rstrip(".")


def lowercase_first(value: str) -> str:
    if value == "":
        return value
    return value[:1].lower() + value[1:]
