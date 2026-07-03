from typing import Protocol

from codealmanac.local.runs.worker.requests import SpawnLocalWorkerRequest
from codealmanac.services.runs.models import RunWorkerSpawnResult


class LocalWorkerSpawner(Protocol):
    def spawn(self, request: SpawnLocalWorkerRequest) -> RunWorkerSpawnResult:
        """Start one detached local worker process for a repo/branch trigger."""
