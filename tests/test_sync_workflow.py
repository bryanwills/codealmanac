from datetime import UTC, datetime, timedelta
from hashlib import sha256
from pathlib import Path

from codealmanac.app import create_app
from codealmanac.core.models import AppConfig
from codealmanac.services.harnesses.models import HarnessKind, HarnessTranscriptRef
from codealmanac.services.runs.models import RunOperation
from codealmanac.services.runs.requests import (
    RecordRunHarnessTranscriptRequest,
    StartRunRequest,
)
from codealmanac.services.sources.models import TranscriptApp, TranscriptCandidate
from codealmanac.services.sources.requests import DiscoverTranscriptsRequest
from codealmanac.services.workspaces.requests import InitializeWorkspaceRequest
from codealmanac.workflows.sync.models import (
    SyncLedger,
    SyncLedgerEntry,
    SyncLedgerStatus,
)
from codealmanac.workflows.sync.requests import RunSyncStatusRequest


class FakeTranscriptDiscoveryAdapter:
    app = TranscriptApp.CODEX

    def __init__(self, candidates: tuple[TranscriptCandidate, ...]):
        self.candidates = candidates
        self.requests: list[DiscoverTranscriptsRequest] = []

    def discover(
        self,
        request: DiscoverTranscriptsRequest,
    ) -> tuple[TranscriptCandidate, ...]:
        self.requests.append(request)
        return self.candidates


def test_sync_status_reports_ready_transcript_ranges(
    tmp_path: Path,
    isolated_home: Path,
):
    repo = tmp_path / "repo"
    repo.mkdir()
    transcript = write_transcript(tmp_path, "one\ntwo\n")
    candidate = transcript_candidate(repo, transcript, modified_at=old_time())
    app = app_with_candidates(isolated_home, (candidate,))
    app.workflows.build.initialize(InitializeWorkspaceRequest(path=repo))

    summary = app.workflows.sync.status(
        RunSyncStatusRequest(
            cwd=repo,
            apps=(TranscriptApp.CODEX,),
            quiet=timedelta(),
            now=current_time(),
        )
    )

    assert summary.scanned == 1
    assert summary.eligible == 1
    assert summary.ready[0].session_id == "session-1"
    assert summary.ready[0].from_line == 1
    assert summary.ready[0].to_line == 2
    assert summary.skipped == ()
    assert summary.needs_attention == ()


def test_sync_status_skips_internal_lifecycle_transcripts_by_session(
    tmp_path: Path,
    isolated_home: Path,
):
    repo = tmp_path / "repo"
    repo.mkdir()
    transcript = write_transcript(tmp_path, "one\ntwo\n")
    candidate = transcript_candidate(repo, transcript, modified_at=old_time())
    app = app_with_candidates(isolated_home, (candidate,))
    app.workflows.build.initialize(InitializeWorkspaceRequest(path=repo))
    record = app.runs.start(
        StartRunRequest(
            cwd=repo,
            operation=RunOperation.INGEST,
            title="Internal ingest",
        )
    )
    app.runs.record_harness_transcript(
        RecordRunHarnessTranscriptRequest(
            cwd=repo,
            run_id=record.run_id,
            transcript=HarnessTranscriptRef(
                kind=HarnessKind.CODEX,
                session_id="session-1",
            ),
        )
    )

    summary = app.workflows.sync.status(
        RunSyncStatusRequest(
            cwd=repo,
            apps=(TranscriptApp.CODEX,),
            quiet=timedelta(),
            now=current_time(),
        )
    )

    assert summary.eligible == 0
    assert summary.ready == ()
    assert summary.skipped[0].reason == "internal-lifecycle-transcript"


def test_sync_status_skips_internal_lifecycle_transcripts_by_path(
    tmp_path: Path,
    isolated_home: Path,
):
    repo = tmp_path / "repo"
    repo.mkdir()
    transcript = write_transcript(tmp_path, "one\ntwo\n")
    candidate = transcript_candidate(repo, transcript, modified_at=old_time())
    app = app_with_candidates(isolated_home, (candidate,))
    app.workflows.build.initialize(InitializeWorkspaceRequest(path=repo))
    record = app.runs.start(
        StartRunRequest(
            cwd=repo,
            operation=RunOperation.GARDEN,
            title="Internal garden",
        )
    )
    app.runs.record_harness_transcript(
        RecordRunHarnessTranscriptRequest(
            cwd=repo,
            run_id=record.run_id,
            transcript=HarnessTranscriptRef(
                kind=HarnessKind.CODEX,
                session_id="different-session",
                transcript_path=transcript,
            ),
        )
    )

    summary = app.workflows.sync.status(
        RunSyncStatusRequest(
            cwd=repo,
            apps=(TranscriptApp.CODEX,),
            quiet=timedelta(),
            now=current_time(),
        )
    )

    assert summary.eligible == 0
    assert summary.ready == ()
    assert summary.skipped[0].reason == "internal-lifecycle-transcript"


