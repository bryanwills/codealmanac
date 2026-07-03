from pathlib import Path
from typing import Protocol

from codealmanac.local.setup.models import LocalRepositoryState


class LocalRepositoryProbe(Protocol):
    def read(self, cwd: Path) -> LocalRepositoryState:
        """Return local Git checkout and provider identity for setup."""
