from codealmanac.cli.render.common import print_json_model
from codealmanac.services.config.models import ConfigSetResult


def render_config_set(result: ConfigSetResult, json_output: bool) -> None:
    if json_output:
        print_json_model(result)
        return
    print(f"config: {result.key.value} = {result.value}")
