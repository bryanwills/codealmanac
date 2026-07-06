import argparse
import os
import sys
import termios
import tty
from dataclasses import dataclass

from codealmanac.cli.render.setup import (
    SetupChoiceOption,
    SetupChoiceScreen,
    render_setup_choice_screen,
)
from codealmanac.services.setup.models import SetupTarget


@dataclass(frozen=True)
class SetupSelections:
    targets: tuple[SetupTarget, ...]
    auto_update: bool
    auto_commit: bool
    sync_off: bool
    garden_off: bool


class SetupCancelled(Exception):
    pass


def resolve_setup_selections(args: argparse.Namespace) -> SetupSelections:
    defaults = default_setup_selections(args)
    if args.yes or args.json or not supports_interactive_setup():
        return defaults
    return interactive_setup_selections(defaults)


def default_setup_selections(args: argparse.Namespace) -> SetupSelections:
    return SetupSelections(
        targets=parse_setup_targets(args.target),
        auto_update=not args.no_auto_update,
        auto_commit=not args.no_auto_commit,
        sync_off=args.sync_off,
        garden_off=args.garden_off,
    )


def supports_interactive_setup() -> bool:
    return sys.stdin.isatty() and sys.stdout.isatty()


def interactive_setup_selections(defaults: SetupSelections) -> SetupSelections:
    target_index = choose_setup_option(
        SetupChoiceScreen(
            step=1,
            title="Agent instructions",
            question="Install CodeAlmanac instructions for:",
            options=target_options(),
        ),
        initial_index=target_default_index(defaults.targets),
    )
    maintenance_index = choose_setup_option(
        SetupChoiceScreen(
            step=2,
            title="Wiki maintenance",
            question="How should your wikis be updated?",
            options=maintenance_options(),
        ),
        initial_index=1 if defaults.sync_off and defaults.garden_off else 0,
    )
    update_index = choose_setup_option(
        SetupChoiceScreen(
            step=3,
            title="Product updates",
            question="Keep CodeAlmanac up to date automatically?",
            options=update_options(),
        ),
        initial_index=0 if defaults.auto_update else 1,
    )
    change_index = choose_setup_option(
        SetupChoiceScreen(
            step=4,
            title="Agent change handling",
            question="Should agents commit wiki changes or leave them in the worktree?",
            options=change_options(),
            visual="change-handling",
        ),
        initial_index=0 if defaults.auto_commit else 1,
    )
    return SetupSelections(
        targets=targets_for_index(target_index),
        auto_update=update_index == 0,
        auto_commit=change_index == 0,
        sync_off=maintenance_index == 1,
        garden_off=maintenance_index == 1,
    )


def target_options() -> tuple[SetupChoiceOption, ...]:
    return (
        SetupChoiceOption(
            "Codex + Claude",
            (),
            ("b",),
        ),
        SetupChoiceOption(
            "Codex only",
            (),
            ("c",),
        ),
        SetupChoiceOption(
            "Claude only",
            (),
            ("l",),
        ),
    )


def maintenance_options() -> tuple[SetupChoiceOption, ...]:
    return (
        SetupChoiceOption("Automatic", ()),
        SetupChoiceOption("Manual", ()),
    )


def update_options() -> tuple[SetupChoiceOption, ...]:
    return (
        SetupChoiceOption("Automatic", ()),
        SetupChoiceOption("Manual", ()),
    )


def change_options() -> tuple[SetupChoiceOption, ...]:
    return (
        SetupChoiceOption("Commit changes", ()),
        SetupChoiceOption("Leave in worktree", ()),
    )


def choose_setup_option(screen: SetupChoiceScreen, initial_index: int) -> int:
    selected_index = initial_index
    while True:
        render_setup_choice_screen(screen, selected_index)
        key = read_setup_key()
        if key in {"\x03", "q"}:
            raise SetupCancelled()
        if key in {"\r", "\n"}:
            return selected_index
        shortcut_index = shortcut_option_index(screen, key)
        if shortcut_index is not None:
            return shortcut_index
        if key in {"\x1b[D", "a"}:
            selected_index = (selected_index - 1) % len(screen.options)
        elif key in {"\x1b[C", "d"}:
            selected_index = (selected_index + 1) % len(screen.options)


def read_setup_key() -> str:
    fd = sys.stdin.fileno()
    previous = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        key = os.read(fd, 1).decode("utf-8", errors="ignore")
        if key == "\x1b":
            key += os.read(fd, 2).decode("utf-8", errors="ignore")
        return key
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, previous)


def shortcut_option_index(screen: SetupChoiceScreen, key: str) -> int | None:
    normalized = key.casefold()
    for index, option in enumerate(screen.options):
        if normalized in option.shortcuts:
            return index
    return None


def target_default_index(targets: tuple[SetupTarget, ...]) -> int:
    if targets == (SetupTarget.CODEX,):
        return 1
    if targets == (SetupTarget.CLAUDE,):
        return 2
    return 0


def targets_for_index(index: int) -> tuple[SetupTarget, ...]:
    if index == 1:
        return (SetupTarget.CODEX,)
    if index == 2:
        return (SetupTarget.CLAUDE,)
    return (SetupTarget.CODEX, SetupTarget.CLAUDE)


def parse_setup_targets(value: str) -> tuple[SetupTarget, ...]:
    if value == "all":
        return (SetupTarget.CODEX, SetupTarget.CLAUDE)
    return (SetupTarget(value),)
