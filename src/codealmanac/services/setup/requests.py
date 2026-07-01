from pydantic import field_validator

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.services.setup.models import SetupTarget

DEFAULT_SETUP_TARGETS = (SetupTarget.CODEX, SetupTarget.CLAUDE)


class RunSetupRequest(CodeAlmanacModel):
    targets: tuple[SetupTarget, ...] = DEFAULT_SETUP_TARGETS
    yes: bool = False
    skip_instructions: bool = False

    @field_validator("targets")
    @classmethod
    def validate_targets(
        cls,
        value: tuple[SetupTarget, ...],
    ) -> tuple[SetupTarget, ...]:
        return unique_non_empty_targets(value)


class RunUninstallRequest(CodeAlmanacModel):
    targets: tuple[SetupTarget, ...] = DEFAULT_SETUP_TARGETS
    yes: bool = False
    keep_instructions: bool = False

    @field_validator("targets")
    @classmethod
    def validate_targets(
        cls,
        value: tuple[SetupTarget, ...],
    ) -> tuple[SetupTarget, ...]:
        return unique_non_empty_targets(value)


def unique_non_empty_targets(
    targets: tuple[SetupTarget, ...],
) -> tuple[SetupTarget, ...]:
    unique: list[SetupTarget] = []
    for target in targets:
        if target not in unique:
            unique.append(target)
    if len(unique) == 0:
        raise ValueError("at least one setup target is required")
    return tuple(unique)
