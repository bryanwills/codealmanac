import sys

from codealmanac.cli.render.style import style, table
from codealmanac.cli.syntax.models import (
    SyntaxProblem,
    SyntaxProblemKind,
)


def render_syntax_problem(problem: SyntaxProblem) -> None:
    err = sys.stderr
    print(f"{style.BLUE}{style.BOLD}◆ codealmanac{style.RST}", file=err)
    print("", file=err)
    print(f"{style.BOLD}{problem_title(problem.kind)}{style.RST}", file=err)
    print("", file=err)
    print(f"{style.DIM}You ran:{style.RST}", file=err)
    print(f"  {typed_command(problem)}", file=err)
    if problem.replacement is not None:
        print("", file=err)
        print(f"{style.DIM}Use this instead:{style.RST}", file=err)
        print(f"  {style.BLUE}{problem.replacement}{style.RST}", file=err)
    elif problem.detail is not None:
        print("", file=err)
        print(problem.detail, file=err)
    print("", file=err)
    print(problem.guide.title, file=err)
    print(problem.guide.summary, file=err)
    print("", file=err)
    for line in table(
        ("COMMAND", "WHAT IT DOES"),
        tuple((row.command, row.description) for row in problem.guide.rows),
    ):
        print(line, file=err)


def problem_title(kind: SyntaxProblemKind) -> str:
    if kind == SyntaxProblemKind.UNKNOWN_COMMAND:
        return "Unknown command"
    if kind == SyntaxProblemKind.UNKNOWN_ACTION:
        return "Unknown command"
    if kind == SyntaxProblemKind.UNKNOWN_OPTION:
        return "Unknown option"
    if kind == SyntaxProblemKind.MISSING_ARGUMENT:
        return "Missing command"
    return "Invalid value"


def typed_command(problem: SyntaxProblem) -> str:
    return " ".join(problem.typed)
