from codealmanac.manual import ManualLibrary
from codealmanac.prompts import PromptName, PromptRenderer, RenderPromptRequest
from codealmanac.services.index.service import IndexService
from codealmanac.services.runs.models import RunEventKind, RunOperation
from codealmanac.services.runs.requests import StartRunRequest
from codealmanac.services.runs.service import RunsService
from codealmanac.services.wiki.service import WikiService
from codealmanac.services.workspaces.models import Workspace
from codealmanac.services.workspaces.requests import (
    InitializeWorkspaceRequest,
    RegisterWorkspaceRequest,
)
from codealmanac.services.workspaces.roots import AlmanacRootMatch
from codealmanac.services.workspaces.service import WorkspacesService
from codealmanac.workflows.build.models import BuildPromptPayload, BuildResult
from codealmanac.workflows.build.requests import RunBuildRequest
from codealmanac.workflows.lifecycle_commit import lifecycle_commit_policy
from codealmanac.workflows.page_run import (
    PageRunBeginRequest,
    PageRunExecuteRequest,
    PageRunRecordEventRequest,
    PageRunWorkflow,
)

BUILD_PROMPT_SECTIONS = (
    PromptName.BASE_KERNEL,
    PromptName.OPERATION_BUILD,
)


class BuildWorkflow:
    def __init__(
        self,
        workspaces: WorkspacesService,
        wiki: WikiService,
        index: IndexService,
        runs: RunsService,
        page_runs: PageRunWorkflow,
        prompts: PromptRenderer,
        manual: ManualLibrary,
    ):
        self.workspaces = workspaces
        self.wiki = wiki
        self.index = index
        self.runs = runs
        self.page_runs = page_runs
        self.prompts = prompts
        self.manual = manual

    def initialize(self, request: InitializeWorkspaceRequest) -> Workspace:
        return self.initialize_ready(request).workspace

    def run(self, request: RunBuildRequest) -> BuildResult:
        initialize_request = InitializeWorkspaceRequest(
            path=request.path,
            name=request.name,
            description=request.description,
        )
        target = self.workspaces.initialization_target(
            initialize_request.path,
            initialize_request.almanac_root,
        )
        self.page_runs.mutation_policy.ensure_tracking_available(target.repo_root)
        workspace = self._register_target(target, initialize_request)
        started = self.runs.start(
            StartRunRequest(
                cwd=workspace.root_path,
                wiki=workspace.name,
                operation=RunOperation.BUILD,
                title=request.title or "Build wiki",
            )
        )
        context = self.page_runs.begin(
            PageRunBeginRequest(
                cwd=workspace.root_path,
                wiki=workspace.name,
                run_id=started.run_id,
            )
        )
        try:
            context = self.page_runs.preflight(context)
            self.wiki.initialize(workspace.workspace_id)
            self.page_runs.record(
                PageRunRecordEventRequest(
                    context=context,
                    kind=RunEventKind.MESSAGE,
                    message="prepared starter wiki",
                )
            )
            page_run = self.page_runs.execute(
                PageRunExecuteRequest(
                    context=context,
                    harness=request.harness,
                    prompt=render_build_prompt(
                        self.prompts,
                        self.manual,
                        workspace,
                        request.guidance,
                        request.auto_commit,
                    ),
                    title=request.title,
                    success_summary="build completed",
                )
            )
            return BuildResult(
                workspace=workspace,
                run=page_run.run,
                harness=page_run.harness,
                safety=page_run.safety,
                index=page_run.index,
            )
        except Exception as error:
            self.page_runs.fail(context, error)
            raise

    def build(self, request: InitializeWorkspaceRequest) -> BuildResult:
        return self.initialize_ready(request)

    def initialize_ready(self, request: InitializeWorkspaceRequest) -> BuildResult:
        workspace = self._initialize_workspace(request)
        index = self.index.ensure_fresh(workspace.workspace_id)
        return BuildResult(workspace=workspace, index=index)

    def _initialize_workspace(self, request: InitializeWorkspaceRequest) -> Workspace:
        workspace = self._register_workspace(request)
        self.wiki.initialize(workspace.workspace_id)
        return workspace

    def _register_workspace(self, request: InitializeWorkspaceRequest) -> Workspace:
        target = self.workspaces.initialization_target(
            request.path,
            request.almanac_root,
        )
        return self._register_target(target, request)

    def _register_target(
        self,
        target: AlmanacRootMatch,
        request: InitializeWorkspaceRequest,
    ) -> Workspace:
        return self.workspaces.register(
            RegisterWorkspaceRequest(
                root_path=target.repo_root,
                almanac_root=target.almanac_root,
                name=request.name,
                description=request.description,
            )
        )


def render_build_prompt(
    prompts: PromptRenderer,
    manual: ManualLibrary,
    workspace: Workspace,
    guidance: str | None,
    auto_commit: bool,
) -> str:
    payload = BuildPromptPayload(
        workspace_name=workspace.name,
        workspace_root=workspace.root_path,
        almanac_root=workspace.almanac_path,
        wiki_source_root=workspace.almanac_path,
        topics_file=workspace.almanac_path / "topics.yaml",
        manual_documents=manual.inventory().documents,
        source_control=lifecycle_commit_policy(auto_commit),
        guidance=guidance,
    )
    return prompts.render(
        RenderPromptRequest(
            sections=BUILD_PROMPT_SECTIONS,
            context=(
                "Runtime context:\n"
                f"{payload.model_dump_json(indent=2)}\n",
            ),
        )
    )
