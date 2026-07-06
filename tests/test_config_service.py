from datetime import timedelta
from pathlib import Path

import pytest

from codealmanac.app import create_app
from codealmanac.core.errors import ValidationFailed
from codealmanac.core.models import AppConfig
from codealmanac.services.config.models import ConfigKey
from codealmanac.services.config.requests import (
    LoadConfigRequest,
    SetConfigValueRequest,
)
from codealmanac.services.harnesses.models import HarnessKind
from codealmanac.services.workspaces.requests import InitializeWorkspaceRequest


def test_config_service_returns_defaults_without_files(
    tmp_path: Path,
    isolated_home: Path,
):
    app = create_app(
        AppConfig(registry_path=isolated_home / ".codealmanac/registry.json")
    )

    config = app.config.load(LoadConfigRequest(cwd=tmp_path))

    assert config.auto_commit is True
    assert config.harness.default == HarnessKind.CODEX
    assert config.sync.quiet == timedelta(minutes=45)


def test_config_service_applies_user_then_project_precedence(
    tmp_path: Path,
    isolated_home: Path,
):
    user_config = isolated_home / ".codealmanac/config.toml"
    user_config.parent.mkdir(parents=True)
    user_config.write_text(
        """
auto_commit = false

[harness]
default = "codex"

[sync]
quiet = "30m"
""",
        encoding="utf-8",
    )
    repo = tmp_path / "repo"
    repo.mkdir()
    app = create_app(
        AppConfig(
            registry_path=isolated_home / ".codealmanac/registry.json",
            config_path=user_config,
        )
    )
    app.workflows.build.initialize(InitializeWorkspaceRequest(path=repo))
    (repo / "almanac/config.toml").write_text(
        """
auto_commit = true

[sync]
quiet = "5s"
""",
        encoding="utf-8",
    )

    config = app.config.load(LoadConfigRequest(cwd=repo))

    assert config.auto_commit is True
    assert config.harness.default == HarnessKind.CODEX
    assert config.sync.quiet == timedelta(seconds=5)


def test_config_service_uses_explicit_wiki_project_config(
    tmp_path: Path,
    isolated_home: Path,
):
    first = tmp_path / "first"
    second = tmp_path / "second"
    first.mkdir()
    second.mkdir()
    app = create_app(
        AppConfig(registry_path=isolated_home / ".codealmanac/registry.json")
    )
    app.workflows.build.initialize(InitializeWorkspaceRequest(path=first))
    app.workflows.build.initialize(InitializeWorkspaceRequest(path=second))
    (second / "almanac/config.toml").write_text(
        """
[harness]
default = "codex"
""",
        encoding="utf-8",
    )

    config = app.config.load(LoadConfigRequest(cwd=first, wiki="second"))

    assert config.harness.default == HarnessKind.CODEX


def test_config_service_reports_invalid_toml(
    tmp_path: Path,
    isolated_home: Path,
):
    config_path = isolated_home / ".codealmanac/config.toml"
    config_path.parent.mkdir(parents=True)
    config_path.write_text('[sync\nquiet = "0s"\n', encoding="utf-8")
    app = create_app(
        AppConfig(
            registry_path=isolated_home / ".codealmanac/registry.json",
            config_path=config_path,
        )
    )

    with pytest.raises(ValidationFailed, match="invalid config TOML"):
        app.config.load(LoadConfigRequest(cwd=tmp_path))


def test_config_service_reports_invalid_values(
    tmp_path: Path,
    isolated_home: Path,
):
    config_path = isolated_home / ".codealmanac/config.toml"
    config_path.parent.mkdir(parents=True)
    config_path.write_text(
        """
[harness]
default = "cursor"
""",
        encoding="utf-8",
    )
    app = create_app(
        AppConfig(
            registry_path=isolated_home / ".codealmanac/registry.json",
            config_path=config_path,
        )
    )

    with pytest.raises(ValidationFailed, match="invalid config"):
        app.config.load(LoadConfigRequest(cwd=tmp_path))


def test_config_service_sets_user_auto_commit(
    tmp_path: Path,
    isolated_home: Path,
):
    config_path = isolated_home / ".codealmanac/config.toml"
    config_path.parent.mkdir(parents=True)
    config_path.write_text(
        """
[sync]
quiet = "30m"
""",
        encoding="utf-8",
    )
    app = create_app(
        AppConfig(
            registry_path=isolated_home / ".codealmanac/registry.json",
            config_path=config_path,
        )
    )

    result = app.config.set(
        SetConfigValueRequest(key=ConfigKey.AUTO_COMMIT, value=False)
    )
    config = app.config.load(LoadConfigRequest(cwd=tmp_path))

    assert result.key == ConfigKey.AUTO_COMMIT
    assert result.value is False
    assert result.path == config_path.as_posix()
    assert config.auto_commit is False
    assert config.sync.quiet == timedelta(minutes=30)
    assert config_path.read_text(encoding="utf-8").startswith(
        "auto_commit = false\n\n[sync]"
    )
