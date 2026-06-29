from pathlib import Path

from codealmanac.services.updates.models import (
    PackageCommandResult,
    PackageInstallMetadata,
    UpdateInstallMethod,
    UpdateStatus,
)
from codealmanac.services.updates.requests import CheckUpdateRequest, RunUpdateRequest
from codealmanac.services.updates.service import UpdatesService


class FakeMetadataProvider:
    def __init__(self, metadata: PackageInstallMetadata):
        self.metadata = metadata

    def read(self) -> PackageInstallMetadata:
        return self.metadata


class FakeCommandRunner:
    def __init__(self, result: PackageCommandResult):
        self.result = result
        self.commands: list[tuple[str, ...]] = []

    def run(self, command: tuple[str, ...]) -> PackageCommandResult:
        self.commands.append(command)
        return self.result


def test_update_service_plans_uv_tool_upgrade():
    service = update_service(
        PackageInstallMetadata(version="0.1.0", installer="uv"),
    )

    plan = service.check(CheckUpdateRequest())

    assert plan.status == UpdateStatus.READY
    assert plan.method == UpdateInstallMethod.UV_TOOL
    assert plan.command == ("uv", "tool", "upgrade", "codealmanac")


def test_update_service_plans_pip_upgrade_with_current_python():
    service = update_service(
        PackageInstallMetadata(
            version="0.1.0",
            installer="pip",
            python_executable=Path("/venv/bin/python"),
        ),
    )

    plan = service.check(CheckUpdateRequest())

    assert plan.status == UpdateStatus.READY
    assert plan.method == UpdateInstallMethod.PIP
    assert plan.command == (
        "/venv/bin/python",
        "-m",
        "pip",
        "install",
        "--upgrade",
        "codealmanac",
    )


def test_update_service_refuses_editable_install_without_running_command():
    runner = FakeCommandRunner(PackageCommandResult(exit_code=0))
    service = UpdatesService(
        FakeMetadataProvider(
            PackageInstallMetadata(
                version="0.1.0",
                installer="uv",
                editable=True,
                source_url="file:///repo",
            )
        ),
        runner,
    )

    result = service.run(RunUpdateRequest())

    assert result.status == UpdateStatus.UNSUPPORTED
    assert result.plan.method == UpdateInstallMethod.EDITABLE
    assert result.plan.fix == "run: git pull && uv sync"
    assert runner.commands == []


def test_update_service_returns_failed_result_from_executor():
    runner = FakeCommandRunner(
        PackageCommandResult(exit_code=2, stdout="out\n", stderr="err\n")
    )
    service = UpdatesService(
        FakeMetadataProvider(PackageInstallMetadata(version="0.1.0", installer="uv")),
        runner,
    )

    result = service.run(RunUpdateRequest())

    assert result.status == UpdateStatus.FAILED
    assert result.exit_code == 2
    assert result.stdout == "out\n"
    assert result.stderr == "err\n"
    assert runner.commands == [("uv", "tool", "upgrade", "codealmanac")]


def test_update_service_returns_completed_result_from_executor_success():
    runner = FakeCommandRunner(
        PackageCommandResult(exit_code=0, stderr="Nothing to upgrade\n")
    )
    service = UpdatesService(
        FakeMetadataProvider(PackageInstallMetadata(version="0.1.0", installer="uv")),
        runner,
    )

    result = service.run(RunUpdateRequest())

    assert result.status == UpdateStatus.COMPLETED
    assert result.exit_code == 0
    assert result.stderr == "Nothing to upgrade\n"
    assert runner.commands == [("uv", "tool", "upgrade", "codealmanac")]


def update_service(metadata: PackageInstallMetadata) -> UpdatesService:
    return UpdatesService(
        FakeMetadataProvider(metadata),
        FakeCommandRunner(PackageCommandResult(exit_code=0)),
    )
