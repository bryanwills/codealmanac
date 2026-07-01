from datetime import UTC, datetime
from pathlib import Path

from codealmanac.core.paths import normalize_path
from codealmanac.services.runs.models import RunRecord, RunStatus
from codealmanac.services.runs.requests import FinishRunRequest, ListRunsRequest
from codealmanac.services.runs.service import RunsService
from codealmanac.services.sources.models import TranscriptCandidate
from codealmanac.services.sources.requests import DiscoverTranscriptsRequest
from codealmanac.services.sources.service import SourcesService
from codealmanac.services.workspaces.requests import SelectWorkspaceRequest
from codealmanac.services.workspaces.service import WorkspacesService
from codealmanac.workflows.ingest.requests import (
    RunIngestRequest,
    RunIngestWithRunRequest,
)
from codealmanac.workflows.ingest.service import IngestWorkflow
from codealmanac.workflows.run_queue.service import RunQueueWorkflow
from codealmanac.workflows.sync.models import (
    SyncDecisionKind,
    SyncEvaluation,
    SyncExecution,
    SyncLedger,
    SyncMode,
    SyncReady,
    SyncSkipped,
    SyncStarted,
    SyncSummary,
    SyncWorkItem,
)
from codealmanac.workflows.sync.policy import (
    absorbed_entry,
    evaluate_cursor,
    evaluate_pending_run,
    failed_entry,
    first_error_line,
    is_internal_transcript,
    ledger_entry,
    ledger_key,
    pending_entry,
    quiet_window_skip,
    read_transcript,
    reconcile_pending_entry,
    same_workspace,
    skip,
    sync_claim_owner,
    sync_ingest_guidance,
    sync_ingest_title,
    sync_started,
)
from codealmanac.workflows.sync.requests import (
    RunSyncRequest,
    RunSyncStatusRequest,
    SyncSelectionRequest,
)
from codealmanac.workflows.sync.store import SyncLedgerStore


