import tomllib
from pathlib import Path
from tomllib import TOMLDecodeError

from pydantic import ValidationError
from pydantic_settings import TomlConfigSettingsSource

from codealmanac.core.errors import ValidationFailed
from codealmanac.services.config.models import CodeAlmanacConfig


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

    def set_auto_commit(self, path: Path, enabled: bool) -> None:
        body = ""
        if path.exists():
            try:
                body = path.read_text(encoding="utf-8")
                tomllib.loads(body)
            except TOMLDecodeError as error:
                raise ValidationFailed(f"invalid config TOML: {error}") from error
            except OSError as error:
                raise ValidationFailed(f"cannot read config: {error}") from error
        updated = update_top_level_bool(
            body=body,
            key="auto_commit",
            value=enabled,
        )
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(updated, encoding="utf-8")
        except OSError as error:
            raise ValidationFailed(f"cannot write config: {error}") from error


def update_top_level_bool(body: str, key: str, value: bool) -> str:
    replacement = f"{key} = {bool_literal(value)}"
    lines = strip_leading_blank_lines(body.splitlines())
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("["):
            return insert_before_table(lines, index, replacement)
        if top_level_key(stripped) == key:
            lines[index] = replacement
            return with_trailing_newline(lines)
    return with_trailing_newline([replacement, *lines])


def strip_leading_blank_lines(lines: list[str]) -> list[str]:
    while lines and not lines[0].strip():
        lines = lines[1:]
    return lines


def insert_before_table(lines: list[str], index: int, replacement: str) -> str:
    prefix = lines[:index]
    suffix = lines[index:]
    if prefix and prefix[-1].strip():
        prefix = [*prefix, ""]
    return with_trailing_newline([*prefix, replacement, "", *suffix])


def top_level_key(stripped_line: str) -> str | None:
    if not stripped_line or stripped_line.startswith("#") or "=" not in stripped_line:
        return None
    return stripped_line.split("=", 1)[0].strip()


def bool_literal(value: bool) -> str:
    return "true" if value else "false"


def with_trailing_newline(lines: list[str]) -> str:
    return "\n".join(lines).rstrip() + "\n"