def test_sync_status_applies_quiet_window(
    tmp_path: Path,
    isolated_home: Path,
):
    repo = tmp_path / "repo"
    repo.mkdir()
    transcript = write_transcript(tmp_path, "one\n")
    candidate = transcript_candidate(repo, transcript, modified_at=current_time())
    app = app_with_candidates(isolated_home, (candidate,))
    app.workflows.build.initialize(InitializeWorkspaceRequest(path=repo))

    summary = app.workflows.sync.status(
        RunSyncStatusRequest(
            cwd=repo,
            apps=(TranscriptApp.CODEX,),
            quiet=timedelta(minutes=45),
            now=current_time(),
        )
    )

    assert summary.eligible == 0
    assert summary.skipped[0].reason == "quiet-window"


def test_sync_status_reports_prefix_mismatch_from_ledger(
    tmp_path: Path,
    isolated_home: Path,
):
    repo = tmp_path / "repo"
    repo.mkdir()
    transcript = write_transcript(tmp_path, "new prefix\nmore\n")
    candidate = transcript_candidate(repo, transcript, modified_at=old_time())
    app = app_with_candidates(isolated_home, (candidate,))
    workspace = app.workflows.build.initialize(InitializeWorkspaceRequest(path=repo))
    write_sync_ledger(
        workspace.almanac_path,
        candidate,
        last_absorbed_size=3,
        last_absorbed_line=1,
        prefix_hash=sha256_text("old"),
    )

    summary = app.workflows.sync.status(
        RunSyncStatusRequest(
            cwd=repo,
            apps=(TranscriptApp.CODEX,),
            quiet=timedelta(),
            now=current_time(),
        )
    )

    assert summary.eligible == 0
    assert summary.needs_attention[0].reason == "prefix-mismatch"


def app_with_candidates(
    isolated_home: Path,
    candidates: tuple[TranscriptCandidate, ...],
):
    return create_app(
        AppConfig(registry_path=isolated_home / ".almanac/registry.json"),
        transcript_discovery_adapters=(FakeTranscriptDiscoveryAdapter(candidates),),
    )


def transcript_candidate(
    repo: Path,
    transcript: Path,
    modified_at: datetime,
) -> TranscriptCandidate:
    return TranscriptCandidate(
        app=TranscriptApp.CODEX,
        session_id="session-1",
        transcript_path=transcript,
        cwd=repo,
        repo_root=repo,
        modified_at=modified_at,
        size_bytes=transcript.stat().st_size,
    )


def write_transcript(root: Path, content: str) -> Path:
    path = root / "session.jsonl"
    path.write_text(content, encoding="utf-8")
    return path


def current_time() -> datetime:
    return datetime(2026, 6, 29, 12, 0, tzinfo=UTC)


def old_time() -> datetime:
    return current_time() - timedelta(hours=2)


def write_sync_ledger(
    almanac_path: Path,
    candidate: TranscriptCandidate,
    last_absorbed_size: int,
    last_absorbed_line: int,
    prefix_hash: str,
) -> None:
    path = almanac_path / "jobs/sync-ledger.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    ledger = SyncLedger(
        version=1,
        updated_at=current_time(),
        sessions={
            f"{candidate.app.value}:{candidate.transcript_path}": SyncLedgerEntry(
                app=candidate.app,
                session_id=candidate.session_id,
                transcript_path=candidate.transcript_path,
                status=SyncLedgerStatus.DONE,
                last_absorbed_size=last_absorbed_size,
                last_absorbed_line=last_absorbed_line,
                last_absorbed_prefix_hash=prefix_hash,
            )
        },
    )
    path.write_text(ledger.model_dump_json(indent=2), encoding="utf-8")


def sha256_text(value: str) -> str:
    return f"sha256:{sha256(value.encode('utf-8')).hexdigest()}"
