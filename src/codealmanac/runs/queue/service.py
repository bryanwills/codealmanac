from pathlib import Path

from codealmanac.runs.ledger.models import (
    QueuedRun,
    RunKind,
    RunQueueDrainResult,
    RunRecord,
    RunSpec,
    RunStatus,
)
from codealmanac.runs.ledger.ports import RunWorkerSpawner
from codealmanac.runs.ledger.requests import (
    AcquireRunWorkerLockRequest,
    FinishRunRequest,
    NextQueuedRunRequest,
    QueueRunRequest,
    SpawnRunWorkerRequest,
)
from codealmanac.runs.ledger.service import RunLedgerService
from codealmanac.runs.queue.models import RunQueueStartResult
from codealmanac.runs.queue.requests import DrainRunQueueRequest
from codealmanac.workflows.garden.requests import (
    RunGardenRequest,
    RunGardenWithRunRequest,
)
from codealmanac.workflows.garden.service import GardenWorkflow
from codealmanac.workflows.ingest.requests import (
    RunIngestRequest,
    RunIngestWithRunRequest,
)
from codealmanac.workflows.ingest.service import IngestWorkflow
from codealmanac.workflows.init.requests import (
    RunInitRequest,
    RunInitWithRunRequest,
)
from codealmanac.workflows.init.service import InitWorkflow


class RunQueueWorkflow:
    def __init__(
        self,
        runs: RunLedgerService,
        init: InitWorkflow,
        ingest: IngestWorkflow,
        garden: GardenWorkflow,
        spawner: RunWorkerSpawner,
    ):
        self.runs = runs
        self.init = init
        self.ingest = ingest
        self.garden = garden
        self.spawner = spawner

    def queue_init(self, request: RunInitRequest) -> RunRecord:
        prepared = self.init.prepare(request, enforce_force=True)
        return self.runs.queue(
            QueueRunRequest(
                cwd=prepared.workspace.root_path,
                title=request.title or "Initialize wiki",
                spec=RunSpec(
                    kind=RunKind.INIT,
                    cwd=prepared.workspace.root_path,
                    harness=request.harness,
                    almanac_root=prepared.workspace.almanac_root,
                    workspace_name=prepared.workspace.name,
                    description=prepared.workspace.description,
                    title=request.title,
                    guidance=request.guidance,
                    force=request.force,
                ),
            )
        )

    def start_init_background(self, request: RunInitRequest) -> RunQueueStartResult:
        run = self.queue_init(request)
        worker = self.spawn_worker(request.path, None)
        return RunQueueStartResult(run=run, worker=worker)

    def queue_ingest(self, request: RunIngestRequest) -> RunRecord:
        return self.runs.queue(
            QueueRunRequest(
                cwd=request.cwd,
                wiki=request.wiki,
                title=request.title or default_ingest_title(request.inputs),
                spec=RunSpec(
                    kind=RunKind.INGEST,
                    cwd=request.cwd,
                    wiki=request.wiki,
                    harness=request.harness,
                    inputs=request.inputs,
                    title=request.title,
                    guidance=request.guidance,
                ),
            )
        )

    def start_ingest_background(self, request: RunIngestRequest) -> RunQueueStartResult:
        run = self.queue_ingest(request)
        worker = self.spawn_worker(request.cwd, request.wiki)
        return RunQueueStartResult(run=run, worker=worker)

    def queue_garden(self, request: RunGardenRequest) -> RunRecord:
        return self.runs.queue(
            QueueRunRequest(
                cwd=request.cwd,
                wiki=request.wiki,
                title=request.title or "Garden wiki",
                spec=RunSpec(
                    kind=RunKind.GARDEN,
                    cwd=request.cwd,
                    wiki=request.wiki,
                    harness=request.harness,
                    title=request.title,
                    guidance=request.guidance,
                ),
            )
        )

    def start_garden_background(self, request: RunGardenRequest) -> RunQueueStartResult:
        run = self.queue_garden(request)
        worker = self.spawn_worker(request.cwd, request.wiki)
        return RunQueueStartResult(run=run, worker=worker)

    def spawn_worker(self, cwd: Path, wiki: str | None):
        return self.spawner.spawn(SpawnRunWorkerRequest(cwd=cwd, wiki=wiki))

    def drain(self, request: DrainRunQueueRequest) -> RunQueueDrainResult:
        lease = self.runs.acquire_worker_lock(
            AcquireRunWorkerLockRequest(
                cwd=request.cwd,
                wiki=request.wiki,
                owner=request.owner,
                pid=request.pid,
                now=request.now,
                stale_after=request.stale_after,
            )
        )
        if lease is None:
            return RunQueueDrainResult(lock_acquired=False)
        processed: list[RunRecord] = []
        try:
            while request.max_runs is None or len(processed) < request.max_runs:
                queued = self.runs.next_queued(
                    NextQueuedRunRequest(cwd=request.cwd, wiki=request.wiki)
                )
                if queued is None:
                    break
                processed.append(self.run_one(queued, request))
            return RunQueueDrainResult(
                lock_acquired=True,
                processed=tuple(processed),
            )
        finally:
            lease.release()

    def run_one(
        self,
        queued: QueuedRun,
        request: DrainRunQueueRequest,
    ) -> RunRecord:
        spec = queued.spec
        if spec is None:
            return self.runs.finish(
                FinishRunRequest(
                    cwd=request.cwd,
                    wiki=request.wiki,
                    run_id=queued.record.run_id,
                    status=RunStatus.FAILED,
                    error="queued run is missing its durable spec",
                )
            )
        if spec.kind == RunKind.INIT:
            result = self.init.run_with_run(
                RunInitWithRunRequest(
                    path=spec.cwd,
                    harness=spec.harness,
                    almanac_root=spec.almanac_root,
                    name=spec.workspace_name,
                    description=spec.description,
                    title=spec.title,
                    guidance=spec.guidance,
                    force=spec.force,
                    run_id=queued.record.run_id,
                )
            )
            return result.run
        if spec.kind == RunKind.INGEST:
            result = self.ingest.run_with_run(
                RunIngestWithRunRequest(
                    cwd=spec.cwd,
                    wiki=spec.wiki,
                    inputs=spec.inputs,
                    harness=spec.harness,
                    title=spec.title,
                    guidance=spec.guidance,
                    run_id=queued.record.run_id,
                )
            )
            return result.run
        if spec.kind == RunKind.GARDEN:
            result = self.garden.run_with_run(
                RunGardenWithRunRequest(
                    cwd=spec.cwd,
                    wiki=spec.wiki,
                    harness=spec.harness,
                    title=spec.title,
                    guidance=spec.guidance,
                    run_id=queued.record.run_id,
                )
            )
            return result.run
        return self.runs.finish(
            FinishRunRequest(
                cwd=request.cwd,
                wiki=request.wiki,
                run_id=queued.record.run_id,
                status=RunStatus.FAILED,
                error=f"unsupported queued run kind: {spec.kind.value}",
            )
        )


def default_ingest_title(inputs: tuple[str, ...]) -> str:
    if len(inputs) == 1:
        return f"Ingest {inputs[0]}"
    return f"Ingest {len(inputs)} sources"
