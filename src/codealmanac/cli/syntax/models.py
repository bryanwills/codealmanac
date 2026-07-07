from enum import StrEnum

from pydantic import field_validator

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.core.text import required_text


class SyntaxProblemKind(StrEnum):
    UNKNOWN_COMMAND = "unknown_command"
    UNKNOWN_ACTION = "unknown_action"
    UNKNOWN_OPTION = "unknown_option"
    MISSING_ARGUMENT = "missing_argument"
    INVALID_VALUE = "invalid_value"


class CommandRow(CodeAlmanacModel):
    command: str
    description: str

    @field_validator("command", "description")
    @classmethod
    def require_text(cls, value: str) -> str:
        return required_text(value, "command guide row")


class CommandAlias(CodeAlmanacModel):
    token: str
    replacement: str

    @field_validator("token", "replacement")
    @classmethod
    def require_text(cls, value: str) -> str:
        return required_text(value, "command guide alias")


class CommandGuide(CodeAlmanacModel):
    path: tuple[str, ...]
    title: str
    summary: str
    rows: tuple[CommandRow, ...]
    aliases: tuple[CommandAlias, ...] = ()

    @field_validator("path")
    @classmethod
    def require_path_parts(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        for item in value:
            required_text(item, "command guide path")
        return value

    @field_validator("title", "summary")
    @classmethod
    def require_text(cls, value: str) -> str:
        return required_text(value, "command guide")


class SyntaxProblem(CodeAlmanacModel):
    kind: SyntaxProblemKind
    typed: tuple[str, ...]
    guide: CommandGuide
    token: str | None = None
    replacement: str | None = None
    detail: str | None = None

    @field_validator("typed")
    @classmethod
    def require_typed_parts(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(value) == 0:
            raise ValueError("typed command is required")
        for item in value:
            required_text(item, "typed command")
        return value

    @field_validator("token", "replacement", "detail")
    @classmethod
    def require_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return required_text(value, "syntax problem text")


class CliSyntaxError(Exception):
    def __init__(self, problem: SyntaxProblem):
        super().__init__(problem.kind.value)
        self.problem = problem
