import tomllib
from datetime import UTC, datetime
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

    def set_value(
        self,
        path: Path,
        table: str | None,
        key: str,
        literal: str,
    ) -> None:
        body = ""
        if path.exists():
            try:
                body = path.read_text(encoding="utf-8")
                tomllib.loads(body)
            except TOMLDecodeError as error:
                raise ValidationFailed(f"invalid config TOML: {error}") from error
            except OSError as error:
                raise ValidationFailed(f"cannot read config: {error}") from error
        updated = update_toml_value(body=body, table=table, key=key, literal=literal)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(updated, encoding="utf-8")
        except OSError as error:
            raise ValidationFailed(f"cannot write config: {error}") from error

    def set_sync_ignore_transcripts_before_if_missing(
        self,
        path: Path,
        baseline: datetime,
    ) -> bool:
        body = ""
        if path.exists():
            try:
                body = path.read_text(encoding="utf-8")
                parsed = tomllib.loads(body)
            except TOMLDecodeError as error:
                raise ValidationFailed(f"invalid config TOML: {error}") from error
            except OSError as error:
                raise ValidationFailed(f"cannot read config: {error}") from error
            sync = parsed.get("sync")
            if (
                isinstance(sync, dict)
                and "ignore_transcripts_before" in sync
            ):
                return False
        updated = set_sync_ignore_transcripts_before(
            body,
            format_datetime(baseline),
        )
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(updated, encoding="utf-8")
        except OSError as error:
            raise ValidationFailed(f"cannot write config: {error}") from error
        return True


def update_toml_value(body: str, table: str | None, key: str, literal: str) -> str:
    replacement = f"{key} = {literal}"
    lines = strip_leading_blank_lines(body.splitlines())
    if table is None:
        return update_top_level_value(lines, key, replacement)
    return update_table_value(lines, table, key, replacement)


def update_top_level_value(lines: list[str], key: str, replacement: str) -> str:
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("["):
            return insert_before_table(lines, index, replacement)
        if top_level_key(stripped) == key:
            lines[index] = replacement
            return with_trailing_newline(lines)
    return with_trailing_newline([replacement, *lines])


def update_table_value(
    lines: list[str],
    table: str,
    key: str,
    replacement: str,
) -> str:
    header = f"[{table}]"
    in_table = False
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("["):
            if in_table:
                return insert_into_table(lines, index, replacement)
            in_table = stripped == header
            continue
        if in_table and top_level_key(stripped) == key:
            lines[index] = replacement
            return with_trailing_newline(lines)
    if in_table:
        return with_trailing_newline([*lines, replacement])
    if lines and lines[-1].strip():
        return with_trailing_newline([*lines, "", header, replacement])
    return with_trailing_newline([*lines, header, replacement])


def insert_into_table(lines: list[str], index: int, replacement: str) -> str:
    prefix = lines[:index]
    while prefix and not prefix[-1].strip():
        prefix = prefix[:-1]
    return with_trailing_newline([*prefix, replacement, "", *lines[index:]])


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


def set_sync_ignore_transcripts_before(body: str, value: str) -> str:
    replacement = f"ignore_transcripts_before = {value}"
    lines = strip_leading_blank_lines(body.splitlines())
    sync_index = table_index(lines, "sync")
    if sync_index is None:
        if lines and lines[-1].strip():
            lines.append("")
        lines.extend(("[sync]", replacement))
        return with_trailing_newline(lines)
    insert_at = next_table_index(lines, sync_index + 1)
    block = lines[sync_index + 1 : insert_at]
    for offset, line in enumerate(block, start=sync_index + 1):
        if top_level_key(line.strip()) == "ignore_transcripts_before":
            lines[offset] = replacement
            return with_trailing_newline(lines)
    lines.insert(sync_index + 1, replacement)
    return with_trailing_newline(lines)


def table_index(lines: list[str], name: str) -> int | None:
    header = f"[{name}]"
    for index, line in enumerate(lines):
        if line.strip() == header:
            return index
    return None


def next_table_index(lines: list[str], start: int) -> int:
    for index in range(start, len(lines)):
        if lines[index].strip().startswith("["):
            return index
    return len(lines)


def format_datetime(value: datetime) -> str:
    if value.tzinfo is None:
        raise ValidationFailed("sync.ignore_transcripts_before must include a timezone")
    normalized = value.astimezone(UTC)
    return normalized.isoformat().replace("+00:00", "Z")
