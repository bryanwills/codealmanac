from contextlib import suppress
from pathlib import Path

from pathspec.gitignore import GitIgnoreSpec

from codealmanac.integrations.sources.filesystem.paths import is_relative_to

DEFAULT_IGNORE_PATTERNS = (
    ".git/",
    "node_modules/",
    ".venv/",
    "venv/",
    "__pycache__/",
    ".mypy_cache/",
    ".pytest_cache/",
    ".ruff_cache/",
    ".gitignore",
    ".env",
    ".env.*",
    "*.pyc",
    ".DS_Store",
)


def ignore_spec_for(
    root: Path,
    cwd: Path,
    ignored_directories: tuple[Path, ...],
) -> GitIgnoreSpec:
    lines = list(DEFAULT_IGNORE_PATTERNS)
    lines.extend(ignored_directory_patterns(ignored_directories))
    gitignore = cwd / ".gitignore" if is_relative_to(root, cwd) else root / ".gitignore"
    if gitignore.is_file():
        with suppress(OSError):
            lines.extend(gitignore.read_text(encoding="utf-8").splitlines())
    return GitIgnoreSpec.from_lines(lines)


def should_skip_path(
    path: Path,
    cwd: Path,
    root: Path,
    ignore_spec: GitIgnoreSpec,
) -> bool:
    return ignore_spec.match_file(ignore_key(path, cwd, root))


def ignore_key(path: Path, cwd: Path, root: Path) -> str:
    base = cwd if is_relative_to(path, cwd) else root
    return path.relative_to(base).as_posix()


def ignored_directory_patterns(
    ignored_directories: tuple[Path, ...],
) -> tuple[str, ...]:
    return tuple(
        f"{directory.as_posix().rstrip('/')}/" for directory in ignored_directories
    )
