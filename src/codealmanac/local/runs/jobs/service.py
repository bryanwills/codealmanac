from codealmanac.local.control.requests import (
    GetBranchRequest,
    GetControlRunRequest,
    GetRepositoryRequest,
    ListControlRunEventsRequest,
    ListControlRunsRequest,
)
from codealmanac.local.control.service import ControlService
from codealmanac.local.runs.jobs.models import (
    LocalJobLogsResult,
    LocalJobSummary,
)
from codealmanac.local.runs.jobs.requests import (
    ListLocalJobsRequest,
    ReadLocalJobLogsRequest,
    ShowLocalJobRequest,
)


class LocalJobsWorkflow:
    def __init__(self, control: ControlService):
        self.control = control

    def list(self, request: ListLocalJobsRequest) -> tuple[LocalJobSummary, ...]:
        runs = self.control.list_runs(
            ListControlRunsRequest(
                repository_id=request.repository_id,
                branch_id=request.branch_id,
                statuses=request.statuses,
                limit=request.limit,
            )
        )
        return tuple(self.summary(run.id) for run in runs)

    def show(self, request: ShowLocalJobRequest) -> LocalJobSummary:
        return self.summary(request.run_id)

    def logs(self, request: ReadLocalJobLogsRequest) -> LocalJobLogsResult:
        job = self.summary(request.run_id)
        events = self.control.list_run_events(
            ListControlRunEventsRequest(run_id=request.run_id)
        )
        return LocalJobLogsResult(job=job, events=events)

    def summary(self, run_id: str) -> LocalJobSummary:
        run = self.control.get_run(GetControlRunRequest(run_id=run_id))
        repository = self.control.get_repository(
            GetRepositoryRequest(repository_id=run.repository_id)
        )
        branch = self.control.get_branch(GetBranchRequest(branch_id=run.branch_id))
        return LocalJobSummary(
            run=run,
            repository=repository,
            branch=branch,
        )
