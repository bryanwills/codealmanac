from pathlib import Path


def home_dir() -> Path:
    return Path.home()


def global_state_dir() -> Path:
    return home_dir() / ".almanac"


def default_registry_path() -> Path:
    return global_state_dir() / "registry.json"


def default_config_path() -> Path:
    return global_state_dir() / "config.toml"


def normalize_path(path: Path) -> Path:
    return path.expanduser().resolve(strict=False)
