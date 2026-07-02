import argparse

from codealmanac.app import CodeAlmanac
from codealmanac.cli.dispatch.admin import dispatch_admin, is_admin_command
from codealmanac.cli.dispatch.lifecycle import (
    dispatch_lifecycle,
    is_lifecycle_command,
)
from codealmanac.cli.dispatch.local import dispatch_local, is_local_command
from codealmanac.cli.dispatch.wiki import dispatch_wiki, is_wiki_command


def dispatch(args: argparse.Namespace, app: CodeAlmanac) -> int:
    if is_lifecycle_command(args.command):
        return dispatch_lifecycle(args, app)
    if is_local_command(args.command):
        return dispatch_local(args, app)
    if is_wiki_command(args.command):
        return dispatch_wiki(args, app)
    if is_admin_command(args.command):
        return dispatch_admin(args, app)
    raise AssertionError(f"unhandled command: {args.command}")
