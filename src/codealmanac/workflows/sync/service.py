from datetime import UTC, datetime

from codealmanac.services.repositories.service import RepositoriesService
from codealmanac.services.sources.service import SourcesService
from codealmanac.workflows.run_queue.service import RunQueue
from codealmanac.workflows.sync.evaluation import SyncEvaluator
from codealmanac.workflows.sync.execution import SyncRunExecutor
from codealmanac.workflows.sync.models import (
    SyncEvaluation,
    SyncMode,
    SyncSummary,
)
from codealmanac.workflows.sync.requests import (
    RunSyncRequest,
    RunSyncStatusRequest,
    SyncSelectionRequest,
)
from codealmanac.workflows.sync.store import SyncStateStore


class SyncWorkflow:
    def __init__(
        self,
        repositories: RepositoriesService,
        sources: SourcesService,
        queue: RunQueue,
        state_store: SyncStateStore,
    ):
        self.evaluator = SyncEvaluator(
            repositories=repositories,
            sources=sources,
            state_store=state_store,
        )
        self.executor = SyncRunExecutor(
            queue=queue,
            state_store=state_store,
        )

    def status(self, request: RunSyncStatusRequest) -> SyncSummary:
        return self.evaluate(request, SyncMode.STATUS).summary

    def run(self, request: RunSyncRequest) -> SyncSummary:
        now = request.now or datetime.now(UTC)
        evaluation = self.evaluate(request, SyncMode.SYNC, now=now)
        effects = self.executor.run(request, evaluation, now)
        return evaluation.summary.model_copy(
            update={
                "started": effects.started,
                "skipped": effects.skipped,
                "completed_at": now,
            }
        )

    def evaluate(
        self,
        request: SyncSelectionRequest,
        mode: SyncMode,
        now: datetime | None = None,
    ) -> SyncEvaluation:
        return self.evaluator.evaluate(request, mode, now)
