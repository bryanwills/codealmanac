from datetime import timedelta
from pathlib import Path

from humanfriendly import InvalidTimespan, parse_timespan

from codealmanac.app import CodeAlmanac
from codealmanac.core.errors import ValidationFailed
from codealmanac.services.config.models import CodeAlmanacConfig
from codealmanac.services.config.requests import LoadConfigRequest
from codealmanac.services.harnesses.models import HarnessKind
from codealmanac.workflows.sync.requests import DEFAULT_SYNC_PENDING_TIMEOUT


def load_cli_config(app: CodeAlmanac, wiki: str | None) -> CodeAlmanacConfig:
    return app.config.load(LoadConfigRequest(cwd=Path.cwd(), wiki=wiki))


def resolve_harness(value: str | None, config: CodeAlmanacConfig) -> HarnessKind:
    if value is None:
        return config.harness.default
    return HarnessKind(value)


def resolve_quiet(value: str | None, config: CodeAlmanacConfig) -> timedelta:
    if value is None:
        return config.sync.quiet
    return parse_quiet(value)


def resolve_pending_timeout(value: str | None) -> timedelta:
    parsed = parse_optional_duration(value, "--pending-timeout")
    return parsed or DEFAULT_SYNC_PENDING_TIMEOUT


def parse_quiet(value: str) -> timedelta:
    try:
        seconds = parse_timespan(value)
    except InvalidTimespan as error:
        raise ValidationFailed(f"invalid --quiet value: {value}") from error
    return timedelta(seconds=seconds)


def parse_optional_duration(value: str | None, flag: str) -> timedelta | None:
    if value is None:
        return None
    try:
        seconds = parse_timespan(value)
    except InvalidTimespan as error:
        raise ValidationFailed(f"invalid {flag} value: {value}") from error
    return timedelta(seconds=seconds)
