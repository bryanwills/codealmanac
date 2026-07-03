from contextlib import suppress

from codealmanac.engine.worker_workspaces.requests import ReadWorkerWorkspaceRequest
from codealmanac.engine.worker_workspaces.service import WorkerWorkspacesService
from codealmanac.services.control.models import (
    ControlDeliveryMode,
    ControlRunEventKind,
    ControlRunRecord,
    ControlRunStatus,
)
from codealmanac.services.control.requests import (
    AppendControlRunEventRequest,
    GetBranchRequest,
    GetControlRunRequest,
    GetRepositoryRequest,
    UpdateControlRunRequest,
)
from codealmanac.services.control.service import ControlService
from codealmanac.services.deliveries.models import DeliveryRecord, DeliveryStatus
from codealmanac.services.deliveries.requests import (
    CreateDeliveryRequest,
    UpdateDeliveryRequest,
)
from codealmanac.services.deliveries.service import DeliveriesService
from codealmanac.services.engine_runs.models import (
    COMMIT_SUBJECT_PREFIX,
    EngineRunResult,
    EngineRunStatus,
)
from codealmanac.services.engine_runs.requests import ReadEngineRunRequest
from codealmanac.services.engine_runs.service import EngineRunsService
from codealmanac.workflows.local_delivery.models import LocalDeliveryResult
from codealmanac.workflows.local_delivery.ports import LocalGitDeliveryManager
from codealmanac.workflows.local_delivery.requests import DeliverLocalRunRequest
from codealmanac.workflows.local_runs.refs import first_line


