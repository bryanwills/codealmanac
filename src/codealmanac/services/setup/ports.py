from typing import Protocol

from codealmanac.services.automation.models import (
    AutomationInstallResult,
    AutomationUninstallResult,
)
from codealmanac.services.automation.requests import (
    InstallAutomationRequest,
    UninstallAutomationRequest,
)
from codealmanac.services.setup.models import InstructionChange, SetupTarget


class InstructionInstaller(Protocol):
    def install(
        self,
        targets: tuple[SetupTarget, ...],
    ) -> tuple[InstructionChange, ...]:
        pass

    def uninstall(
        self,
        targets: tuple[SetupTarget, ...],
    ) -> tuple[InstructionChange, ...]:
        pass


class SetupAutomationManager(Protocol):
    def install(self, request: InstallAutomationRequest) -> AutomationInstallResult:
        pass

    def uninstall(
        self,
        request: UninstallAutomationRequest,
    ) -> AutomationUninstallResult:
        pass
