from typing import Protocol

from codealmanac.runs.ledger.models import RunWorkerSpawnResult
from codealmanac.runs.ledger.requests import SpawnRunWorkerRequest


class RunWorkerSpawner(Protocol):
    def spawn(self, request: SpawnRunWorkerRequest) -> RunWorkerSpawnResult:
        """Start a detached process that drains queued runs for one wiki."""
