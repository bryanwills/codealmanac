import re

from codealmanac.cli.syntax.catalog import CommandCatalog
from codealmanac.cli.syntax.models import (
    SyntaxProblem,
    SyntaxProblemKind,
)

INVALID_CHOICE_RE = re.compile(r"invalid choice: '([^']+)'")
UNRECOGNIZED_RE = re.compile(r"unrecognized arguments: (.+)")
REQUIRED_RE = re.compile(r"the following arguments are required: (.+)")


def classify_syntax_problem(
    argv: tuple[str, ...],
    message: str,
    catalog: CommandCatalog,
) -> SyntaxProblem:
    guide = catalog.guide_for_argv(argv)
    token = problem_token(message)
    kind = problem_kind(argv, message, guide.path, token)
    replacement = catalog.replacement_for(guide, token)
    return SyntaxProblem(
        kind=kind,
        typed=("codealmanac", *argv),
        guide=guide,
        token=token,
        replacement=replacement,
        detail=problem_detail(message, token, replacement),
    )


def problem_token(message: str) -> str | None:
    invalid_choice = INVALID_CHOICE_RE.search(message)
    if invalid_choice is not None:
        return invalid_choice.group(1)
    unrecognized = UNRECOGNIZED_RE.search(message)
    if unrecognized is not None:
        return unrecognized.group(1).split()[0]
    required = REQUIRED_RE.search(message)
    if required is not None:
        return required.group(1).split(",")[0].strip()
    return None


def problem_kind(
    argv: tuple[str, ...],
    message: str,
    guide_path: tuple[str, ...],
    token: str | None,
) -> SyntaxProblemKind:
    if REQUIRED_RE.search(message) is not None:
        return SyntaxProblemKind.MISSING_ARGUMENT
    if UNRECOGNIZED_RE.search(message) is not None:
        if token is not None and token.startswith("-"):
            return SyntaxProblemKind.UNKNOWN_OPTION
        return SyntaxProblemKind.UNKNOWN_ACTION
    if INVALID_CHOICE_RE.search(message) is not None:
        if message.startswith("argument --"):
            return SyntaxProblemKind.INVALID_VALUE
        if guide_path == () and len(argv) > 0 and argv[0] == token:
            return SyntaxProblemKind.UNKNOWN_COMMAND
        return SyntaxProblemKind.UNKNOWN_ACTION
    return SyntaxProblemKind.INVALID_VALUE


def problem_detail(
    message: str,
    token: str | None,
    replacement: str | None,
) -> str | None:
    if replacement is not None:
        return None
    if token is None:
        return clean_message(message)
    return None


def clean_message(message: str) -> str:
    return " ".join(message.strip().split())
