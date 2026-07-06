from codealmanac.cli.render.common import print_json_model
from codealmanac.services.config.models import ConfigSetResult


def render_config_set(result: ConfigSetResult, json_output: bool) -> None:
    if json_output:
        print_json_model(result)
        return
    value = "true" if result.value else "false"
    print(f"config: {result.key.value} = {value}")
