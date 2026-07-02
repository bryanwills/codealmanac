from pathlib import Path

from codealmanac.core.models import CodeAlmanacModel


class ReadLocalStatusRequest(CodeAlmanacModel):
    cwd: Path
