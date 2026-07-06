import os
from collections.abc import Iterator
from datetime import UTC, datetime
from pathlib import Path

from codealmanac.services.runs.models import (
    QueuedRun,
    RunAttachSnapshot,
    RunAttachUpdate,
    RunCancelResult,
    RunLogEvent,
    RunRecord,
    RunSpec,
)
from codealmanac.services.runs.requests import (
    AcquireRunWorkerLockRequest,
    AttachRunRequest,
    CancelRunRequest,
    FinishRunRequest,
    ListRunsRequest,
    MarkRunRunningRequest,
    NextQueuedRunRequest,
    QueueRunRequest,
    ReadRunLogRequest,
    ReadRunSpecRequest,
    RecordRunEventRequest,
    RecordRunHarnessTranscriptRequest,
    ShowRunRequest,
    StartRunRequest,
    StreamRunAttachRequest,
)
from codealmanac.services.runs.store import RunStore, RunWorkerLease
from codealmanac.services.runs.streaming import RunAttachStreamer
from codealmanac.services.workspaces.models import Workspace
from codealmanac.services.workspaces.requests import SelectWorkspaceRequest
from codealmanac.services.workspaces.runtime import WorkspaceRuntimePaths
from codealmanac.services.workspaces.service import WorkspacesService


class RunsService:
    def __init__(
        self,
        workspaces: WorkspacesService,
        store: RunStore,
        runtime_paths: WorkspaceRuntimePaths,
        streamer: RunAttachStreamer | None = None,
    ):
        self.workspaces = workspaces
        self.store = store
        self.runtime_paths = runtime_paths
        self.streamer = streamer or RunAttachStreamer(store)

    def start(self, request: StartRunRequest) -> RunRecord:
        workspace = self.resolve_workspace(request.cwd, request.wiki)
        return self.store.create(
            self.runtime_paths.repo_dir(workspace),
            workspace.workspace_id,
            request.operation,
            request.title,
        )

    def queue(self, request: QueueRunRequest) -> RunRecord:
        workspace = self.resolve_workspace(request.cwd, request.wiki)
        spec = request.spec.model_copy(
            update={"cwd": request.cwd, "wiki": request.wiki}
        )
        return self.store.queue(
            self.runtime_paths.repo_dir(workspace),
            workspace.workspace_id,
            spec,
            request.title,
        )

    def list(self, request: ListRunsRequest) -> tuple[RunRecord, ...]:
        workspace = self.resolve_workspace(request.cwd, request.wiki)
        return self.store.list(self.runtime_paths.repo_dir(workspace), request.limit)

    def show(self, request: ShowRunRequest) -> RunRecord:
        workspace = self.resolve_workspace(request.cwd, request.wiki)
        return self.store.read(self.runtime_paths.repo_dir(workspace), request.run_id)

    def read_spec(self, request: ReadRunSpecRequest) -> RunSpec | None:
        workspace = self.resolve_workspace(request.cwd, request.wiki)
        return self.store.read_spec(
            self.runtime_paths.repo_dir(workspace),
            request.run_id,
        )

    def next_queued(self, request: NextQueuedRunRequest) -> QueuedRun | None:
        workspace = self.resolve_workspace(request.cwd, request.wiki)
        return self.store.next_queued(self.runtime_paths.repo_dir(workspace))

    def acquire_worker_lock(
        self,
        request: AcquireRunWorkerLockRequest,
    ) -> RunWorkerLease | None:
        workspace = self.resolve_workspace(request.cwd, request.wiki)
        return self.store.acquire_worker_lock(
            self.runtime_paths.repo_dir(workspace),
            request.owner,
            request.pid or os.getpid(),
            request.now or datetime.now(UTC),
            request.stale_after,
        )

    def log(self, request: ReadRunLogRequest) -> tuple[RunLogEvent, ...]:
        workspace = self.resolve_workspace(request.cwd, request.wiki)
        return self.store.log(self.runtime_paths.repo_dir(workspace), request.run_id)

    def attach(self, request: AttachRunRequest) -> RunAttachSnapshot:
        workspace = self.resolve_workspace(request.cwd, request.wiki)
        return self.store.attach(self.runtime_paths.repo_dir(workspace), request.run_id)

    def stream_attach(
        self,
        request: StreamRunAttachRequest,
    ) -> Iterator[RunAttachUpdate]:
        workspace = self.resolve_workspace(request.cwd, request.wiki)
        return self.streamer.stream(
            self.runtime_paths.repo_dir(workspace),
            request.run_id,
            request.poll_interval_seconds,
        )

    def record_event(self, request: RecordRunEventRequest) -> RunLogEvent:
        workspace = self.resolve_workspace(request.cwd, request.wiki)
        return self.store.append(
            self.runtime_paths.repo_dir(workspace),
            request.run_id,
            request.kind,
            request.message,
            request.harness_event,
        )

    def mark_running(self, request: MarkRunRunningRequest) -> RunRecord:
        workspace = self.resolve_workspace(request.cwd, request.wiki)
        return self.store.mark_running(
            self.runtime_paths.repo_dir(workspace),
            request.run_id,
        )

    def record_harness_transcript(
        self,
        request: RecordRunHarnessTranscriptRequest,
    ) -> RunRecord:
        workspace = self.resolve_workspace(request.cwd, request.wiki)
        return self.store.record_harness_transcript(
            self.runtime_paths.repo_dir(workspace),
            request.run_id,
            request.transcript,
        )

    def finish(self, request: FinishRunRequest) -> RunRecord:
        workspace = self.resolve_workspace(request.cwd, request.wiki)
        return self.store.finish(
            self.runtime_paths.repo_dir(workspace),
            request.run_id,
            request.status,
            request.summary,
            request.error,
        )

    def cancel(self, request: CancelRunRequest) -> RunCancelResult:
        workspace = self.resolve_workspace(request.cwd, request.wiki)
        return self.store.cancel(self.runtime_paths.repo_dir(workspace), request.run_id)

    def resolve_workspace(self, cwd: Path, wiki: str | None) -> Workspace:
        if wiki is None:
            return self.workspaces.resolve(cwd)
        return self.workspaces.select(
            SelectWorkspaceRequest(selector=wiki, base_path=cwd)
        )
