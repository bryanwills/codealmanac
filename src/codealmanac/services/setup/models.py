from enum import StrEnum
from pathlib import Path

from pydantic import Field

from codealmanac.core.models import CodeAlmanacModel


class SetupTarget(StrEnum):
    CODEX = "codex"
    CLAUDE = "claude"


class InstructionChange(CodeAlmanacModel):
    target: SetupTarget
    changed: bool
    paths: tuple[Path, ...] = ()
    message: str = Field(min_length=1)


class SetupResult(CodeAlmanacModel):
    skipped_instructions: bool = False
    changes: tuple[InstructionChange, ...] = ()


class UninstallResult(CodeAlmanacModel):
    kept_instructions: bool = False
    changes: tuple[InstructionChange, ...] = ()
