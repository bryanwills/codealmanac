from pathlib import Path


def home_dir() -> Path:
    return Path.home()


def global_state_dir() -> Path:
    return home_dir() / ".almanac"


def default_registry_path() -> Path:
    return global_state_dir() / "registry.json"


def normalize_path(path: Path) -> Path:
    return path.expanduser().resolve(strict=False)


def nearest_almanac_root(path: Path) -> Path | None:
    current = normalize_path(path)
    if current.is_file():
        current = current.parent
    for candidate in [current, *current.parents]:
        if (candidate / ".almanac").is_dir():
            return candidate
    return None
