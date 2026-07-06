from pathlib import Path

from humanfriendly import InvalidTimespan, parse_timespan

from codealmanac.core.errors import NotFoundError, ValidationFailed
from codealmanac.core.paths import normalize_path
from codealmanac.services.config.models import (
    CodeAlmanacConfig,
    ConfigKey,
    ConfigSetResult,
)
from codealmanac.services.config.requests import (
    LoadConfigRequest,
    SetConfigValueRequest,
)
from codealmanac.services.config.store import ConfigStore
from codealmanac.services.harnesses.models import HarnessKind
from codealmanac.services.workspaces.requests import SelectWorkspaceRequest
from codealmanac.services.workspaces.service import WorkspacesService

PROJECT_CONFIG_NAME = "config.toml"


class ConfigService:
    def __init__(
        self,
        workspaces: WorkspacesService,
        store: ConfigStore,
        user_config_path: Path,
    ):
        self.workspaces = workspaces
        self.store = store
        self.user_config_path = user_config_path

    def load(self, request: LoadConfigRequest) -> CodeAlmanacConfig:
        project_config_path = self._project_config_path(request)
        paths = config_source_paths(
            user_config_path=normalize_path(self.user_config_path),
            project_config_path=project_config_path,
        )
        return self.store.load(paths)

    def load_user(self) -> CodeAlmanacConfig:
        return self.store.load((normalize_path(self.user_config_path),))

    def set(self, request: SetConfigValueRequest) -> ConfigSetResult:
        path = normalize_path(self.user_config_path)
        if request.key == ConfigKey.AUTO_COMMIT:
            normalized = parse_bool_value(request.value)
            self.store.set_value(path, None, "auto_commit", normalized)
        elif request.key == ConfigKey.HARNESS_DEFAULT:
            normalized = parse_harness_value(request.value)
            self.store.set_value(path, "harness", "default", f'"{normalized}"')
        elif request.key == ConfigKey.SYNC_QUIET:
            normalized = parse_quiet_value(request.value)
            self.store.set_value(path, "sync", "quiet", f'"{normalized}"')
        else:
            raise AssertionError(f"unhandled config key: {request.key}")
        # Defense in depth: reject a write that leaves the config unloadable.
        self.store.load((path,))
        return ConfigSetResult(
            path=path.as_posix(),
            key=request.key,
            value=normalized,
        )

    def _project_config_path(self, request: LoadConfigRequest) -> Path | None:
        if request.wiki is not None:
            workspace = self.workspaces.select(
                SelectWorkspaceRequest(
                    selector=request.wiki,
                    base_path=request.cwd,
                )
            )
            return workspace.almanac_path / PROJECT_CONFIG_NAME
        try:
            workspace = self.workspaces.resolve(request.cwd)
        except (NotFoundError, OSError):
            return None
        return workspace.almanac_path / PROJECT_CONFIG_NAME


def parse_bool_value(value: str) -> str:
    token = value.strip().lower()
    if token not in ("true", "false"):
        raise ValidationFailed("auto_commit must be true or false")
    return token


def parse_harness_value(value: str) -> str:
    token = value.strip().lower()
    kinds = tuple(kind.value for kind in HarnessKind)
    if token not in kinds:
        raise ValidationFailed(
            f"harness.default must be one of: {', '.join(kinds)}"
        )
    return token


def parse_quiet_value(value: str) -> str:
    token = value.strip()
    try:
        seconds = parse_timespan(token)
    except InvalidTimespan as error:
        raise ValidationFailed(
            "sync.quiet must be a duration (e.g. 45m, 2h)"
        ) from error
    if seconds < 0:
        raise ValidationFailed("sync.quiet must be zero or greater")
    return token


def config_source_paths(
    user_config_path: Path,
    project_config_path: Path | None,
) -> tuple[Path, ...]:
    if project_config_path is None:
        return (user_config_path,)
    return (project_config_path, user_config_path)
