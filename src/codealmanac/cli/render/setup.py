import shlex
import sys
from dataclasses import dataclass

from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from codealmanac.cli.render.common import print_json_model
from codealmanac.services.automation.models import (
    AutomationTask,
    AutomationUninstallResult,
)
from codealmanac.services.setup.models import (
    GlobalStateRemovalResult,
    InstructionChange,
    PackageUninstallResult,
    SetupResult,
    UninstallResult,
)

SETUP_BANNER = (
    "   _____          _        _                         ",
    "  / ____|        | |      / \\                        ",
    " | |     ___   __| | ___ / _ \\   _ __ ___   __ _ ___ ",
    " | |    / _ \\ / _` |/ _ / ___ \\ | '_ ` _ \\ / _` / __|",
    " | |___| (_) | (_| |  __/ ___ \\ | | | | | | (_| \\__ \\",
    "  \\_____\\___/ \\__,_|\\___/_/   \\_\\|_| |_| |_|\\__,_|___/",
)


@dataclass(frozen=True)
class SetupStep:
    label: str
    status: str
    detail: str


def render_setup_result(result: SetupResult, json_output: bool) -> None:
    if json_output:
        print_json_model(result)
        return
    render_setup_text(result)


def render_uninstall_result(result: UninstallResult, json_output: bool) -> None:
    if json_output:
        print_json_model(result)
        return
    render_uninstall_text(result)


def render_setup_text(result: SetupResult) -> None:
    console = setup_console()
    console.print()
    console.print(Text("  CODEALMANAC", style="bold blue"))
    for line in SETUP_BANNER:
        console.print(Text(line, style="bold white"))
    console.print(Text("  Local repo wiki, maintained by coding agents.", style="dim"))
    console.print()
    console.print(Text(" codealmanac ", style="black on white"))
    console.print()
    console.print(setup_steps_panel(result))
    console.print(next_steps_panel(result))


def render_uninstall_text(result: UninstallResult) -> None:
    console = setup_console()
    console.print(setup_panel("CodeAlmanac uninstall", "Remove setup-owned files."))
    console.print(changes_panel("Removed artifacts", result.changes))
    if result.automation_uninstall is not None:
        console.print(automation_uninstall_panel(result.automation_uninstall))
    if result.global_state is not None:
        console.print(global_state_panel(result.global_state))
    if result.package_uninstall is not None:
        console.print(package_uninstall_panel(result.package_uninstall))


def setup_panel(title: str, subtitle: str) -> Panel:
    heading = Text(title, style="bold")
    body = Group(heading, Text(subtitle))
    return Panel(body, border_style="blue", padding=(1, 2))


def changes_panel(title: str, changes: tuple[InstructionChange, ...]) -> Panel:
    table = Table.grid(padding=(0, 2))
    table.add_column("target", style="bold")
    table.add_column("status")
    table.add_column("message")
    for change in changes:
        table.add_row(change.target.value, change_status(change), change.message)
        for path in change.paths:
            table.add_row("", "", str(path))
    return Panel(
        Group(Text(title, style="bold"), table),
        border_style="blue",
        padding=(1, 2),
    )


def setup_steps_panel(result: SetupResult) -> Panel:
    table = Table.grid(padding=(0, 2))
    table.add_column("step", style="bold")
    table.add_column("status")
    table.add_column("detail")
    for index, step in enumerate(setup_steps(result), start=1):
        table.add_row(f"{index}. {step.label}", step.status, step.detail)
    return Panel(
        Group(Text("Setup complete", style="bold"), table),
        border_style="blue",
        padding=(1, 2),
    )


def setup_steps(result: SetupResult) -> tuple[SetupStep, ...]:
    return (
        instruction_step(result),
        automation_step(result, AutomationTask.SYNC, "Sync automation"),
        automation_step(result, AutomationTask.GARDEN, "Garden automation"),
        automation_step(result, AutomationTask.UPDATE, "Update automation"),
        auto_commit_step(result),
    )


def instruction_step(result: SetupResult) -> SetupStep:
    if result.skipped_instructions:
        return SetupStep("Agent instructions", "skipped", "left unchanged")
    changed = any(change.changed for change in result.changes)
    status = "installed" if changed else "ready"
    return SetupStep("Agent instructions", status, instruction_detail(result))


def instruction_detail(result: SetupResult) -> str:
    if len(result.changes) == 0:
        return ", ".join(target.value for target in result.plan.instruction_targets)
    return "; ".join(change.message for change in result.changes)


def automation_step(
    result: SetupResult,
    task: AutomationTask,
    label: str,
) -> SetupStep:
    if result.automation_install is None:
        return SetupStep(label, "skipped", "not requested")
    installed = {job.task for job in result.automation_install.jobs}
    disabled = {job.task for job in result.automation_install.disabled}
    if task in installed:
        return SetupStep(label, "installed", automation_detail(result, task))
    if task in disabled:
        return SetupStep(label, "disabled", "removed existing schedule")
    return SetupStep(label, "skipped", "disabled by setup option")


def automation_detail(result: SetupResult, task: AutomationTask) -> str:
    for recommendation in result.plan.automation:
        if recommendation.task == task:
            return recommendation.description
    return "scheduled"


def auto_commit_step(result: SetupResult) -> SetupStep:
    enabled = result.plan.auto_commit
    status = "on" if enabled else "off"
    detail = "agents may commit wiki changes" if enabled else "agents will not commit"
    return SetupStep("Auto commit", status, detail)


def automation_uninstall_panel(result: AutomationUninstallResult) -> Panel:
    table = Table.grid(padding=(0, 2))
    table.add_column("label", style="bold")
    table.add_column("value")
    if len(result.removed) == 0:
        table.add_row("automation", "not installed")
    for path in result.removed:
        table.add_row("removed", str(path))
    return Panel(
        Group(Text("Scheduled automation", style="bold"), table),
        border_style="blue",
        padding=(1, 2),
    )


def global_state_panel(result: GlobalStateRemovalResult) -> Panel:
    table = Table.grid(padding=(0, 2))
    table.add_column("label", style="bold")
    table.add_column("value")
    table.add_row("status", "removed" if result.removed else "not found")
    table.add_row("path", str(result.path))
    table.add_row("message", result.message)
    return Panel(
        Group(Text("Global state", style="bold"), table),
        border_style="blue",
        padding=(1, 2),
    )


def package_uninstall_panel(result: PackageUninstallResult) -> Panel:
    table = Table.grid(padding=(0, 2))
    table.add_column("label", style="bold")
    table.add_column("value")
    table.add_row("status", result.status.value)
    table.add_row("method", result.method.value)
    table.add_row("message", result.message)
    if len(result.command) > 0:
        table.add_row("command", shell_command(result.command))
    if result.exit_code is not None:
        table.add_row("exit code", str(result.exit_code))
    return Panel(
        Group(Text("Installed tool", style="bold"), table),
        border_style="blue",
        padding=(1, 2),
    )


def next_steps_panel(result: SetupResult) -> Panel:
    table = Table.grid()
    for command in result.plan.next_commands:
        table.add_row(Text(command.label, style="bold"))
        table.add_row(Text(shell_command(command.command), style="cyan"))
    return Panel(
        Group(Text("Next steps", style="bold"), table),
        border_style="green",
        padding=(1, 2),
    )


def change_status(change: InstructionChange) -> str:
    return "changed" if change.changed else "ok"


def shell_command(command: tuple[str, ...]) -> str:
    return shlex.join(command)


def setup_console() -> Console:
    return Console(file=sys.stdout, highlight=False)
