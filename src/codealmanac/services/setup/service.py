from codealmanac.services.automation.defaults import (
    DEFAULT_GARDEN_INTERVAL,
    DEFAULT_SYNC_INTERVAL,
    duration_text,
)
from codealmanac.services.automation.models import AutomationTask
from codealmanac.services.config.models import DEFAULT_HARNESS, DEFAULT_SYNC_QUIET
from codealmanac.services.setup.models import (
    SetupAutomationRecommendation,
    SetupCommand,
    SetupPlan,
    SetupResult,
    UninstallResult,
)
from codealmanac.services.setup.ports import InstructionInstaller
from codealmanac.services.setup.requests import RunSetupRequest, RunUninstallRequest


class SetupService:
    def __init__(self, instructions: InstructionInstaller):
        self._instructions = instructions

    def run(self, request: RunSetupRequest) -> SetupResult:
        plan = setup_plan(request)
        if request.skip_instructions:
            return SetupResult(plan=plan, skipped_instructions=True)
        return SetupResult(
            plan=plan,
            changes=self._instructions.install(request.targets),
        )

    def uninstall(self, request: RunUninstallRequest) -> UninstallResult:
        if request.keep_instructions:
            return UninstallResult(kept_instructions=True)
        return UninstallResult(changes=self._instructions.uninstall(request.targets))


def setup_plan(request: RunSetupRequest) -> SetupPlan:
    automation = automation_recommendations()
    return SetupPlan(
        default_harness=DEFAULT_HARNESS,
        instruction_targets=request.targets,
        automation=automation,
        next_commands=next_commands(automation),
    )


def automation_recommendations() -> tuple[SetupAutomationRecommendation, ...]:
    sync_every = duration_text(DEFAULT_SYNC_INTERVAL)
    sync_quiet = duration_text(DEFAULT_SYNC_QUIET)
    garden_every = duration_text(DEFAULT_GARDEN_INTERVAL)
    return (
        SetupAutomationRecommendation(
            task=AutomationTask.SYNC,
            description="scan quiet local agent transcripts and ingest durable changes",
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
        ),
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
        ),
    )


def next_commands(
    automation: tuple[SetupAutomationRecommendation, ...],
) -> tuple[SetupCommand, ...]:
    return (
        SetupCommand(label="Initialize this repo", command=("codealmanac", "init")),
        SetupCommand(
            label="Read the starter page",
            command=("codealmanac", "search", "getting"),
        ),
        SetupCommand(
            label="Install scheduled transcript sync",
            command=automation[0].command,
        ),
    )
