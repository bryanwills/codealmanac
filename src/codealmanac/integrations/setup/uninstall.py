import shutil
from pathlib import Path

from codealmanac.core.paths import global_state_dir
from codealmanac.services.setup.models import (
    GlobalStateRemovalResult,
    PackageUninstallResult,
    PackageUninstallStatus,
)
from codealmanac.services.updates.models import (
    PACKAGE_NAME,
    UpdateInstallMethod,
)
from codealmanac.services.updates.ports import (
    PackageCommandRunner,
    PackageInstallMetadataProvider,
)
from codealmanac.services.updates.service import update_method


class FilesystemGlobalStateRemover:
    def __init__(self, state_dir: Path | None = None):
        self._state_dir = state_dir

    def remove(self) -> GlobalStateRemovalResult:
        path = self._state_dir or global_state_dir()
        if not path.exists() and not path.is_symlink():
            return GlobalStateRemovalResult(
                path=path,
                removed=False,
                message="global state not found",
            )
        if path.is_symlink() or path.is_file():
            path.unlink()
        else:
            shutil.rmtree(path)
        return GlobalStateRemovalResult(
            path=path,
            removed=True,
            message="removed global state",
        )


class PackageToolUninstaller:
    def __init__(
        self,
        metadata: PackageInstallMetadataProvider,
        runner: PackageCommandRunner,
    ):
        self._metadata = metadata
        self._runner = runner

    def uninstall(self) -> PackageUninstallResult:
        metadata = self._metadata.read()
        method = update_method(metadata)
        command = package_uninstall_command(method, metadata.python_executable)
        if len(command) == 0:
            return PackageUninstallResult(
                status=PackageUninstallStatus.SKIPPED,
                method=method,
                message=unsupported_uninstall_message(method),
            )
        output = self._runner.run(command)
        if output.exit_code != 0:
            return PackageUninstallResult(
                status=PackageUninstallStatus.FAILED,
                method=method,
                command=command,
                exit_code=output.exit_code,
                stdout=output.stdout,
                stderr=output.stderr,
                message="package uninstall failed",
            )
        return PackageUninstallResult(
            status=PackageUninstallStatus.REMOVED,
            method=method,
            command=command,
            exit_code=output.exit_code,
            stdout=output.stdout,
            stderr=output.stderr,
            message="removed installed CodeAlmanac tool",
        )


def package_uninstall_command(
    method: UpdateInstallMethod,
    python_executable: Path,
) -> tuple[str, ...]:
    if method == UpdateInstallMethod.UV_TOOL:
        return ("uv", "tool", "uninstall", PACKAGE_NAME)
    if method == UpdateInstallMethod.PIP:
        return (
            str(python_executable),
            "-m",
            "pip",
            "uninstall",
            "-y",
            PACKAGE_NAME,
        )
    return ()


def unsupported_uninstall_message(method: UpdateInstallMethod) -> str:
    if method == UpdateInstallMethod.EDITABLE:
        return "editable source install cannot be self-uninstalled"
    return "unknown package installer; skipped package uninstall"
