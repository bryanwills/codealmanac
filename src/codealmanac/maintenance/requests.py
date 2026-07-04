from enum import StrEnum
from pathlib import Path

from pydantic import field_validator, model_validator

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.core.text import required_text
from codealmanac.engine.harnesses.models import HarnessKind
from codealmanac.wiki.workspaces.roots import validate_almanac_root_field


class MaintenanceRunKind(StrEnum):
    INIT = "init"
    INGEST = "ingest"


class RunMaintenanceRequest(CodeAlmanacModel):
    kind: MaintenanceRunKind
    cwd: Path
    inputs: tuple[str, ...] = ()
    harness: HarnessKind = HarnessKind.CODEX
    almanac_root: Path | None = None
    name: str | None = None
    description: str = ""
    title: str | None = None
    guidance: str | None = None
    force: bool = False

    @field_validator("inputs")
    @classmethod
    def require_input_text(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        for item in value:
            required_text(item, "maintenance input")
        return value

    @field_validator("almanac_root")
    @classmethod
    def validate_almanac_root(cls, value: Path | None) -> Path | None:
        if value is None:
            return None
        return validate_almanac_root_field(value)

    @field_validator("name", "title", "guidance")
    @classmethod
    def require_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return required_text(value, "maintenance request text")

    @model_validator(mode="after")
    def validate_kind_payload(self) -> "RunMaintenanceRequest":
        if self.kind == MaintenanceRunKind.INIT:
            if len(self.inputs) > 0:
                raise ValueError("init maintenance request does not accept inputs")
            return self
        if self.kind == MaintenanceRunKind.INGEST:
            if len(self.inputs) == 0:
                raise ValueError("ingest maintenance request requires inputs")
            if self.almanac_root is not None:
                raise ValueError(
                    "ingest maintenance request does not accept almanac_root"
                )
            if self.name is not None:
                raise ValueError("ingest maintenance request does not accept name")
            if self.description:
                raise ValueError(
                    "ingest maintenance request does not accept description"
                )
            if self.force:
                raise ValueError("ingest maintenance request does not accept force")
            return self
        raise ValueError(f"unsupported maintenance kind: {self.kind.value}")
