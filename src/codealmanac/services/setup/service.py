from codealmanac.services.automation.defaults import (
    DEFAULT_GARDEN_INTERVAL,
    DEFAULT_SYNC_INTERVAL,
    duration_text,
)
from codealmanac.services.automation.models import AutomationTask
from codealmanac.services.automation.requests import (
    InstallAutomationRequest,
    UninstallAutomationRequest,
)
from codealmanac.services.config.models import DEFAULT_HARNESS, DEFAULT_SYNC_QUIET
from codealmanac.services.setup.models import (
    SetupAutomationMode,
    SetupAutomationRecommendation,
    SetupCommand,
    SetupPlan,
    SetupResult,
    UninstallResult,
)
from codealmanac.services.setup.ports import (
    InstructionInstaller,
    SetupAutomationManager,
)
from codealmanac.services.setup.requests import RunSetupRequest, RunUninstallRequest


class SetupService:
    def __init__(
        self,
        instructions: InstructionInstaller,
        automation: SetupAutomationManager,
    ):
        self._instructions = instructions
        self._automation = automation

    def run(self, request: RunSetupRequest) -> SetupResult:
        plan = setup_plan(request)
        changes = ()
        if not request.skip_instructions:
            changes = self._instructions.install(request.targets)
        automation_install = None
        if should_install_automation(request):
            automation_install = self._automation.install(
                install_automation_request(request)
            )
        if request.skip_instructions:
            return SetupResult(
                plan=plan,
                skipped_instructions=True,
                automation_install=automation_install,
            )
        return SetupResult(
            plan=plan,
            changes=changes,
            automation_install=automation_install,
        )

    def uninstall(self, request: RunUninstallRequest) -> UninstallResult:
        changes = ()
        if not request.keep_instructions:
            changes = self._instructions.uninstall(request.targets)
        automation_uninstall = None
        if not request.keep_automation:
            automation_uninstall = self._automation.uninstall(
                UninstallAutomationRequest(
                    tasks=request.automation_tasks,
                    home=request.home,
                )
            )
        if request.keep_instructions:
            return UninstallResult(
                kept_instructions=True,
                kept_automation=request.keep_automation,
                automation_uninstall=automation_uninstall,
            )
        return UninstallResult(
            kept_automation=request.keep_automation,
            changes=changes,
            automation_uninstall=automation_uninstall,
        )


def setup_plan(request: RunSetupRequest) -> SetupPlan:
    automation = automation_recommendations(request)
    mode = (
        SetupAutomationMode.INSTALL
        if should_install_automation(request)
        else SetupAutomationMode.RECOMMEND
    )
    return SetupPlan(
        default_harness=DEFAULT_HARNESS,
        instruction_targets=request.targets,
        automation_mode=mode,
        automation=automation,
        next_commands=next_commands(automation, mode),
    )


def automation_recommendations(
    request: RunSetupRequest,
) -> tuple[SetupAutomationRecommendation, ...]:
    sync_every = duration_text(
        request.sync_every if request.sync_every is not None else DEFAULT_SYNC_INTERVAL
    )
    sync_quiet = duration_text(
        request.sync_quiet if request.sync_quiet is not None else DEFAULT_SYNC_QUIET
    )
    garden_every = duration_text(
        request.garden_every
        if request.garden_every is not None
        else DEFAULT_GARDEN_INTERVAL
    )
    recommendations: list[SetupAutomationRecommendation] = []
    for task in recommendation_tasks(request):
        if task == AutomationTask.SYNC:
            recommendations.append(
                SetupAutomationRecommendation(
                    task=AutomationTask.SYNC,
                    description=(
                        "scan quiet local agent transcripts and ingest durable changes"
                    ),
                    command=(
                        "codealmanac",
                        "automation",
                        "install",
                        "sync",
                        "--every",
                        sync_every,
                        "--quiet",
                        sync_quiet,
                    ),
                )
            )
        else:
            recommendations.append(
                SetupAutomationRecommendation(
                    task=AutomationTask.GARDEN,
                    description="periodically improve wiki structure and graph hygiene",
                    command=(
                        "codealmanac",
                        "automation",
                        "install",
                        "garden",
                        "--every",
                        garden_every,
                    ),
                )
            )
    return tuple(recommendations)


def next_commands(
    automation: tuple[SetupAutomationRecommendation, ...],
    mode: SetupAutomationMode,
) -> tuple[SetupCommand, ...]:
    automation_command = (
        SetupCommand(
            label="Check scheduled automation",
            command=("codealmanac", "automation", "status"),
        )
        if mode == SetupAutomationMode.INSTALL
        else SetupCommand(
            label="Install scheduled transcript sync",
            command=automation[0].command,
        )
    )
    return (
        SetupCommand(label="Initialize this repo", command=("codealmanac", "init")),
        SetupCommand(
            label="Read the starter page",
            command=("codealmanac", "search", "getting"),
        ),
        automation_command,
    )


def should_install_automation(request: RunSetupRequest) -> bool:
    return (
        request.install_automation
        or len(request.automation_tasks) > 0
        or request.sync_every is not None
        or request.sync_quiet is not None
        or request.garden_every is not None
        or request.garden_off
    )


def recommendation_tasks(request: RunSetupRequest) -> tuple[AutomationTask, ...]:
    tasks = request.automation_tasks or (AutomationTask.SYNC, AutomationTask.GARDEN)
    return tuple(
        task
        for task in tasks
        if not (task == AutomationTask.GARDEN and request.garden_off)
    )


def install_automation_request(request: RunSetupRequest) -> InstallAutomationRequest:
    return InstallAutomationRequest(
        cwd=request.cwd,
        tasks=request.automation_tasks,
        home=request.home,
        every=request.sync_every,
        quiet=request.sync_quiet,
        garden_every=request.garden_every,
        garden_off=request.garden_off,
        env_path=request.env_path,
        python_executable=request.python_executable,
    )
