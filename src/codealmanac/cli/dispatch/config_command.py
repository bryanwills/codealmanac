import argparse

from codealmanac.app import CodeAlmanac
from codealmanac.cli.render.admin import render_config_set
from codealmanac.services.config.models import ConfigKey
from codealmanac.services.config.requests import SetConfigValueRequest


def dispatch_config(args: argparse.Namespace, app: CodeAlmanac) -> int:
    if args.config_command == "set":
        result = app.config.set(
            SetConfigValueRequest(
                key=ConfigKey(args.key),
                value=parse_bool(args.value),
            )
        )
        render_config_set(result, json_output=False)
        return 0
    raise AssertionError(f"unhandled config command: {args.config_command}")


def parse_bool(value: str) -> bool:
    return value == "true"
