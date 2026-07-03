from hashlib import sha256
from pathlib import Path

from codealmanac.core.paths import normalize_path
from codealmanac.engine.sources.address_hints import (
    DIRECTORY_PROMPT_HINT,
    FILE_PROMPT_HINT,
    MISSING_PATH_PROMPT_HINT,
)
from codealmanac.engine.sources.models import (
    SourceBrief,
    SourceKind,
    SourceProvenanceKind,
    SourceRef,
)


def resolve_path(raw: str, cwd: Path) -> SourceBrief:
    path = resolve_user_path(raw, cwd)
    if path.is_dir():
        kind = SourceKind.PATH_DIRECTORY
        provenance_kind = SourceProvenanceKind.DIRECTORY
        title = f"Directory {path}"
        prompt_hint = DIRECTORY_PROMPT_HINT
        fingerprint = None
    elif path.is_file():
        kind = SourceKind.PATH_FILE
        provenance_kind = SourceProvenanceKind.FILE
        title = f"File {path}"
        prompt_hint = FILE_PROMPT_HINT
        fingerprint = file_fingerprint(path)
    else:
        kind = SourceKind.PATH_UNKNOWN
        provenance_kind = SourceProvenanceKind.MISSING_PATH
        title = f"Missing path {path}"
        prompt_hint = MISSING_PATH_PROMPT_HINT
        fingerprint = None
    ref = SourceRef(
        raw=raw,
        kind=kind,
        identity=f"{kind.value}:{path}",
        path=path,
        exists=path.exists(),
        fingerprint=fingerprint,
    )
    return SourceBrief(
        ref=ref,
        title=title,
        provenance_kind=provenance_kind,
        prompt_hint=prompt_hint,
    )


def resolve_user_path(raw: str, cwd: Path) -> Path:
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = cwd / path
    return normalize_path(path)


def file_fingerprint(path: Path) -> str | None:
    try:
        return sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None
