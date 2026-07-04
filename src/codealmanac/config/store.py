from pathlib import Path
from tomllib import TOMLDecodeError

from pydantic import ValidationError
from pydantic_settings import TomlConfigSettingsSource

from codealmanac.config.models import CodeAlmanacConfig
from codealmanac.core.errors import ValidationFailed


class ConfigStore:
    def load(self, paths: tuple[Path, ...]) -> CodeAlmanacConfig:
        try:
            sources = tuple(
                TomlConfigSettingsSource(
                    CodeAlmanacConfig,
                    toml_file=path,
                    deep_merge=True,
                )
                for path in paths
            )
            return CodeAlmanacConfig(_build_sources=(sources, {}))
        except TOMLDecodeError as error:
            raise ValidationFailed(f"invalid config TOML: {error}") from error
        except ValidationError as error:
            raise ValidationFailed(f"invalid config: {error}") from error
