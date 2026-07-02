from rich.console import Console

from codealmanac.cli.render.common import print_json_model
from codealmanac.services.cloud_auth.models import CloudLogoutResult, CloudStatus
from codealmanac.workflows.cloud_login.models import CloudLoginWorkflowResult


def render_cloud_login_result(
    result: CloudLoginWorkflowResult,
    *,
    json_output: bool,
) -> None:
    if json_output:
        print_json_model(result)
        return
    console = Console(highlight=False)
    if result.status == "signed_in":
        console.print(f"Signed in as {result.github_login}")
        console.print(f"Cloud: {result.api_url}")
        return
    if result.status == "already_signed_in":
        console.print(f"Already signed in as {result.github_login}")
        console.print(f"Cloud: {result.api_url}")
        return
    console.print(f"Open: {result.verification_url}")
    if result.user_code is not None:
        console.print(f"Code: {result.user_code}")
    if result.status == "expired":
        console.print("Login expired. Run `codealmanac login` again.")
    else:
        console.print("Login timed out. Run `codealmanac login` again.")


def render_cloud_status(status: CloudStatus, *, json_output: bool) -> None:
    if json_output:
        print_json_model(status)
        return
    console = Console(highlight=False)
    if not status.authenticated:
        console.print("Not signed in")
        console.print(f"Cloud: {status.api_url}")
        return
    console.print(f"Signed in as {status.github_login}")
    console.print(f"Cloud: {status.api_url}")


def render_cloud_logout_result(result: CloudLogoutResult, *, json_output: bool) -> None:
    if json_output:
        print_json_model(result)
        return
    console = Console(highlight=False)
    if not result.signed_out:
        console.print("Already signed out")
        console.print(f"Cloud: {result.api_url}")
        return
    console.print(f"Signed out {result.github_login}")
    console.print(f"Cloud: {result.api_url}")
