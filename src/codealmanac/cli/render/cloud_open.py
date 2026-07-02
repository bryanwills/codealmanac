from codealmanac.cli.render.common import print_json_model
from codealmanac.workflows.cloud_open.models import CloudOpenResult


def render_cloud_open(result: CloudOpenResult, *, json_output: bool) -> None:
    if json_output:
        print_json_model(result)
        return
    state = "opened" if result.opened else "url"
    print(f"{state}: {result.url}")