class SyncWorkflow:
    def __init__(
        self,
        workspaces: WorkspacesService,
        sources: SourcesService,
        runs: RunsService,
        ingest: IngestWorkflow,
        queue: RunQueueWorkflow,
        ledger_store: SyncLedgerStore,
    ):
        self.workspaces = workspaces
        self.sources = sources
        self.runs = runs
        self.ingest = ingest
        self.queue = queue
        self.ledger_store = ledger_store

    def status(self, request: RunSyncStatusRequest) -> SyncSummary:
        return self.evaluate(request, SyncMode.STATUS).summary

    def run(self, request: RunSyncRequest) -> SyncSummary:
        now = request.now or datetime.now(UTC)
        evaluation = self.evaluate(request, SyncMode.SYNC, now=now)
        claim_owner = request.claim_owner or sync_claim_owner(now)
        started: list[SyncStarted] = []
        needs_attention = list(evaluation.summary.needs_attention)
        ledgers = dict(evaluation.ledgers)
        for item in evaluation.work_items:
            ledger = ledgers[item.candidate.repo_root]
            ingest_request = RunIngestRequest(
                cwd=item.candidate.repo_root,
                inputs=(f"transcript:{item.candidate.transcript_path}",),
                harness=request.harness,
                wiki=request.wiki,
                title=sync_ingest_title(item.candidate),
                guidance=sync_ingest_guidance(item),
            )
            if request.execution == SyncExecution.BACKGROUND:
                run = self.queue.queue_ingest(ingest_request)
                pending = pending_entry(item.entry, item, now, claim_owner, run.run_id)
                ledger.sessions[item.ledger_key] = pending
                ledger = self.ledger_store.save(
                    item.candidate.almanac_path,
                    ledger,
                    now,
                )
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
                    ledger.sessions[item.ledger_key] = failed_entry(
                        pending,
                        error,
                        run.run_id,
                    )
                    self.ledger_store.save(
                        item.candidate.almanac_path,
                        ledger,
                        now,
                    )
                    needs_attention.append(skip(item.candidate, "worker-spawn-failed"))
                    continue
                started.append(sync_started(item, run.run_id))
                continue
            run = self.ingest.start(ingest_request)
            pending = pending_entry(item.entry, item, now, claim_owner, run.run_id)
            ledger.sessions[item.ledger_key] = pending
            ledger = self.ledger_store.save(
                item.candidate.almanac_path,
                ledger,
                now,
            )
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
                self.ledger_store.save(
                    item.candidate.almanac_path,
                    ledger,
                    now,
                )
                needs_attention.append(skip(item.candidate, "ingest-failed"))
                continue
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
            started.append(sync_started(item, result.run.run_id))
        return evaluation.summary.model_copy(
            update={
                "started": tuple(started),
                "needs_attention": tuple(needs_attention),
            }
        )

    def evaluate(
        self,
        request: SyncSelectionRequest,
        mode: SyncMode,
        now: datetime | None = None,
    ) -> SyncEvaluation:
        current_time = now or request.now or datetime.now(UTC)
        candidates = self.sources.discover_transcripts(
            DiscoverTranscriptsRequest(
                home=normalize_path(request.home or Path.home()),
                apps=request.apps,
                almanac_roots=self.workspaces.discoverable_almanac_roots(),
            )
        )
        scoped_candidates = self.scope_candidates(request, candidates)
        ready: list[SyncReady] = []
        skipped: list[SyncSkipped] = []
        needs_attention: list[SyncSkipped] = []
        ledgers: dict[Path, SyncLedger] = {}
        work_items: list[SyncWorkItem] = []
        run_records: dict[Path, tuple[RunRecord, ...]] = {}
        for candidate in scoped_candidates:
            quiet_skip = quiet_window_skip(candidate, request, current_time)
            if quiet_skip is not None:
                skipped.append(quiet_skip)
                continue
            records = run_records.setdefault(
                candidate.repo_root,
                self.runs.list(ListRunsRequest(cwd=candidate.repo_root)),
            )
            if is_internal_transcript(candidate, records):
                skipped.append(skip(candidate, "internal-lifecycle-transcript"))
                continue
            ledger = ledgers.setdefault(
                candidate.repo_root,
                self.ledger_store.load(candidate.almanac_path),
            )
            snapshot = read_transcript(candidate)
            if snapshot is None:
                needs_attention.append(skip(candidate, "read-failed"))
                continue
            key = ledger_key(candidate)
            entry = ledger_entry(ledger, candidate, key)
            if mode == SyncMode.SYNC:
                reconciled = reconcile_pending_entry(entry, records, current_time)
                if reconciled != entry:
                    ledger.sessions[key] = reconciled
                    ledger = self.ledger_store.save(
                        candidate.almanac_path,
                        ledger,
                        current_time,
                    )
                    ledgers[candidate.repo_root] = ledger
                    entry = reconciled
            pending_run_decision = evaluate_pending_run(entry, records)
            if pending_run_decision is not None:
                if pending_run_decision.kind == SyncDecisionKind.SKIP:
                    skipped.append(skip(candidate, pending_run_decision.reason))
                else:
                    needs_attention.append(
                        skip(candidate, pending_run_decision.reason)
                    )
                continue
            decision = evaluate_cursor(
                entry,
                snapshot,
                current_time,
                request.pending_timeout,
                request.max_failed_attempts,
            )
            if decision.kind == SyncDecisionKind.SKIP:
                skipped.append(skip(candidate, decision.reason))
            elif decision.kind == SyncDecisionKind.NEEDS_ATTENTION:
                needs_attention.append(skip(candidate, decision.reason))
            else:
                if mode == SyncMode.STATUS:
                    ready.append(
                        SyncReady(
                            app=candidate.app,
                            session_id=candidate.session_id,
                            transcript_path=candidate.transcript_path,
                            repo_root=candidate.repo_root,
                            from_line=decision.from_line,
                            to_line=decision.to_line,
                        )
                    )
                work_items.append(
                    SyncWorkItem(
                        candidate=candidate,
                        ledger_key=key,
                        entry=entry,
                        snapshot=snapshot,
                        from_line=decision.from_line,
                        to_line=decision.to_line,
                    )
                )
        summary = SyncSummary(
            mode=mode,
            scanned=len(candidates),
            eligible=len(work_items),
            ready=tuple(ready),
            skipped=tuple(skipped),
            needs_attention=tuple(needs_attention),
        )
        return SyncEvaluation(
            summary=summary,
            work_items=tuple(work_items),
            ledgers=ledgers,
        )

    def scope_candidates(
        self,
        request: SyncSelectionRequest,
        candidates: tuple[TranscriptCandidate, ...],
    ) -> tuple[TranscriptCandidate, ...]:
        if request.wiki is None:
            return candidates
        workspace = self.workspaces.select(
            SelectWorkspaceRequest(selector=request.wiki, base_path=request.cwd)
        )
        return tuple(
            candidate
            for candidate in candidates
            if same_workspace(candidate.repo_root, workspace)
        )