class LocalDeliveryWorkflow:
    def __init__(
        self,
        control: ControlService,
        deliveries: DeliveriesService,
        engine_runs: EngineRunsService,
        worker_workspaces: WorkerWorkspacesService,
        git_delivery: LocalGitDeliveryManager,
    ):
        self.control = control
        self.deliveries = deliveries
        self.engine_runs = engine_runs
        self.worker_workspaces = worker_workspaces
        self.git_delivery = git_delivery

    def deliver(self, request: DeliverLocalRunRequest) -> LocalDeliveryResult:
        run = self.control.get_run(GetControlRunRequest(run_id=request.run_id))
        repository = self.control.get_repository(
            GetRepositoryRequest(repository_id=run.repository_id)
        )
        branch = self.control.get_branch(GetBranchRequest(branch_id=run.branch_id))
        engine = self.engine_runs.read_result(ReadEngineRunRequest(run_id=run.id))
        delivery = self.deliveries.create(
            CreateDeliveryRequest(
                run_id=run.id,
                mode=branch.delivery_mode,
                target_ref=branch.name,
                expected_head_sha=run.expected_head_sha,
            )
        )
        try:
            if repository.local_root_path is None:
                raise ValueError("repository local_root_path is required")
            if run.expected_head_sha is None:
                raise ValueError("run expected_head_sha is required")
            if branch.delivery_mode is ControlDeliveryMode.PR:
                raise ValueError(
                    f"unsupported local delivery mode: {branch.delivery_mode.value}"
                )
            if engine.status is not EngineRunStatus.SUCCEEDED:
                return self.skip_failed_engine(run, delivery, engine)
            head = self.git_delivery.read_head(repository.local_root_path)
            if (
                head.branch_name != branch.name
                or head.head_sha != run.expected_head_sha
            ):
                return self.mark_stale(
                    run,
                    delivery,
                    f"branch advanced to {head.head_sha}; delivery skipped",
                    head.head_sha,
                )
            workspace = self.worker_workspaces.paths(
                ReadWorkerWorkspaceRequest(run_id=run.id)
            )
            patch = self.git_delivery.collect_patch(
                workspace.repo_path,
                repository.almanac_root,
            )
            if patch.empty:
                updated = self.finish_run(run, engine)
                skipped = self.deliveries.update(
                    UpdateDeliveryRequest(
                        delivery_id=delivery.id,
                        status=DeliveryStatus.SKIPPED,
                        summary="no wiki changes to deliver",
                    )
                )
                self.append_status(run.id, "delivery skipped: no wiki changes")
                return LocalDeliveryResult(
                    delivered=False,
                    reason="no_wiki_changes",
                    run=updated,
                    delivery=skipped,
                )
            if branch.delivery_mode is ControlDeliveryMode.WORKING_TREE:
                self.git_delivery.apply_patch_to_working_tree(
                    repository.local_root_path,
                    repository.almanac_root,
                    patch.patch_text,
                )
                delivered = self.deliveries.update(
                    UpdateDeliveryRequest(
                        delivery_id=delivery.id,
                        status=DeliveryStatus.SUCCEEDED,
                        delivered_head_sha=head.head_sha,
                        summary=engine.summary,
                    )
                )
                updated = self.finish_run(run, engine)
                self.append_status(run.id, "delivered local working tree changes")
                return LocalDeliveryResult(
                    delivered=True,
                    run=updated,
                    delivery=delivered,
                )
            commit = self.git_delivery.apply_patch_and_commit(
                repository.local_root_path,
                repository.almanac_root,
                patch.patch_text,
                commit_subject(engine),
                engine.commit_body,
            )
            delivered = self.deliveries.update(
                UpdateDeliveryRequest(
                    delivery_id=delivery.id,
                    status=DeliveryStatus.SUCCEEDED,
                    delivered_head_sha=commit.commit_sha,
                    commit_sha=commit.commit_sha,
                    summary=engine.summary,
                )
            )
            updated = self.finish_run(run, engine)
            self.append_status(run.id, f"delivered local commit {commit.commit_sha}")
            return LocalDeliveryResult(
                delivered=True,
                run=updated,
                delivery=delivered,
                commit_sha=commit.commit_sha,
            )
        except Exception as error:
            message = first_line(str(error)) or error.__class__.__name__
            failed = self.deliveries.update(
                UpdateDeliveryRequest(
                    delivery_id=delivery.id,
                    status=DeliveryStatus.FAILED,
                    error=message,
                )
            )
            updated = self.control.update_run(
                UpdateControlRunRequest(
                    run_id=run.id,
                    status=ControlRunStatus.FAILED,
                    error=message,
                )
            )
            self.append_error(run.id, message)
            return LocalDeliveryResult(
                delivered=False,
                reason="delivery_failed",
                run=updated,
                delivery=failed,
            )

    def skip_failed_engine(
        self,
        run: ControlRunRecord,
        delivery: DeliveryRecord,
        engine: EngineRunResult,
    ) -> LocalDeliveryResult:
        message = f"engine result is {engine.status.value}; delivery skipped"
        status = ControlRunStatus.FAILED
        if engine.status is EngineRunStatus.STALE:
            status = ControlRunStatus.STALE
        if engine.status is EngineRunStatus.CANCELLED:
            status = ControlRunStatus.CANCELLED
        updated = self.control.update_run(
            UpdateControlRunRequest(
                run_id=run.id,
                status=status,
                error=engine.error or message,
            )
        )
        skipped = self.deliveries.update(
            UpdateDeliveryRequest(
                delivery_id=delivery.id,
                status=DeliveryStatus.SKIPPED,
                error=message,
            )
        )
        self.append_status(run.id, message)
        return LocalDeliveryResult(
            delivered=False,
            reason="engine_not_succeeded",
            run=updated,
            delivery=skipped,
        )

    def mark_stale(
        self,
        run: ControlRunRecord,
        delivery: DeliveryRecord,
        message: str,
        head_sha: str,
    ) -> LocalDeliveryResult:
        updated = self.control.update_run(
            UpdateControlRunRequest(
                run_id=run.id,
                status=ControlRunStatus.STALE,
                error=message,
            )
        )
        skipped = self.deliveries.update(
            UpdateDeliveryRequest(
                delivery_id=delivery.id,
                status=DeliveryStatus.SKIPPED,
                delivered_head_sha=head_sha,
                error=message,
            )
        )
        self.append_status(run.id, message)
        return LocalDeliveryResult(
            delivered=False,
            reason="expected_head_changed",
            run=updated,
            delivery=skipped,
        )

    def finish_run(
        self,
        run: ControlRunRecord,
        engine: EngineRunResult,
    ) -> ControlRunRecord:
        return self.control.update_run(
            UpdateControlRunRequest(
                run_id=run.id,
                status=ControlRunStatus.SUCCEEDED,
                summary=engine.summary,
                commit_subject=engine.commit_subject,
                commit_body=engine.commit_body,
            )
        )

    def append_status(self, run_id: str, message: str) -> None:
        with suppress(Exception):
            self.control.append_run_event(
                AppendControlRunEventRequest(
                    run_id=run_id,
                    kind=ControlRunEventKind.STATUS,
                    message=message,
                )
            )

    def append_error(self, run_id: str, message: str) -> None:
        with suppress(Exception):
            self.control.append_run_event(
                AppendControlRunEventRequest(
                    run_id=run_id,
                    kind=ControlRunEventKind.ERROR,
                    message=message,
                )
            )


def commit_subject(engine: EngineRunResult) -> str:
    return engine.commit_subject or f"{COMMIT_SUBJECT_PREFIX} update wiki"
