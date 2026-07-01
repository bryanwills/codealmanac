from pathlib import Path
from urllib.parse import urlsplit

from codealmanac.services.sources.address_git import (
    resolve_git_diff,
    resolve_git_range,
)
from codealmanac.services.sources.address_github import resolve_github_shorthand
from codealmanac.services.sources.address_path import resolve_path
from codealmanac.services.sources.address_transcript import resolve_transcript
from codealmanac.services.sources.address_web import resolve_url
from codealmanac.services.sources.models import SourceAddress, SourceBrief


def resolve_address(address: SourceAddress, cwd: Path) -> SourceBrief:
    raw = address.raw
    if raw.startswith("github:"):
        return resolve_github_shorthand(raw)
    if raw.startswith("git:range:"):
        return resolve_git_range(raw)
    if raw == "git:diff" or raw.startswith("git:diff:"):
        return resolve_git_diff(raw)
    if raw.startswith("transcript:"):
        return resolve_transcript(raw)
    parsed = urlsplit(raw)
    if parsed.scheme in {"http", "https"}:
        return resolve_url(raw)
    return resolve_path(raw, cwd)
