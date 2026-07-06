from pathlib import Path

from codealmanac.core.errors import ValidationFailed
from codealmanac.services.health.models import ValidationIssue, ValidationResult
from codealmanac.services.health.reports import (
    health_report_issues,
    validation_failure_message,
)
from codealmanac.services.health.requests import HealthCheckRequest, ValidateWikiRequest
from codealmanac.services.health.runtime import runtime_state_issues
from codealmanac.services.health.sources import source_shape_issues
from codealmanac.services.index.models import HealthReport, IndexRefreshResult
from codealmanac.services.index.service import IndexService
from codealmanac.services.workspaces.models import Workspace
from codealmanac.services.workspaces.requests import SelectWorkspaceRequest
from codealmanac.services.workspaces.service import WorkspacesService


class HealthService:
    def __init__(self, workspaces: WorkspacesService, index: IndexService):
        self.workspaces = workspaces
        self.index = index

    def check(self, request: HealthCheckRequest) -> HealthReport:
        workspace = self.select_workspace(request.cwd, request.wiki)
        return self.index.health_report(workspace.workspace_id)

    def validate(self, request: ValidateWikiRequest) -> ValidationResult:
        workspace = self.select_workspace(request.cwd, request.wiki)
        return self.validate_workspace(workspace)

    def validate_workspace(self, workspace: Workspace) -> ValidationResult:
        issues = [
            *source_shape_issues(workspace.almanac_path),
            *runtime_state_issues(workspace.almanac_path),
        ]
        index = None
        try:
            index = self.index.ensure_fresh(workspace.workspace_id)
        except ValidationFailed as error:
            issues.append(
                ValidationIssue(
                    category="page_routes",
                    message=str(error),
                    path=workspace.almanac_root.as_posix(),
                )
            )
            return validation_result(workspace, index, issues)
        issues.extend(
            health_report_issues(self.index.health_report(workspace.workspace_id))
        )
        return validation_result(workspace, index, issues)

    def ensure_valid(self, workspace: Workspace) -> ValidationResult:
        result = self.validate_workspace(workspace)
        if not result.ok:
            raise ValidationFailed(validation_failure_message(result))
        return result

    def select_workspace(self, cwd: Path, wiki: str | None) -> Workspace:
        if wiki is None:
            return self.workspaces.resolve(cwd)
        return self.workspaces.select(
            SelectWorkspaceRequest(selector=wiki, base_path=cwd)
        )


def validation_result(
    workspace: Workspace,
    index: IndexRefreshResult | None,
    issues: list[ValidationIssue],
) -> ValidationResult:
    return ValidationResult(
        workspace_name=workspace.name,
        almanac_path=workspace.almanac_path,
        index=index,
        issues=tuple(issues),
        ok=len(issues) == 0,
    )
