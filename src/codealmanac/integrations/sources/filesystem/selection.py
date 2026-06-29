from enum import StrEnum
from pathlib import Path

from pydantic import field_validator

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.core.text import required_text


class FilesystemDirectoryListingSource(StrEnum):
    GIT = "git"
    WALK = "walk"


class FilesystemDirectoryFileState(StrEnum):
    CHANGED = "changed"
    UNCHANGED = "unchanged"


class FilesystemDirectorySelectionPolicy(StrEnum):
    CHANGED_THEN_DIVERSE = "changed_then_diverse"
    DIVERSE = "diverse"


class FilesystemDirectoryCandidate(CodeAlmanacModel):
    path: Path
    display_path: str
    selection_group: str
    state: FilesystemDirectoryFileState = FilesystemDirectoryFileState.UNCHANGED
    git_status: str | None = None

    @field_validator("display_path", "selection_group")
    @classmethod
    def require_display_path(cls, value: str) -> str:
        return required_text(value, "filesystem directory candidate")

    @field_validator("git_status")
    @classmethod
    def validate_git_status(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if len(value) != 2:
            raise ValueError("filesystem directory git status must be two characters")
        return value


SOURCE_SUFFIXES = frozenset(
    {
        ".c",
        ".cc",
        ".cpp",
        ".cs",
        ".css",
        ".go",
        ".h",
        ".hpp",
        ".html",
        ".java",
        ".js",
        ".jsx",
        ".kt",
        ".mjs",
        ".php",
        ".py",
        ".rb",
        ".rs",
        ".scss",
        ".sh",
        ".sql",
        ".swift",
        ".ts",
        ".tsx",
        ".vue",
    }
)
STRUCTURED_SUFFIXES = frozenset(
    {
        ".cfg",
        ".ini",
        ".json",
        ".md",
        ".toml",
        ".yaml",
        ".yml",
    }
)
LOW_VALUE_FILENAMES = frozenset(
    {
        ".gitkeep",
        "__init__.py",
    }
)
PRIMARY_ROLE_FILENAMES = frozenset(
    {
        "adapter.py",
        "app.py",
        "main.py",
        "service.py",
    }
)
SECONDARY_ROLE_FILENAMES = frozenset(
    {
        "models.py",
        "ports.py",
        "renderer.py",
        "requests.py",
        "root.py",
        "store.py",
    }
)


def ranked_directory_candidates(
    candidates: tuple[FilesystemDirectoryCandidate, ...],
) -> tuple[FilesystemDirectoryCandidate, ...]:
    changed = tuple(
        candidate
        for candidate in candidates
        if candidate.state == FilesystemDirectoryFileState.CHANGED
    )
    unchanged = tuple(
        candidate
        for candidate in candidates
        if candidate.state == FilesystemDirectoryFileState.UNCHANGED
    )
    return (
        *diverse_directory_candidates(changed),
        *diverse_directory_candidates(unchanged),
    )


def directory_candidate_key(
    candidate: FilesystemDirectoryCandidate,
) -> tuple[int, int, int, str]:
    return (
        filename_role_rank(candidate.path),
        unchanged_content_rank(candidate.path),
        path_depth(candidate.display_path),
        candidate.display_path.casefold(),
    )


def diverse_directory_candidates(
    candidates: tuple[FilesystemDirectoryCandidate, ...],
) -> tuple[FilesystemDirectoryCandidate, ...]:
    grouped: dict[str, list[FilesystemDirectoryCandidate]] = {}
    for candidate in candidates:
        grouped.setdefault(candidate.selection_group, []).append(candidate)
    for group_candidates in grouped.values():
        group_candidates.sort(key=directory_candidate_key)
    groups = tuple(
        sorted(
            grouped.items(),
            key=lambda item: (directory_candidate_key(item[1][0]), item[0].casefold()),
        )
    )
    ordered: list[FilesystemDirectoryCandidate] = []
    index = 0
    while True:
        added = False
        for _group, group_candidates in groups:
            if index >= len(group_candidates):
                continue
            ordered.append(group_candidates[index])
            added = True
        if not added:
            return tuple(ordered)
        index += 1


def filename_role_rank(path: Path) -> int:
    name = path.name
    if name in PRIMARY_ROLE_FILENAMES:
        return 0
    if name in SECONDARY_ROLE_FILENAMES:
        return 1
    if name in LOW_VALUE_FILENAMES:
        return 4
    return 2


def unchanged_content_rank(path: Path) -> int:
    if path.name in LOW_VALUE_FILENAMES:
        return 3
    suffix = path.suffix.casefold()
    if suffix in SOURCE_SUFFIXES:
        return 0
    if suffix in STRUCTURED_SUFFIXES:
        return 1
    return 2


def path_depth(display_path: str) -> int:
    return display_path.count("/")


def directory_selection_group(path: Path, root: Path) -> str:
    try:
        relative = path.relative_to(root)
    except ValueError:
        return path.name
    parts = relative.parts
    if len(parts) == 0:
        return "."
    if len(parts) == 1:
        return parts[0]
    if Path(parts[1]).suffix:
        return parts[0]
    return "/".join(parts[:2])
