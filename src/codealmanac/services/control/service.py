from codealmanac.services.control.models import (
    BranchRecord,
    ControlSchemaStatus,
    RecordTriggerEventResult,
    RepositoryRecord,
    TriggerEventRecord,
)
from codealmanac.services.control.requests import (
    EnsureControlSchemaRequest,
    ListTriggerEventsRequest,
    ReadControlSchemaStatusRequest,
    RecordTriggerEventRequest,
    SetBranchPolicyRequest,
    UpsertRepositoryRequest,
)
from codealmanac.services.control.store import ControlStore


class ControlService:
    def __init__(self, store: ControlStore):
        self.store = store

    def ensure_ready(
        self,
        request: EnsureControlSchemaRequest | None = None,
    ) -> ControlSchemaStatus:
        _ = request or EnsureControlSchemaRequest()
        return self.store.ensure_ready()

    def status(
        self,
        request: ReadControlSchemaStatusRequest | None = None,
    ) -> ControlSchemaStatus:
        resolved = request or ReadControlSchemaStatusRequest()
        return self.store.status(resolved.ensure)

    def upsert_repository(
        self,
        request: UpsertRepositoryRequest,
    ) -> RepositoryRecord:
        return self.store.upsert_repository(request)

    def set_branch_policy(
        self,
        request: SetBranchPolicyRequest,
    ) -> BranchRecord:
        return self.store.set_branch_policy(request)

    def record_trigger_event(
        self,
        request: RecordTriggerEventRequest,
    ) -> RecordTriggerEventResult:
        return self.store.record_trigger_event(request)

    def list_trigger_events(
        self,
        request: ListTriggerEventsRequest | None = None,
    ) -> tuple[TriggerEventRecord, ...]:
        resolved = request or ListTriggerEventsRequest()
        return self.store.list_trigger_events(resolved)
