from pathlib import Path

from codealmanac.integrations.command import CommandRunner
from codealmanac.integrations.sources.filesystem.documents import (
    FilesystemDirectoryDocument,
    FilesystemTextDocument,
    UnreadableTextError,
    read_text_document,
)
from codealmanac.integrations.sources.filesystem.git import git_directory_candidates
from codealmanac.integrations.sources.filesystem.ignore import ignore_spec_for
from codealmanac.integrations.sources.filesystem.paths import display_path
from codealmanac.integrations.sources.filesystem.selection import (
    FilesystemDirectoryFileState,
    FilesystemDirectoryListingSource,
    FilesystemDirectorySelectionPolicy,
    ranked_directory_candidates,
)
from codealmanac.integrations.sources.filesystem.walk import walk_file_candidates


def read_directory_document(
    root: Path,
    cwd: Path,
    max_file_bytes: int,
    max_directory_files: int,
    runner: CommandRunner,
    git_timeout_seconds: int,
    ignored_directories: tuple[Path, ...],
) -> FilesystemDirectoryDocument:
    ignore_spec = ignore_spec_for(root, cwd, ignored_directories)
    listing_source = FilesystemDirectoryListingSource.WALK
    selection_policy = FilesystemDirectorySelectionPolicy.DIVERSE
    candidates = ranked_directory_candidates(
        tuple(walk_file_candidates(root, cwd, ignore_spec))
    )
    git_candidates = git_directory_candidates(
        root,
        cwd,
        runner,
        git_timeout_seconds,
        ignore_spec,
    )
    if git_candidates is not None:
        listing_source = FilesystemDirectoryListingSource.GIT
        selection_policy = FilesystemDirectorySelectionPolicy.CHANGED_THEN_DIVERSE
        candidates = git_candidates
    files: list[FilesystemTextDocument] = []
    skipped_count = 0
    file_list_truncated = False
    changed_count = sum(
        1
        for candidate in candidates
        if candidate.state == FilesystemDirectoryFileState.CHANGED
    )
    for candidate in candidates:
        if len(files) >= max_directory_files:
            file_list_truncated = True
            break
        try:
            files.append(
                read_text_document(
                    candidate.path,
                    cwd,
                    max_file_bytes,
                    candidate.state,
                    candidate.git_status,
                )
            )
        except (OSError, UnreadableTextError):
            skipped_count += 1
    return FilesystemDirectoryDocument(
        path=root,
        display_path=display_path(root, cwd),
        listing_source=listing_source,
        selection_policy=selection_policy,
        changed_count=changed_count,
        files=tuple(files),
        skipped_count=skipped_count,
        file_list_truncated=file_list_truncated,
    )
