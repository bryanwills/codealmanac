from codealmanac.services.control import models as m
from codealmanac.services.control import requests as r
from codealmanac.services.control.current_git import record_current_git_trigger
from codealmanac.services.control.ports import LocalGitStateProbe
from codealmanac.services.control.store import ControlStore


class ControlService:
    def __init__(self, store: ControlStore, local_git_state: LocalGitStateProbe):
        self.store = store
        self.local_git_state = local_git_state

    def ensure_ready(self) -> m.ControlSchemaStatus:
        return self.store.ensure_ready()

    def status(
        self,
        request: r.ReadControlSchemaStatusRequest | None = None,
    ) -> m.ControlSchemaStatus:
        resolved = request or r.ReadControlSchemaStatusRequest()
        return self.store.status(resolved.ensure)

    def get_repository(self, request: r.GetRepositoryRequest) -> m.RepositoryRecord:
        return self.store.get_repository(request)

    def find_repository_by_local_root(
        self,
        request: r.FindRepositoryByLocalRootRequest,
    ) -> m.RepositoryRecord | None:
        return self.store.find_repository_by_local_root(request)

    def get_branch(self, request: r.GetBranchRequest) -> m.BranchRecord:
        return self.store.get_branch(request)

    def find_branch_by_name(
        self,
        request: r.FindBranchByNameRequest,
    ) -> m.BranchRecord | None:
        return self.store.find_branch_by_name(request)

    def get_run(self, request: r.GetControlRunRequest) -> m.ControlRunRecord:
        return self.store.get_run(request)

    def list_sessions_for_branch(
        self,
        request: r.ListBranchSessionsRequest,
    ) -> tuple[m.SessionRecord, ...]:
        return self.store.list_sessions_for_branch(request)

    def upsert_repository(
        self,
        request: r.UpsertRepositoryRequest,
    ) -> m.RepositoryRecord:
        return self.store.upsert_repository(request)

    def set_branch_policy(
        self,
        request: r.SetBranchPolicyRequest,
    ) -> m.BranchRecord:
        return self.store.set_branch_policy(request)

    def record_trigger_event(
        self,
        request: r.RecordTriggerEventRequest,
    ) -> m.RecordTriggerEventResult:
        return self.store.record_trigger_event(request)

    def record_current_git_trigger(
        self,
        request: r.RecordCurrentGitTriggerRequest,
    ) -> m.RecordTriggerEventResult:
        return record_current_git_trigger(
            self.store,
            self.local_git_state,
            request,
        )

    def list_trigger_events(
        self,
        request: r.ListTriggerEventsRequest | None = None,
    ) -> tuple[m.TriggerEventRecord, ...]:
        resolved = request or r.ListTriggerEventsRequest()
        return self.store.list_trigger_events(resolved)

    def create_run(self, request: r.CreateControlRunRequest) -> m.ControlRunRecord:
        return self.store.create_run(request)

    def update_run(self, request: r.UpdateControlRunRequest) -> m.ControlRunRecord:
        return self.store.update_run(request)

    def append_run_event(
        self,
        request: r.AppendControlRunEventRequest,
    ) -> m.ControlRunEventRecord:
        return self.store.append_run_event(request)

    def upsert_session(self, request: r.UpsertSessionRequest) -> m.SessionRecord:
        return self.store.upsert_session(request)

    def upsert_turn(self, request: r.UpsertTurnRequest) -> m.TurnRecord:
        return self.store.upsert_turn(request)

    def link_turn_branch(self, request: r.LinkTurnBranchRequest) -> None:
        self.store.link_turn_branch(request)

    def list_run_events(
        self,
        request: r.ListControlRunEventsRequest,
    ) -> tuple[m.ControlRunEventRecord, ...]:
        return self.store.list_run_events(request)

    def list_runs(
        self,
        request: r.ListControlRunsRequest | None = None,
    ) -> tuple[m.ControlRunRecord, ...]:
        resolved = request or r.ListControlRunsRequest()
        return self.store.list_runs(resolved)

    def claim_next_trigger(
        self,
        request: r.ClaimNextTriggerRequest | None = None,
    ) -> m.ClaimNextTriggerResult:
        resolved = request or r.ClaimNextTriggerRequest()
        return self.store.claim_next_trigger(resolved)
