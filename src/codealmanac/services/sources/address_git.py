from codealmanac.core.errors import ValidationFailed
from codealmanac.services.sources.address_hints import (
    GIT_DIFF_PROMPT_HINT,
    GIT_RANGE_PROMPT_HINT,
)
from codealmanac.services.sources.models import (
    SourceBrief,
    SourceKind,
    SourceProvenanceKind,
    SourceRef,
)


def resolve_git_range(raw: str) -> SourceBrief:
    revision_range = raw.removeprefix("git:range:").strip()
    if not revision_range:
        raise ValidationFailed("git range source requires a revision range")
    ref = SourceRef(
        raw=raw,
        kind=SourceKind.GIT_RANGE,
        identity=f"git.range:{revision_range}",
        revision_range=revision_range,
    )
    return SourceBrief(
        ref=ref,
        title=f"Git range {revision_range}",
        provenance_kind=SourceProvenanceKind.GIT,
        prompt_hint=GIT_RANGE_PROMPT_HINT,
    )


def resolve_git_diff(raw: str) -> SourceBrief:
    target = raw.removeprefix("git:diff").removeprefix(":").strip() or "working-tree"
    ref = SourceRef(
        raw=raw,
        kind=SourceKind.GIT_DIFF,
        identity=f"git.diff:{target}",
        revision_range=target,
    )
    return SourceBrief(
        ref=ref,
        title=f"Git diff {target}",
        provenance_kind=SourceProvenanceKind.GIT,
        prompt_hint=GIT_DIFF_PROMPT_HINT,
    )
