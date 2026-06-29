from pydantic import field_validator

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.core.text import required_text
from codealmanac.prompts.models import PromptName


class RenderPromptRequest(CodeAlmanacModel):
    sections: tuple[PromptName, ...]
    context: tuple[str, ...] = ()

    @field_validator("sections")
    @classmethod
    def require_sections(cls, value: tuple[PromptName, ...]) -> tuple[PromptName, ...]:
        if len(value) == 0:
            raise ValueError("at least one prompt section is required")
        return value

    @field_validator("context")
    @classmethod
    def require_context_text(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        return tuple(required_text(item, "prompt context") for item in value)
