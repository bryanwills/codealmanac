from datetime import datetime
from pathlib import Path

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.services.runs.models import RunStatus
from codealmanac.services.runs.requests import FinishRunRequest
from codealmanac.services.runs.service import RunsService
from codealmanac.workflows.ingest.requests import (
    RunIngestRequest,
    RunIngestWithRunRequest,
)
from codealmanac.workflows.ingest.service import IngestWorkflow
from codealmanac.workflows.run_queue.service import RunQueueWorkflow
from codealmanac.workflows.sync.models import (
    SyncEvaluation,
    SyncExecution,
    SyncLedger,
    SyncSkipped,
    SyncStarted,
    SyncWorkItem,
)
from codealmanac.workflows.sync.policy import (
    absorbed_entry,
    failed_entry,
    first_error_line,
    pending_entry,
    skip,
    sync_ingest_guidance,
    sync_ingest_title,
    sync_started,
)
from codealmanac.workflows.sync.requests import RunSyncRequest
from codealmanac.workflows.sync.store import SyncLedgerStore


class SyncRunExecutor:
    def __init__(
        self,
        runs: RunsService,
        ingest: IngestWorkflow,
        queue: RunQueueWorkflow,
        ledger_store: SyncLedgerStore,
    ):
        self.runs = runs
        self.ingest = ingest
        self.queue = queue
        self.ledger_store = ledger_store

    def run(
        self,
        request: RunSyncRequest,
        evaluation: SyncEvaluation,
        now: datetime,
        claim_owner: str,
    ) -> "SyncRunExecutionResult":
        started: list[SyncStarted] = []
        needs_attention = list(evaluation.summary.needs_attention)
        ledgers = dict(evaluation.ledgers)
        for item in evaluation.work_items:
            if request.execution == SyncExecution.BACKGROUND:
                result = self.run_background_item(
                    request,
                    item,
                    ledgers,
                    now,
                    claim_owner,
                )
            else:
                result = self.run_foreground_item(
                    request,
                    item,
                    ledgers,
                    now,
                    claim_owner,
                )
            ledgers = result.ledgers
            started.extend(result.started)
            needs_attention.extend(result.needs_attention)
        return SyncRunExecutionResult(
            started=tuple(started),
            needs_attention=tuple(needs_attention),
            ledgers=ledgers,
        )

    def run_background_item(
        self,
        request: RunSyncRequest,
        item: SyncWorkItem,
        ledgers: dict[Path, SyncLedger],
        now: datetime,
        claim_owner: str,
    ) -> "SyncItemExecutionResult":
        ingest_request = sync_ingest_request(request, item)
        run = self.queue.queue_ingest(ingest_request)
        ledger = ledgers[item.candidate.repo_root]
        pending = pending_entry(item.entry, item, now, claim_owner, run.run_id)
        ledger.sessions[item.ledger_key] = pending
        ledger = self.ledger_store.save(item.candidate.almanac_path, ledger, now)
        ledgers[item.candidate.repo_root] = ledger
        try:
            self.queue.spawn_worker(item.candidate.repo_root, request.wiki)
        except Exception as error:
            self.runs.finish(
                FinishRunRequest(
                    cwd=item.candidate.repo_root,
                    wiki=request.wiki,
                    run_id=run.run_id,
                    status=RunStatus.FAILED,
                    error=first_error_line(error),
                )
            )
            ledger.sessions[item.ledger_key] = failed_entry(pending, error, run.run_id)
            ledger = self.ledger_store.save(item.candidate.almanac_path, ledger, now)
            ledgers[item.candidate.repo_root] = ledger
            return SyncItemExecutionResult(
                ledgers=ledgers,
                needs_attention=(skip(item.candidate, "worker-spawn-failed"),),
            )
        return SyncItemExecutionResult(
            ledgers=ledgers,
            started=(sync_started(item, run.run_id),),
        )

    def run_foreground_item(
        self,
        request: RunSyncRequest,
        item: SyncWorkItem,
        ledgers: dict[Path, SyncLedger],
        now: datetime,
        claim_owner: str,
    ) -> "SyncItemExecutionResult":
        ingest_request = sync_ingest_request(request, item)
        run = self.ingest.start(ingest_request)
        ledger = ledgers[item.candidate.repo_root]
        pending = pending_entry(item.entry, item, now, claim_owner, run.run_id)
        ledger.sessions[item.ledger_key] = pending
        ledger = self.ledger_store.save(item.candidate.almanac_path, ledger, now)
        ledgers[item.candidate.repo_root] = ledger
        item = item.model_copy(update={"entry": pending})
        try:
            result = self.ingest.run_with_run(
                RunIngestWithRunRequest(
                    cwd=ingest_request.cwd,
                    inputs=ingest_request.inputs,
                    harness=ingest_request.harness,
                    wiki=ingest_request.wiki,
                    title=ingest_request.title,
                    guidance=ingest_request.guidance,
                    run_id=run.run_id,
                )
            )
        except Exception as error:
            ledger.sessions[item.ledger_key] = failed_entry(
                item.entry,
                error,
                run.run_id,
            )
            ledger = self.ledger_store.save(item.candidate.almanac_path, ledger, now)
            ledgers[item.candidate.repo_root] = ledger
            return SyncItemExecutionResult(
                ledgers=ledgers,
                needs_attention=(skip(item.candidate, "ingest-failed"),),
            )
        ledger.sessions[item.ledger_key] = absorbed_entry(
            item.entry,
            item.snapshot,
            result.run.run_id,
            now,
        )
        ledgers[item.candidate.repo_root] = self.ledger_store.save(
            item.candidate.almanac_path,
            ledger,
            now,
        )
        return SyncItemExecutionResult(
            ledgers=ledgers,
            started=(sync_started(item, result.run.run_id),),
        )


class SyncRunExecutionResult(CodeAlmanacModel):
    started: tuple[SyncStarted, ...]
    needs_attention: tuple[SyncSkipped, ...]
    ledgers: dict[Path, SyncLedger]


class SyncItemExecutionResult(CodeAlmanacModel):
    ledgers: dict[Path, SyncLedger]
    started: tuple[SyncStarted, ...] = ()
    needs_attention: tuple[SyncSkipped, ...] = ()


def sync_ingest_request(
    request: RunSyncRequest,
    item: SyncWorkItem,
) -> RunIngestRequest:
    return RunIngestRequest(
        cwd=item.candidate.repo_root,
        inputs=(f"transcript:{item.candidate.transcript_path}",),
        harness=request.harness,
        wiki=request.wiki,
        title=sync_ingest_title(item.candidate),
        guidance=sync_ingest_guidance(item),
    )
