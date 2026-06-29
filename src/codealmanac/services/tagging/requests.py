from pathlib import Path
from typing import Any

from pydantic import field_validator

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.core.slug import to_kebab_case
from codealmanac.core.text import required_text


class TagPageRequest(CodeAlmanacModel):
    cwd: Path
    slug: str
    topics: tuple[str, ...]
    wiki: str | None = None

    @field_validator("slug")
    @classmethod
    def require_slug(cls, value: str) -> str:
        return required_text(value, "page")

    @field_validator("topics", mode="before")
    @classmethod
    def canonical_topics(cls, value: Any) -> tuple[str, ...]:
        if not isinstance(value, list | tuple):
            raise ValueError("topics must not be empty")
        topics = tuple(dict.fromkeys(to_kebab_case(str(item)) for item in value))
        topics = tuple(topic for topic in topics if topic)
        if not topics:
            raise ValueError("topics must not be empty")
        return topics


class UntagPageRequest(TagPageRequest):
    pass
