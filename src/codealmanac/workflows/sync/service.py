from datetime import UTC, datetime
from pathlib import Path

from codealmanac.core.paths import normalize_path
from codealmanac.services.runs.models import RunRecord
from codealmanac.services.runs.requests import ListRunsRequest
from codealmanac.services.runs.service import RunsService
from codealmanac.services.sources.models import TranscriptCandidate
from codealmanac.services.sources.requests import DiscoverTranscriptsRequest
from codealmanac.services.sources.service import SourcesService
from codealmanac.services.workspaces.requests import SelectWorkspaceRequest
from codealmanac.services.workspaces.service import WorkspacesService
from codealmanac.workflows.ingest.service import IngestWorkflow
from codealmanac.workflows.run_queue.service import RunQueueWorkflow
from codealmanac.workflows.sync.execution import SyncRunExecutor
from codealmanac.workflows.sync.models import (
    SyncDecisionKind,
    SyncEvaluation,
    SyncLedger,
    SyncMode,
    SyncReady,
    SyncSkipped,
    SyncSummary,
    SyncWorkItem,
)
from codealmanac.workflows.sync.policy import (
    evaluate_cursor,
    evaluate_pending_run,
    is_internal_transcript,
    ledger_entry,
    ledger_key,
    quiet_window_skip,
    read_transcript,
    reconcile_pending_entry,
    same_workspace,
    skip,
    sync_claim_owner,
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
        self.ledger_store = ledger_store
        self.executor = SyncRunExecutor(
            runs=runs,
            ingest=ingest,
            queue=queue,
            ledger_store=ledger_store,
        )

    def status(self, request: RunSyncStatusRequest) -> SyncSummary:
        return self.evaluate(request, SyncMode.STATUS).summary

    def run(self, request: RunSyncRequest) -> SyncSummary:
        now = request.now or datetime.now(UTC)
        evaluation = self.evaluate(request, SyncMode.SYNC, now=now)
        claim_owner = request.claim_owner or sync_claim_owner(now)
        effects = self.executor.run(
            request,
            evaluation,
            now,
            claim_owner,
        )
        return evaluation.summary.model_copy(
            update={
                "started": effects.started,
                "needs_attention": effects.needs_attention,
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
