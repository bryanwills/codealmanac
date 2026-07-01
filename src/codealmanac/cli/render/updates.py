import shlex

from codealmanac.cli.render.common import print_json_model
from codealmanac.services.updates.models import UpdatePlan, UpdateResult


def render_update_plan(plan: UpdatePlan, json_output: bool) -> None:
    if json_output:
        print_json_model(plan)
        return
    print(f"codealmanac {plan.installed_version}")
    print(f"update status: {plan.status.value}")
    print(f"install method: {plan.method.value}")
    print(f"message: {plan.message}")
    if plan.command:
        print(f"command: {shell_command(plan.command)}")
    if plan.fix is not None:
        print(plan.fix)


def render_update_result(result: UpdateResult, json_output: bool) -> None:
    if json_output:
        print_json_model(result)
        return
    render_update_plan(result.plan, json_output=False)
    if result.exit_code is not None:
        print(f"exit_code: {result.exit_code}")
    if result.stdout:
        print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
    if result.stderr:
        print(result.stderr, end="" if result.stderr.endswith("\n") else "\n")


def shell_command(command: tuple[str, ...]) -> str:
    return shlex.join(command)
