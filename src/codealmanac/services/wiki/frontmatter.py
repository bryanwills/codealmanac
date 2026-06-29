import re
from datetime import UTC, date, datetime
from typing import Any

import frontmatter
from pydantic import BaseModel, ConfigDict, ValidationError, field_validator
from yaml import YAMLError

from codealmanac.services.wiki.models import ParsedFrontmatter


def parse_frontmatter(raw: str) -> ParsedFrontmatter:
    try:
        post = frontmatter.loads(raw)
        fields = FrontmatterFields.model_validate(post.metadata)
    except (YAMLError, ValueError, ValidationError):
        return ParsedFrontmatter(body=raw)
    return ParsedFrontmatter(
        page_id=fields.page_id,
        title=fields.title,
        summary=fields.summary,
        topics=fields.topics,
        files=fields.files,
        archived_at=fields.archived_at,
        superseded_by=fields.superseded_by,
        body=post.content,
    )


def strip_frontmatter(raw: str) -> str:
    return parse_frontmatter(raw).body


def first_h1(body: str) -> str | None:
    for line in body.splitlines()[:40]:
        match = re.match(r"^#\s+(.+?)\s*#*\s*$", line)
        if match is not None:
            return match.group(1)
    return None


class FrontmatterFields(BaseModel):
    model_config = ConfigDict(extra="ignore", frozen=True)

    page_id: str | None = None
    title: str | None = None
    summary: str | None = None
    topics: tuple[str, ...] = ()
    files: tuple[str, ...] = ()
    archived_at: int | None = None
    superseded_by: str | None = None

    @field_validator("page_id", "title", "summary", "superseded_by", mode="before")
    @classmethod
    def optional_text(cls, value: Any) -> str | None:
        if isinstance(value, str) and value.strip():
            return value.strip()
        return None

    @field_validator("topics", "files", mode="before")
    @classmethod
    def text_tuple(cls, value: Any) -> tuple[str, ...]:
        if not isinstance(value, list | tuple):
            return ()
        values: list[str] = []
        for item in value:
            if isinstance(item, str) and item.strip():
                values.append(item.strip())
        return tuple(values)

    @field_validator("archived_at", mode="before")
    @classmethod
    def epoch_seconds(cls, value: Any) -> int | None:
        if isinstance(value, datetime):
            return timestamp_seconds(value)
        if isinstance(value, date):
            return timestamp_seconds(
                datetime(value.year, value.month, value.day, tzinfo=UTC)
            )
        if isinstance(value, int | float):
            return int(value)
        if isinstance(value, str) and value.strip():
            try:
                parsed = datetime.fromisoformat(value.strip())
            except ValueError:
                return None
            return timestamp_seconds(parsed)
        return None


def timestamp_seconds(value: datetime) -> int:
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return int(value.timestamp())
