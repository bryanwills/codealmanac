from pathlib import Path

import pytest
from pydantic import ValidationError

from codealmanac.app import create_app
from codealmanac.core.errors import ExecutionFailed, NotFoundError, ValidationFailed
from codealmanac.core.models import AppConfig
from codealmanac.services.harnesses.models import (
    HarnessKind,
    HarnessReadiness,
    HarnessRunResult,
    HarnessRunStatus,
)
from codealmanac.services.harnesses.requests import RunHarnessRequest
from codealmanac.services.runs.models import RunEventKind, RunStatus
from codealmanac.services.runs.requests import ListRunsRequest, ReadRunLogRequest
from codealmanac.services.search.requests import SearchPagesRequest
from codealmanac.services.workspaces.requests import InitializeWorkspaceRequest
from codealmanac.workflows.ingest.requests import RunIngestRequest


class WritingHarnessAdapter:
    kind = HarnessKind.CODEX

    def __init__(self):
        self.requests: list[RunHarnessRequest] = []

    def check(self) -> HarnessReadiness:
        return HarnessReadiness(
            kind=self.kind,
            available=True,
            message="codex ready",
        )

    def run(self, request: RunHarnessRequest) -> HarnessRunResult:
        self.requests.append(request)
        page = request.cwd / ".almanac/pages/ingested-note.md"
        page.write_text(
            """---
title: Ingested Note
topics: [getting-started]
sources:
  - id: note
    type: file
    target: note.md
---
# Ingested Note

Ingested durable wiki knowledge from the note.
""",
            encoding="utf-8",
        )
        return HarnessRunResult(
            kind=self.kind,
            status=HarnessRunStatus.SUCCEEDED,
            output_text="updated wiki",
            summary="ingested note",
            changed_files=(page,),
        )


class UnsafeHarnessAdapter(WritingHarnessAdapter):
    def run(self, request: RunHarnessRequest) -> HarnessRunResult:
        self.requests.append(request)
        outside = request.cwd / "README.md"
        return HarnessRunResult(
            kind=self.kind,
            status=HarnessRunStatus.SUCCEEDED,
            output_text="changed the wrong file",
            changed_files=(outside,),
        )


class FailedHarnessAdapter(WritingHarnessAdapter):
    def run(self, request: RunHarnessRequest) -> HarnessRunResult:
        self.requests.append(request)
        return HarnessRunResult(
            kind=self.kind,
            status=HarnessRunStatus.FAILED,
            output_text="agent failed",
        )


def test_ingest_workflow_resolves_sources_runs_harness_and_refreshes_index(
    tmp_path: Path,
    isolated_home: Path,
):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "note.md").write_text("auth decision\n", encoding="utf-8")
    adapter = WritingHarnessAdapter()
    app = create_app(
        AppConfig(registry_path=isolated_home / ".almanac/registry.json"),
        harness_adapters=(adapter,),
    )
    app.workflows.build.initialize(InitializeWorkspaceRequest(path=repo))

    result = app.workflows.ingest.run(
        RunIngestRequest(
            cwd=repo,
            inputs=("note.md",),
            harness=HarnessKind.CODEX,
            title="Ingest note",
            guidance="Prefer short pages.",
        )
    )

    matches = app.search.search(SearchPagesRequest(cwd=repo, query="durable"))
    log = app.runs.log(ReadRunLogRequest(cwd=repo, run_id=result.run.run_id))

    assert result.run.status == RunStatus.DONE
    assert result.run.summary == "ingested note"
    assert result.sources[0].ref.fingerprint is not None
    assert result.harness.changed_files == (
        repo / ".almanac/pages/ingested-note.md",
    )
    assert result.index.pages_indexed == 2
    assert matches[0].slug == "ingested-note"
    assert "path.file" in adapter.requests[0].prompt
    assert "Prefer short pages." in adapter.requests[0].prompt
    assert "public CLI name is codealmanac" in adapter.requests[0].prompt
    assert tuple(entry.kind for entry in log) == (
        RunEventKind.STATUS,
        RunEventKind.MESSAGE,
        RunEventKind.OUTPUT,
        RunEventKind.STATUS,
    )


def test_ingest_workflow_fails_run_when_harness_is_missing(
    tmp_path: Path,
    isolated_home: Path,
):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "note.md").write_text("auth decision\n", encoding="utf-8")
    app = create_app(AppConfig(registry_path=isolated_home / ".almanac/registry.json"))
    app.workflows.build.initialize(InitializeWorkspaceRequest(path=repo))

    with pytest.raises(NotFoundError):
        app.workflows.ingest.run(
            RunIngestRequest(
                cwd=repo,
                inputs=("note.md",),
                harness=HarnessKind.CODEX,
            )
        )

    run = app.runs.list(ListRunsRequest(cwd=repo))[0]
    log = app.runs.log(ReadRunLogRequest(cwd=repo, run_id=run.run_id))

    assert run.status == RunStatus.FAILED
    assert run.error == "harness not found: codex"
    assert RunEventKind.ERROR in {entry.kind for entry in log}


def test_ingest_workflow_rejects_harness_changes_outside_almanac(
    tmp_path: Path,
    isolated_home: Path,
):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "note.md").write_text("auth decision\n", encoding="utf-8")
    app = create_app(
        AppConfig(registry_path=isolated_home / ".almanac/registry.json"),
        harness_adapters=(UnsafeHarnessAdapter(),),
    )
    app.workflows.build.initialize(InitializeWorkspaceRequest(path=repo))

    with pytest.raises(ValidationFailed):
        app.workflows.ingest.run(
            RunIngestRequest(
                cwd=repo,
                inputs=("note.md",),
                harness=HarnessKind.CODEX,
            )
        )

    run = app.runs.list(ListRunsRequest(cwd=repo))[0]

    assert run.status == RunStatus.FAILED
    assert run.error is not None
    assert run.error.startswith("harness changed file outside .almanac:")
    assert "README.md" in run.error


def test_ingest_workflow_fails_when_harness_returns_failed_status(
    tmp_path: Path,
    isolated_home: Path,
):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "note.md").write_text("auth decision\n", encoding="utf-8")
    app = create_app(
        AppConfig(registry_path=isolated_home / ".almanac/registry.json"),
        harness_adapters=(FailedHarnessAdapter(),),
    )
    app.workflows.build.initialize(InitializeWorkspaceRequest(path=repo))

    with pytest.raises(ExecutionFailed):
        app.workflows.ingest.run(
            RunIngestRequest(
                cwd=repo,
                inputs=("note.md",),
                harness=HarnessKind.CODEX,
            )
        )

    run = app.runs.list(ListRunsRequest(cwd=repo))[0]

    assert run.status == RunStatus.FAILED
    assert run.error == "harness codex failed with status failed"


def test_run_ingest_request_requires_inputs(tmp_path: Path):
    with pytest.raises(ValidationError):
        RunIngestRequest(cwd=tmp_path, inputs=(), harness=HarnessKind.CODEX)
