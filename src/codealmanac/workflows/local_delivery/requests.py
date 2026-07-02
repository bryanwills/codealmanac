from pydantic import field_validator

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.core.text import required_text
from codealmanac.services.runs.models import RunId


class DeliverLocalRunRequest(CodeAlmanacModel):
    run_id: RunId

    @field_validator("run_id")
    @classmethod
    def require_run_id(cls, value: str) -> str:
        return required_text(value, "local delivery run id")
