from pathlib import Path

from codealmanac.app import CodeAlmanac
from codealmanac.config.models import CodeAlmanacConfig
from codealmanac.config.requests import LoadConfigRequest
from codealmanac.engine.harnesses.models import HarnessKind


def load_cli_config(app: CodeAlmanac, wiki: str | None) -> CodeAlmanacConfig:
    return app.config.load(LoadConfigRequest(cwd=Path.cwd(), wiki=wiki))


def resolve_harness(value: str | None, config: CodeAlmanacConfig) -> HarnessKind:
    if value is None:
        return config.harness.default
    return HarnessKind(value)
