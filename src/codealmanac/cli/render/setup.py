import shlex
import shutil
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

RST = "\x1b[0m"
BOLD = "\x1b[1m"
DIM = "\x1b[2m"
WHITE_BOLD = "\x1b[1;37m"
BLUE = "\x1b[38;5;75m"
BLUE_DIM = "\x1b[38;5;69m"
ACCENT_BG = "\x1b[48;5;252m\x1b[38;5;16m"

GRADIENT = (
    "\x1b[38;5;255m",
    "\x1b[38;5;253m",
    "\x1b[38;5;251m",
    "\x1b[38;5;249m",
    "\x1b[38;5;246m",
    "\x1b[38;5;243m",
)

SETUP_BANNER = (
    " █████╗ ██╗     ███╗   ███╗ █████╗ ███╗   ██╗ █████╗  ██████╗",
    "██╔══██╗██║     ████╗ ████║██╔══██╗████╗  ██║██╔══██╗██╔════╝",
    "███████║██║     ██╔████╔██║███████║██╔██╗ ██║███████║██║     ",
    "██╔══██║██║     ██║╚██╔╝██║██╔══██║██║╚██╗██║██╔══██║██║     ",
    "██║  ██║███████╗██║ ╚═╝ ██║██║  ██║██║ ╚████║██║  ██║╚██████╗",
    "╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝ ╚═════╝",
)

ACCENT_STYLE = "bright_blue"
BAR = f"  {DIM}│{RST}"


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
    print_banner()
    print_badge()
    write_line("")
    write_line(f"  {WHITE_BOLD}Setup complete{RST}")
    write_line(BAR)
    steps = setup_steps(result)
    for index, step in enumerate(steps):
        render_setup_step(step)
        if index < len(steps) - 1:
            write_line(BAR)
    write_line("")
    render_next_steps_box(next_step_lines(result))


def print_banner() -> None:
    write_line("")
    for index, line in enumerate(SETUP_BANNER):
        color = GRADIENT[index]
        write_line(f"{color}{line}{RST}")
    write_line("")
    write_line(
        f"{WHITE_BOLD}  CodeAlmanac is a local codebase wiki,"
        f" maintained by your coding agents.{RST}"
    )
    write_line(
        f"{DIM}  Machine setup only. Repo wikis still start with"
        f" codealmanac init.{RST}"
    )


def print_badge() -> None:
    write_line("")
    write_line(f"   {ACCENT_BG} codealmanac {RST}")


def render_setup_step(step: SetupStep) -> None:
    marker = "◇"
    marker_style = BLUE
    label_style = WHITE_BOLD
    status_style = BLUE
    if step.status in {"skipped", "disabled", "off"}:
        marker = "○"
        marker_style = DIM
        label_style = DIM
        status_style = DIM
    write_line(
        f"  {marker_style}{marker}{RST}  "
        f"{label_style}{step.label}{RST} "
        f"{status_style}{step.status}{RST}"
    )
    for detail in wrap_step_detail(step.detail):
        write_line(detail)


def wrap_step_detail(detail: str) -> tuple[str, ...]:
    width = max(40, terminal_width() - 6)
    return tuple(wrap_with_prefixes(detail, f"{BAR}   ", f"{BAR}   ", width))


def next_step_lines(result: SetupResult) -> tuple[str, ...]:
    lines: list[str] = [
        f"  {WHITE_BOLD}Create almanac/ inside a repo when you are ready.{RST}",
        "",
    ]
    for command in result.plan.next_commands:
        lines.append(f"  {BOLD}{command.label}{RST}")
        lines.append(f"  {BLUE}{shell_command(command.command)}{RST}")
    return tuple(lines)


def render_next_steps_box(lines: tuple[str, ...]) -> None:
    header = f"  {WHITE_BOLD}Next steps{RST}"
    inner_width = box_inner_width((header, *lines))
    empty = box_row("", inner_width)
    write_line(f"  {BLUE_DIM}╭{'─' * inner_width}╮{RST}")
    write_line(empty)
    write_line(box_row(header, inner_width))
    write_line(empty)
    for line in lines:
        write_line(box_row(line, inner_width))
    write_line(empty)
    write_line(f"  {BLUE_DIM}╰{'─' * inner_width}╯{RST}")
    write_line("")


def box_inner_width(contents: tuple[str, ...], min_width: int = 62) -> int:
    available = max(40, terminal_width() - 6)
    widest = max((visible_length(content) for content in contents), default=0)
    return min(max(min_width, widest), available)


def box_row(content: str, inner_width: int) -> str:
    padding = max(0, inner_width - visible_length(content))
    return f"  {BLUE_DIM}│{RST}{content}{' ' * padding}{BLUE_DIM}│{RST}"


def wrap_with_prefixes(
    text: str,
    first_prefix: str,
    next_prefix: str,
    width: int,
) -> tuple[str, ...]:
    words = tuple(word for word in text.split(" ") if len(word) > 0)
    if len(words) == 0:
        return (first_prefix,)
    lines: list[str] = []
    prefix = first_prefix
    line = prefix
    has_word = False
    for word in words:
        candidate = f"{line} {word}" if has_word else f"{prefix}{word}"
        if has_word and visible_length(candidate) > width:
            lines.append(line)
            prefix = next_prefix
            line = f"{prefix}{word}"
            has_word = True
            continue
        line = candidate
        has_word = True
    lines.append(line)
    return tuple(lines)


def visible_length(value: str) -> int:
    count = 0
    in_escape = False
    for character in value:
        if character == "\x1b":
            in_escape = True
            continue
        if in_escape:
            if character == "m":
                in_escape = False
            continue
        count += 1
    return count


def terminal_width() -> int:
    return shutil.get_terminal_size((80, 24)).columns


def write_line(line: str) -> None:
    sys.stdout.write(f"{line}\n")


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
    return Panel(body, border_style=ACCENT_STYLE, padding=(1, 2))


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
        border_style=ACCENT_STYLE,
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
        return SetupStep(label, "installed", installed_automation_detail(result, task))
    if task in disabled:
        return SetupStep(label, "disabled", disabled_automation_detail(task))
    return SetupStep(label, "skipped", skipped_automation_detail(task))


def installed_automation_detail(result: SetupResult, task: AutomationTask) -> str:
    if task == AutomationTask.UPDATE:
        return "permission granted; updater installed"
    return automation_detail(result, task)


def skipped_automation_detail(task: AutomationTask) -> str:
    if task == AutomationTask.UPDATE:
        return "permission not granted; updater skipped"
    return "disabled by setup option"


def disabled_automation_detail(task: AutomationTask) -> str:
    if task == AutomationTask.UPDATE:
        return "permission not granted; updater removed"
    return "removed existing schedule"


def automation_detail(result: SetupResult, task: AutomationTask) -> str:
    for recommendation in result.plan.automation:
        if recommendation.task == task:
            return recommendation.description
    return "scheduled"


def auto_commit_step(result: SetupResult) -> SetupStep:
    enabled = result.plan.auto_commit
    status = "on" if enabled else "off"
    detail = (
        "commit permission in instructions"
        if enabled
        else "commit permission withheld"
    )
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
        border_style=ACCENT_STYLE,
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
        border_style=ACCENT_STYLE,
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
        border_style=ACCENT_STYLE,
        padding=(1, 2),
    )


def change_status(change: InstructionChange) -> str:
    return "changed" if change.changed else "ok"


def shell_command(command: tuple[str, ...]) -> str:
    return shlex.join(command)


def setup_console() -> Console:
    return Console(file=sys.stdout, highlight=False)
