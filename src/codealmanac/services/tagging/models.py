from codealmanac.core.models import CodeAlmanacModel


class TaggingResult(CodeAlmanacModel):
    slug: str
    topics_before: tuple[str, ...]
    topics_after: tuple[str, ...]
    changed_topics: tuple[str, ...]
