import argparse

from codealmanac.app import CodeAlmanac
from codealmanac.cli.render.admin import render_update_plan, render_update_result
from codealmanac.services.updates.models import UpdateStatus
from codealmanac.services.updates.requests import CheckUpdateRequest, RunUpdateRequest


def dispatch_update(args: argparse.Namespace, app: CodeAlmanac) -> int:
    if args.check:
        plan = app.updates.check(CheckUpdateRequest())
        render_update_plan(plan, json_output=args.json)
        return 0
    result = app.updates.run(RunUpdateRequest(scheduled=args.scheduled))
    render_update_result(result, json_output=args.json)
    if result.status in {UpdateStatus.COMPLETED, UpdateStatus.SKIPPED}:
        return 0
    return 1
