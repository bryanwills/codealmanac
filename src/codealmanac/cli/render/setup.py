import sys

from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from codealmanac.services.setup.models import (
    InstructionChange,
    SetupResult,
    UninstallResult,
)


def render_setup_text(result: SetupResult) -> None:
    console = setup_console()
    console.print(
        setup_panel(
            "CodeAlmanac setup",
            "Local repo wiki, maintained by coding agents.",
        )
    )
    if result.skipped_instructions:
        console.print(status_panel("Instructions skipped", "No files changed."))
        return
    console.print(changes_panel("Agent instructions", result.changes))
    console.print(
        next_steps_panel(
            (
                "codealmanac init",
                'codealmanac search "getting"',
                "codealmanac automation install sync --every 5h --quiet 30m",
            )
        )
    )


def render_uninstall_text(result: UninstallResult) -> None:
    console = setup_console()
    console.print(setup_panel("CodeAlmanac uninstall", "Remove setup-owned files."))
    if result.kept_instructions:
        console.print(status_panel("Instructions kept", "No files changed."))
        return
    console.print(changes_panel("Removed artifacts", result.changes))


def setup_panel(title: str, subtitle: str) -> Panel:
    heading = Text(title, style="bold")
    body = Group(heading, Text(subtitle))
    return Panel(body, border_style="blue", padding=(1, 2))


def status_panel(title: str, message: str) -> Panel:
    body = Group(Text(title, style="bold"), Text(message))
    return Panel(body, border_style="dim", padding=(1, 2))


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


def next_steps_panel(commands: tuple[str, ...]) -> Panel:
    table = Table.grid()
    for command in commands:
        table.add_row(Text(command, style="bold cyan"))
    return Panel(
        Group(Text("Next steps", style="bold"), table),
        border_style="green",
        padding=(1, 2),
    )


def change_status(change: InstructionChange) -> str:
    return "changed" if change.changed else "ok"


def setup_console() -> Console:
    return Console(file=sys.stdout, highlight=False)
