from contextlib import suppress
from pathlib import Path

from codealmanac.prompts import PromptName, PromptRenderer, RenderPromptRequest
from codealmanac.services.harnesses.models import HarnessRunResult
from codealmanac.services.harnesses.requests import RunHarnessRequest
from codealmanac.services.harnesses.service import HarnessesService
from codealmanac.services.index.service import IndexService
from codealmanac.services.runs.models import RunEventKind, RunOperation, RunStatus
from codealmanac.services.runs.requests import (
    FinishRunRequest,
    RecordRunEventRequest,
    RecordRunHarnessTranscriptRequest,
    StartRunRequest,
)
from codealmanac.services.runs.service import RunsService
from codealmanac.services.sources.models import SourceBrief
from codealmanac.services.sources.requests import ResolveSourcesRequest
from codealmanac.services.sources.service import SourcesService
from codealmanac.services.workspaces.models import Workspace
from codealmanac.services.workspaces.requests import SelectWorkspaceRequest
from codealmanac.services.workspaces.service import WorkspacesService
from codealmanac.workflows.ingest.models import IngestPromptPayload, IngestResult
from codealmanac.workflows.ingest.requests import RunIngestRequest
from codealmanac.workflows.lifecycle import (
    LifecycleMutationPolicy,
    first_line,
    validate_harness_result,
)

INGEST_PROMPT_SECTIONS = (
    PromptName.BASE_PURPOSE,
    PromptName.BASE_NOTABILITY,
    PromptName.BASE_SYNTAX,
    PromptName.OPERATION_INGEST,
)


class IngestWorkflow:
    def __init__(
        self,
        workspaces: WorkspacesService,
        sources: SourcesService,
        harnesses: HarnessesService,
        runs: RunsService,
        index: IndexService,
        mutation_policy: LifecycleMutationPolicy,
        prompts: PromptRenderer,
    ):
        self.workspaces = workspaces
        self.sources = sources
        self.harnesses = harnesses
        self.runs = runs
        self.index = index
        self.mutation_policy = mutation_policy
        self.prompts = prompts

    def run(self, request: RunIngestRequest) -> IngestResult:
        workspace = self.resolve_workspace(request.cwd, request.wiki)
        started = self.runs.start(
            StartRunRequest(
                cwd=request.cwd,
                wiki=request.wiki,
                operation=RunOperation.INGEST,
                title=request.title or default_title(request.inputs),
            )
        )
        try:
            preflight = self.mutation_policy.preflight(workspace)
            self.record(
                request,
                started.run_id,
                RunEventKind.MESSAGE,
                "verified clean .almanac preflight",
            )
            sources = self.sources.resolve(
                ResolveSourcesRequest(cwd=request.cwd, inputs=request.inputs)
            )
            self.record(
                request,
                started.run_id,
                RunEventKind.MESSAGE,
                f"resolved {len(sources)} {source_word(len(sources))}",
            )
            harness = self.harnesses.run(
                RunHarnessRequest(
                    kind=request.harness,
                    cwd=workspace.root_path,
                    prompt=render_ingest_prompt(
                        self.prompts,
                        workspace,
                        sources,
                        request.guidance,
                    ),
                    title=request.title,
                )
            )
            self.record_harness_transcript(request, started.run_id, harness)
            safety = self.mutation_policy.validate(
                preflight,
                workspace,
                harness.changed_files,
            )
            validate_harness_result(harness)
            self.record(
                request,
                started.run_id,
                RunEventKind.OUTPUT,
                f"{harness.kind.value} {harness.status.value}",
            )
            index = self.index.ensure_fresh(workspace.workspace_id)
            finished = self.runs.finish(
                FinishRunRequest(
                    cwd=request.cwd,
                    wiki=request.wiki,
                    run_id=started.run_id,
                    status=RunStatus.DONE,
                    summary=harness.summary or "ingest completed",
                )
            )
            return IngestResult(
                run=finished,
                sources=sources,
                harness=harness,
                safety=safety,
                index=index,
            )
        except Exception as error:
            self.fail_run(request, started.run_id, error)
            raise

    def resolve_workspace(self, cwd: Path, wiki: str | None) -> Workspace:
        if wiki is None:
            return self.workspaces.resolve(cwd)
        return self.workspaces.select(
            SelectWorkspaceRequest(selector=wiki, base_path=cwd)
        )

    def record(
        self,
        request: RunIngestRequest,
        run_id: str,
        kind: RunEventKind,
        message: str,
    ) -> None:
        self.runs.record_event(
            RecordRunEventRequest(
                cwd=request.cwd,
                wiki=request.wiki,
                run_id=run_id,
                kind=kind,
                message=message,
            )
        )

    def record_harness_transcript(
        self,
        request: RunIngestRequest,
        run_id: str,
        harness: HarnessRunResult,
    ) -> None:
        if harness.transcript is None:
            return
        self.runs.record_harness_transcript(
            RecordRunHarnessTranscriptRequest(
                cwd=request.cwd,
                wiki=request.wiki,
                run_id=run_id,
                transcript=harness.transcript,
            )
        )

    def fail_run(
        self,
        request: RunIngestRequest,
        run_id: str,
        error: Exception,
    ) -> None:
        message = first_line(str(error)) or error.__class__.__name__
        with suppress(Exception):
            self.record(request, run_id, RunEventKind.ERROR, message)
            self.runs.finish(
                FinishRunRequest(
                    cwd=request.cwd,
                    wiki=request.wiki,
                    run_id=run_id,
                    status=RunStatus.FAILED,
                    error=message,
                )
            )


def render_ingest_prompt(
    prompts: PromptRenderer,
    workspace: Workspace,
    sources: tuple[SourceBrief, ...],
    guidance: str | None,
) -> str:
    payload = IngestPromptPayload(
        workspace_name=workspace.name,
        workspace_root=workspace.root_path,
        almanac_root=workspace.almanac_path,
        sources=sources,
        guidance=guidance,
    )
    return prompts.render(
        RenderPromptRequest(
            sections=INGEST_PROMPT_SECTIONS,
            context=(
                "Runtime context:\n"
                f"{payload.model_dump_json(indent=2)}\n",
            ),
        )
    )


def default_title(inputs: tuple[str, ...]) -> str:
    if len(inputs) == 1:
        return f"Ingest {inputs[0]}"
    return f"Ingest {len(inputs)} sources"


def source_word(count: int) -> str:
    return "source" if count == 1 else "sources"
