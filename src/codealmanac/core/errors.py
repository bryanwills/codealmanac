from typing import Literal

ErrorCode = Literal[
    "codealmanac_error",
    "not_found",
    "conflict",
    "validation_failed",
]


class CodeAlmanacError(Exception):
    """Base class for product errors that cross CLI and future server edges."""

    code: ErrorCode = "codealmanac_error"


class NotFoundError(CodeAlmanacError):
    code: ErrorCode = "not_found"

    def __init__(self, resource: str, identifier: str):
        super().__init__(f"{resource} not found: {identifier}")
        self.resource = resource
        self.identifier = identifier


class ConflictError(CodeAlmanacError):
    code: ErrorCode = "conflict"

    def __init__(self, message: str):
        super().__init__(message)


class ValidationFailed(CodeAlmanacError):
    code: ErrorCode = "validation_failed"

    def __init__(self, message: str):
        super().__init__(message)
