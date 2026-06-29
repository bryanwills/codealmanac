from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path

from codealmanac.core.paths import normalize_path
from codealmanac.services.runs.models import RunRecord
from codealmanac.services.runs.requests import ListRunsRequest
from codealmanac.services.runs.service import RunsService
from codealmanac.services.sources.models import TranscriptCandidate
from codealmanac.services.sources.requests import DiscoverTranscriptsRequest
from codealmanac.services.sources.service import SourcesService
from codealmanac.services.workspaces.models import Workspace
from codealmanac.services.workspaces.requests import SelectWorkspaceRequest
from codealmanac.services.workspaces.service import WorkspacesService
from codealmanac.workflows.sync.models import (
    SyncCursorDecision,
    SyncDecisionKind,
    SyncLedgerEntry,
    SyncLedgerStatus,
    SyncMode,
    SyncReady,
    SyncSkipped,
    SyncSummary,
    TranscriptSnapshot,
)
from codealmanac.workflows.sync.requests import RunSyncStatusRequest
from codealmanac.workflows.sync.store import SyncLedgerStore

EMPTY_SHA256 = f"sha256:{sha256(b'').hexdigest()}"


class SyncWorkflow:
    def __init__(
        self,
        workspaces: WorkspacesService,
        sources: SourcesService,
        runs: RunsService,
        ledger_store: SyncLedgerStore,
    ):
        self.workspaces = workspaces
        self.sources = sources
        self.runs = runs
        self.ledger_store = ledger_store

    def status(self, request: RunSyncStatusRequest) -> SyncSummary:
        now = request.now or datetime.now(UTC)
        candidates = self.sources.discover_transcripts(
            DiscoverTranscriptsRequest(
                home=normalize_path(request.home or Path.home()),
                apps=request.apps,
            )
        )
        scoped_candidates = self.scope_candidates(request, candidates)
        ready: list[SyncReady] = []
        skipped: list[SyncSkipped] = []
        needs_attention: list[SyncSkipped] = []
        ledgers: dict[Path, dict[str, SyncLedgerEntry]] = {}
        run_records: dict[Path, tuple[RunRecord, ...]] = {}
        for candidate in scoped_candidates:
            quiet_skip = quiet_window_skip(candidate, request, now)
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
                self.ledger_store.load(candidate.repo_root / ".almanac").sessions,
            )
            snapshot = read_transcript(candidate)
            if snapshot is None:
                needs_attention.append(skip(candidate, "read-failed"))
                continue
            entry = ledger.get(ledger_key(candidate)) or fresh_ledger_entry(candidate)
            decision = evaluate_cursor(entry, snapshot)
            if decision.kind == SyncDecisionKind.SKIP:
                skipped.append(skip(candidate, decision.reason))
            elif decision.kind == SyncDecisionKind.NEEDS_ATTENTION:
                needs_attention.append(skip(candidate, decision.reason))
            else:
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
        return SyncSummary(
            mode=SyncMode.STATUS,
            scanned=len(candidates),
            eligible=len(ready),
            ready=tuple(ready),
            skipped=tuple(skipped),
            needs_attention=tuple(needs_attention),
        )

    def scope_candidates(
        self,
        request: RunSyncStatusRequest,
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


def same_workspace(repo_root: Path, workspace: Workspace) -> bool:
    return normalize_path(repo_root) == normalize_path(workspace.root_path)


def quiet_window_skip(
    candidate: TranscriptCandidate,
    request: RunSyncStatusRequest,
    now: datetime,
) -> SyncSkipped | None:
    if now - candidate.modified_at < request.quiet:
        return skip(candidate, "quiet-window")
    return None


def is_internal_transcript(
    candidate: TranscriptCandidate,
    records: tuple[RunRecord, ...],
) -> bool:
    candidate_path = normalize_path(candidate.transcript_path)
    for record in records:
        ref = record.harness_transcript
        if ref is None or ref.kind.value != candidate.app.value:
            continue
        if ref.session_id == candidate.session_id:
            return True
        if (
            ref.transcript_path is not None
            and normalize_path(ref.transcript_path) == candidate_path
        ):
            return True
    return False


def read_transcript(candidate: TranscriptCandidate) -> TranscriptSnapshot | None:
    try:
        content = candidate.transcript_path.read_bytes()
    except OSError:
        return None
    return TranscriptSnapshot(
        content=content,
        current_size=len(content),
        current_line=count_lines(content.decode("utf-8", errors="replace")),
    )


def fresh_ledger_entry(candidate: TranscriptCandidate) -> SyncLedgerEntry:
    return SyncLedgerEntry(
        app=candidate.app,
        session_id=candidate.session_id,
        transcript_path=candidate.transcript_path,
        status=SyncLedgerStatus.DONE,
        last_absorbed_size=0,
        last_absorbed_line=0,
        last_absorbed_prefix_hash=EMPTY_SHA256,
    )


def evaluate_cursor(
    entry: SyncLedgerEntry,
    snapshot: TranscriptSnapshot,
) -> SyncCursorDecision:
    if entry.status == SyncLedgerStatus.PENDING:
        return SyncCursorDecision(
            kind=SyncDecisionKind.SKIP,
            reason="sync-already-pending",
        )
    if snapshot.current_size <= entry.last_absorbed_size:
        return SyncCursorDecision(kind=SyncDecisionKind.SKIP, reason="unchanged")
    prefix_hash = sha256_bytes(snapshot.content[: entry.last_absorbed_size])
    if prefix_hash != entry.last_absorbed_prefix_hash:
        return SyncCursorDecision(
            kind=SyncDecisionKind.NEEDS_ATTENTION,
            reason="prefix-mismatch",
        )
    return SyncCursorDecision(
        kind=SyncDecisionKind.READY,
        from_line=entry.last_absorbed_line + 1,
        to_line=snapshot.current_line,
    )


def ledger_key(candidate: TranscriptCandidate) -> str:
    return f"{candidate.app.value}:{candidate.transcript_path}"


def sha256_bytes(content: bytes) -> str:
    return f"sha256:{sha256(content).hexdigest()}"


def count_lines(content: str) -> int:
    if content == "":
        return 0
    return content.count("\n") + (0 if content.endswith("\n") else 1)


def skip(candidate: TranscriptCandidate, reason: str) -> SyncSkipped:
    return SyncSkipped(
        app=candidate.app,
        session_id=candidate.session_id,
        transcript_path=candidate.transcript_path,
        repo_root=candidate.repo_root,
        reason=reason,
    )
