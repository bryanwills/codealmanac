from pathlib import Path

from codealmanac.core.errors import ValidationFailed
from codealmanac.services.control.models import ControlRunEventKind, ControlRunStatus
from codealmanac.services.control.requests import (
    AppendControlRunEventRequest,
    ClaimNextTriggerRequest,
    GetBranchRequest,
    GetRepositoryRequest,
    UpdateControlRunRequest,
)
from codealmanac.services.control.service import ControlService
from codealmanac.services.engine_runs.requests import PrepareEngineRunRequest
from codealmanac.services.engine_runs.service import EngineRunsService
from codealmanac.services.worker_workspaces.requests import (
    PrepareWorkerWorkspaceRequest,
)
from codealmanac.services.worker_workspaces.service import WorkerWorkspacesService
from codealmanac.workflows.local_runs.models import LocalRunPreparationResult
from codealmanac.workflows.local_runs.requests import PrepareNextLocalRunRequest


class LocalRunPreparationWorkflow:
    def __init__(
        self,
        control: ControlService,
        worker_workspaces: WorkerWorkspacesService,
        engine_runs: EngineRunsService,
    ):
        self.control = control
        self.worker_workspaces = worker_workspaces
        self.engine_runs = engine_runs

    def prepare_next(
        self,
        request: PrepareNextLocalRunRequest | None = None,
    ) -> LocalRunPreparationResult:
        resolved = request or PrepareNextLocalRunRequest()
        claim = self.control.claim_next_trigger(
            ClaimNextTriggerRequest(
                repository_id=resolved.repository_id,
                branch_id=resolved.branch_id,
                operation=resolved.operation,
            )
        )
        if not claim.claimed or claim.run is None or claim.trigger is None:
            return LocalRunPreparationResult(
                prepared=False,
                reason=claim.reason or "no_pending_trigger",
            )
        try:
            repository = self.control.get_repository(
                GetRepositoryRequest(repository_id=claim.run.repository_id)
            )
            branch = self.control.get_branch(
                GetBranchRequest(branch_id=claim.run.branch_id)
            )
            if repository.local_root_path is None:
                raise ValidationFailed("repository local_root_path is required")
            if claim.run.expected_head_sha is None:
                raise ValidationFailed("run expected_head_sha is required")
            worker_workspace = self.worker_workspaces.prepare(
                PrepareWorkerWorkspaceRequest(
                    run_id=claim.run.id,
                    repository_root_path=repository.local_root_path,
                    expected_head_sha=claim.run.expected_head_sha,
                )
            )
            source_ref = path_ref(worker_workspace.paths.sources_path)
            engine_run = self.engine_runs.prepare(
                PrepareEngineRunRequest(
                    run_id=claim.run.id,
                    repository_id=repository.id,
                    branch_id=branch.id,
                    repository_full_name=repository.full_name,
                    branch_name=branch.name,
                    expected_head_sha=claim.run.expected_head_sha,
                    repo_path=worker_workspace.paths.repo_path,
                    almanac_root=repository.almanac_root,
                    sources_path=worker_workspace.paths.sources_path,
                    source_bundle_ref=source_ref,
                )
            )
            run = self.control.update_run(
                UpdateControlRunRequest(
                    run_id=claim.run.id,
                    source_bundle_ref=source_ref,
                    request_ref=path_ref(engine_run.paths.request_path),
                )
            )
            self.control.append_run_event(
                AppendControlRunEventRequest(
                    run_id=run.id,
                    kind=ControlRunEventKind.STATUS,
                    message="prepared local worker workspace",
                    artifact_ref=run.request_ref,
                )
            )
            return LocalRunPreparationResult(
                prepared=True,
                repository=repository,
                branch=branch,
                trigger=claim.trigger,
                run=run,
                worker_workspace=worker_workspace,
                engine_run=engine_run,
            )
        except Exception as error:
            message = first_line(str(error)) or error.__class__.__name__
            run = self.control.update_run(
                UpdateControlRunRequest(
                    run_id=claim.run.id,
                    status=ControlRunStatus.FAILED,
                    error=message,
                )
            )
            self.control.append_run_event(
                AppendControlRunEventRequest(
                    run_id=run.id,
                    kind=ControlRunEventKind.ERROR,
                    message=message,
                )
            )
            return LocalRunPreparationResult(
                prepared=False,
                reason="preparation_failed",
                trigger=claim.trigger,
                run=run,
            )


def path_ref(path: Path) -> str:
    return path.resolve(strict=False).as_uri()


def first_line(value: str) -> str:
    for line in value.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return ""
