from pathlib import Path

from pydantic import field_validator

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.core.text import required_text
from codealmanac.services.control.models import ControlRunRecord
from codealmanac.services.deliveries.models import DeliveryRecord


class LocalDeliveryHead(CodeAlmanacModel):
    branch_name: str
    head_sha: str

    @field_validator("branch_name", "head_sha")
    @classmethod
    def require_text(cls, value: str) -> str:
        return required_text(value, "local delivery head text")


class LocalDeliveryPatch(CodeAlmanacModel):
    patch_text: str
    changed_paths: tuple[Path, ...] = ()

    @field_validator("changed_paths")
    @classmethod
    def require_relative_paths(cls, value: tuple[Path, ...]) -> tuple[Path, ...]:
        for path in value:
            if path.is_absolute() or ".." in path.parts:
                raise ValueError("delivery changed paths must be relative")
        return value

    @property
    def empty(self) -> bool:
        return len(self.changed_paths) == 0


class LocalDeliveryCommit(CodeAlmanacModel):
    commit_sha: str

    @field_validator("commit_sha")
    @classmethod
    def require_commit_sha(cls, value: str) -> str:
        return required_text(value, "local delivery commit sha")


class LocalDeliveryWorkingTree(CodeAlmanacModel):
    changed_paths: tuple[Path, ...] = ()

    @field_validator("changed_paths")
    @classmethod
    def require_relative_paths(cls, value: tuple[Path, ...]) -> tuple[Path, ...]:
        for path in value:
            if path.is_absolute() or ".." in path.parts:
                raise ValueError("working tree delivery paths must be relative")
        return value


class LocalDeliveryResult(CodeAlmanacModel):
    delivered: bool
    reason: str | None = None
    run: ControlRunRecord
    delivery: DeliveryRecord
    commit_sha: str | None = None

    @field_validator("reason", "commit_sha")
    @classmethod
    def require_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return required_text(value, "local delivery result text")
