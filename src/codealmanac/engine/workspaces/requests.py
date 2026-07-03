from pathlib import Path

from pydantic import field_validator

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.core.text import required_text
from codealmanac.engine.run_ids import EngineRunId


class PrepareEngineWorkspaceRequest(CodeAlmanacModel):
    run_id: EngineRunId
    repository_root_path: Path
    expected_head_sha: str

    @field_validator("expected_head_sha")
    @classmethod
    def require_expected_head_sha(cls, value: str) -> str:
        return required_text(value, "engine workspace expected_head_sha")


class ReadEngineWorkspaceRequest(CodeAlmanacModel):
    run_id: EngineRunId


class RemoveEngineWorkspaceRequest(CodeAlmanacModel):
    run_id: EngineRunId
    repository_root_path: Path
