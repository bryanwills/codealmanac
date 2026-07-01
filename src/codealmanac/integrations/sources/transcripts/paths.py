from pathlib import Path

from codealmanac.core.paths import normalize_path
from codealmanac.services.sources.models import SourceRef


def transcript_path(cwd: Path, ref: SourceRef) -> Path | None:
    if ref.transcript is None or ref.transcript.strip() == "":
        return None
    path = Path(ref.transcript).expanduser()
    if not path.is_absolute():
        path = cwd / path
    return normalize_path(path)
