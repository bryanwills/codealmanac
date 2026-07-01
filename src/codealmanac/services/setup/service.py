from codealmanac.services.setup.models import SetupResult, UninstallResult
from codealmanac.services.setup.ports import InstructionInstaller
from codealmanac.services.setup.requests import RunSetupRequest, RunUninstallRequest


class SetupService:
    def __init__(self, instructions: InstructionInstaller):
        self._instructions = instructions

    def run(self, request: RunSetupRequest) -> SetupResult:
        if request.skip_instructions:
            return SetupResult(skipped_instructions=True)
        return SetupResult(changes=self._instructions.install(request.targets))

    def uninstall(self, request: RunUninstallRequest) -> UninstallResult:
        if request.keep_instructions:
            return UninstallResult(kept_instructions=True)
        return UninstallResult(changes=self._instructions.uninstall(request.targets))
