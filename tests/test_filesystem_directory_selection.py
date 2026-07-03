from pathlib import Path

from codealmanac.integrations.sources.filesystem.selection import (
    FilesystemDirectoryCandidate,
    directory_selection_group,
    ranked_directory_candidates,
)


def test_directory_selection_interleaves_groups_before_second_file():
    root = Path("/repo/src")
    candidates = (
        candidate(root, "alpha/a.py"),
        candidate(root, "alpha/b.py"),
        candidate(root, "alpha/c.py"),
        candidate(root, "beta/service.py"),
        candidate(root, "gamma/adapter.py"),
    )

    ranked = ranked_directory_candidates(candidates)

    assert tuple(item.display_path for item in ranked[:3]) == (
        "src/beta/service.py",
        "src/gamma/adapter.py",
        "src/alpha/a.py",
    )


def test_directory_selection_group_uses_two_directory_levels():
    root = Path("/repo/src/codealmanac")

    assert directory_selection_group(root / "app.py", root) == "app.py"
    assert directory_selection_group(root / "cli/main.py", root) == "cli"
    assert (
        directory_selection_group(root / "engine/sources/service.py", root)
        == "engine/sources"
    )


def candidate(root: Path, relative_path: str) -> FilesystemDirectoryCandidate:
    path = root / relative_path
    return FilesystemDirectoryCandidate(
        path=path,
        display_path=f"src/{relative_path}",
        selection_group=directory_selection_group(path, root),
    )
