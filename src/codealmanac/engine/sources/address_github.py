from urllib.parse import urlsplit

from codealmanac.core.errors import ValidationFailed
from codealmanac.engine.sources.address_hints import (
    ISSUE_PROMPT_HINT,
    PULL_REQUEST_PROMPT_HINT,
)
from codealmanac.engine.sources.address_numbers import parse_positive_int
from codealmanac.engine.sources.models import (
    SourceBrief,
    SourceKind,
    SourceProvenanceKind,
    SourceRef,
)


def resolve_github_shorthand(raw: str) -> SourceBrief:
    parts = raw.split(":")
    if len(parts) != 3:
        raise ValidationFailed(f"invalid GitHub source address: {raw}")
    _, source_type, number_text = parts
    number = parse_positive_int(number_text, raw)
    if source_type == "pr":
        ref = SourceRef(
            raw=raw,
            kind=SourceKind.GITHUB_PULL_REQUEST,
            identity=f"github.pull_request:{number}",
            number=number,
        )
        return SourceBrief(
            ref=ref,
            title=f"GitHub pull request #{number}",
            provenance_kind=SourceProvenanceKind.PR,
            prompt_hint=PULL_REQUEST_PROMPT_HINT,
        )
    if source_type == "issue":
        ref = SourceRef(
            raw=raw,
            kind=SourceKind.GITHUB_ISSUE,
            identity=f"github.issue:{number}",
            number=number,
        )
        return SourceBrief(
            ref=ref,
            title=f"GitHub issue #{number}",
            provenance_kind=SourceProvenanceKind.ISSUE,
            prompt_hint=ISSUE_PROMPT_HINT,
        )
    raise ValidationFailed(f"unsupported GitHub source address: {raw}")


def parse_github_url(raw: str, url: str) -> SourceBrief | None:
    parsed = urlsplit(url)
    if parsed.netloc.casefold() != "github.com":
        return None
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) < 4:
        return None
    owner, repo, source_type, number_text = parts[:4]
    if source_type not in {"pull", "issues"}:
        return None
    number = parse_positive_int(number_text, raw)
    repository = f"{owner}/{repo}"
    if source_type == "pull":
        url = f"https://github.com/{repository}/pull/{number}"
        ref = SourceRef(
            raw=raw,
            kind=SourceKind.GITHUB_PULL_REQUEST,
            identity=f"github.pull_request:{repository}#{number}",
            url=url,
            repository=repository,
            number=number,
        )
        return SourceBrief(
            ref=ref,
            title=f"{repository} pull request #{number}",
            provenance_kind=SourceProvenanceKind.PR,
            prompt_hint=PULL_REQUEST_PROMPT_HINT,
        )
    url = f"https://github.com/{repository}/issues/{number}"
    ref = SourceRef(
        raw=raw,
        kind=SourceKind.GITHUB_ISSUE,
        identity=f"github.issue:{repository}#{number}",
        url=url,
        repository=repository,
        number=number,
    )
    return SourceBrief(
        ref=ref,
        title=f"{repository} issue #{number}",
        provenance_kind=SourceProvenanceKind.ISSUE,
        prompt_hint=ISSUE_PROMPT_HINT,
    )
