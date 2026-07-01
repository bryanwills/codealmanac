from urllib.parse import urlsplit

from pydantic import AnyHttpUrl, TypeAdapter, ValidationError

from codealmanac.core.errors import ValidationFailed
from codealmanac.services.sources.address_github import parse_github_url
from codealmanac.services.sources.address_hints import WEB_PROMPT_HINT
from codealmanac.services.sources.models import (
    SourceBrief,
    SourceKind,
    SourceProvenanceKind,
    SourceRef,
)

HTTP_URL_ADAPTER = TypeAdapter(AnyHttpUrl)


def resolve_url(raw: str) -> SourceBrief:
    url = normalize_http_url(raw)
    github = parse_github_url(raw, url)
    if github is not None:
        return github
    ref = SourceRef(
        raw=raw,
        kind=SourceKind.WEB_URL,
        identity=url,
        url=url,
    )
    return SourceBrief(
        ref=ref,
        title=url,
        provenance_kind=SourceProvenanceKind.URL,
        prompt_hint=WEB_PROMPT_HINT,
    )


def normalize_http_url(raw: str) -> str:
    parsed = urlsplit(raw)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValidationFailed(f"invalid URL source address: {raw}")
    try:
        return str(HTTP_URL_ADAPTER.validate_python(raw))
    except ValidationError as error:
        raise ValidationFailed(f"invalid URL source address: {raw}") from error
