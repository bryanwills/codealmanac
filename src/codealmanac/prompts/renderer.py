from importlib.resources import files

from codealmanac.prompts.models import PromptName
from codealmanac.prompts.requests import RenderPromptRequest

PROMPTS_PACKAGE = "codealmanac.prompts"


class PromptRenderer:
    def render(self, request: RenderPromptRequest) -> str:
        sections = [prompt_text(section) for section in request.sections]
        sections.extend(request.context)
        return join_prompt_sections(tuple(sections))


def prompt_text(name: PromptName) -> str:
    resource = files(PROMPTS_PACKAGE).joinpath(*name.value.split("/"))
    return resource.read_text(encoding="utf-8").strip()


def join_prompt_sections(sections: tuple[str, ...]) -> str:
    return "\n\n---\n\n".join(
        section.strip() for section in sections if section.strip()
    )
