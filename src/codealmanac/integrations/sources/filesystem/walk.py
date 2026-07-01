from collections.abc import Iterator
from pathlib import Path

from pathspec.gitignore import GitIgnoreSpec

from codealmanac.integrations.sources.filesystem.ignore import should_skip_path
from codealmanac.integrations.sources.filesystem.paths import display_path
from codealmanac.integrations.sources.filesystem.selection import (
    FilesystemDirectoryCandidate,
    directory_selection_group,
)


def walk_file_candidates(
    root: Path,
    cwd: Path,
    ignore_spec: GitIgnoreSpec,
) -> Iterator[FilesystemDirectoryCandidate]:
    for path in walk_files(root, cwd, ignore_spec):
        yield FilesystemDirectoryCandidate(
            path=path,
            display_path=display_path(path, cwd),
            selection_group=directory_selection_group(path, root),
        )


def walk_files(
    root: Path,
    cwd: Path,
    ignore_spec: GitIgnoreSpec,
) -> Iterator[Path]:
    for child in sorted_children(root):
        if should_skip_path(child, cwd, root, ignore_spec):
            continue
        if child.is_symlink():
            continue
        if child.is_dir():
            yield from walk_files(child, cwd, ignore_spec)
            continue
        if child.is_file():
            yield child


def sorted_children(path: Path) -> tuple[Path, ...]:
    try:
        return tuple(sorted(path.iterdir(), key=lambda child: child.name.casefold()))
    except OSError:
        return ()
