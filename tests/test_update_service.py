from datetime import UTC, datetime
from pathlib import Path

from codealmanac.services.runs.models import RunOperation, RunRecord, RunStatus
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


class ScriptedCommandRunner:
    def __init__(self, results: tuple[PackageCommandResult, ...]):
        self.results = list(results)
        self.commands: list[tuple[str, ...]] = []

    def run(self, command: tuple[str, ...]) -> PackageCommandResult:
        self.commands.append(command)
        if self.results:
            return self.results.pop(0)
        return PackageCommandResult(exit_code=0)


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


def test_scheduled_update_skips_editable_install(tmp_path: Path):
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
        state_dir=tmp_path / ".codealmanac",
    )

    result = service.run(RunUpdateRequest(scheduled=True))

    assert result.status == UpdateStatus.SKIPPED
    assert result.plan.method == UpdateInstallMethod.EDITABLE
    assert result.message == (
        "scheduled update skipped: editable source install cannot be self-updated"
    )
    assert runner.commands == []


def test_scheduled_update_skips_when_lifecycle_run_is_active(tmp_path: Path):
    state_dir = tmp_path / ".codealmanac"
    write_run_record(state_dir, RunStatus.RUNNING)
    runner = FakeCommandRunner(PackageCommandResult(exit_code=0))
    service = UpdatesService(
        FakeMetadataProvider(PackageInstallMetadata(version="0.1.0", installer="uv")),
        runner,
        state_dir=state_dir,
    )

    result = service.run(RunUpdateRequest(scheduled=True))

    assert result.status == UpdateStatus.SKIPPED
    assert result.message == "scheduled update skipped: 1 CodeAlmanac job is active"
    assert runner.commands == []
    assert not (state_dir / "update.lock").exists()


def test_scheduled_update_skips_when_update_lock_is_held(tmp_path: Path):
    state_dir = tmp_path / ".codealmanac"
    state_dir.mkdir()
    (state_dir / "update.lock").write_text(
        '{"pid": 1, "created_at": "2099-01-01T00:00:00Z"}',
        encoding="utf-8",
    )
    runner = FakeCommandRunner(PackageCommandResult(exit_code=0))
    service = UpdatesService(
        FakeMetadataProvider(PackageInstallMetadata(version="0.1.0", installer="uv")),
        runner,
        state_dir=state_dir,
    )

    result = service.run(
        RunUpdateRequest(
            scheduled=True,
            now=datetime(2026, 7, 6, tzinfo=UTC),
        )
    )

    assert result.status == UpdateStatus.SKIPPED
    assert result.message == "scheduled update skipped: update already in progress"
    assert runner.commands == []
    assert (state_dir / "update.lock").exists()


def test_scheduled_update_runs_smoke_after_success(tmp_path: Path):
    runner = ScriptedCommandRunner(
        (
            PackageCommandResult(exit_code=0, stdout="updated\n"),
            PackageCommandResult(exit_code=0, stdout="codealmanac 0.2.0\n"),
            PackageCommandResult(exit_code=0, stdout='{"checks":[]}\n'),
        )
    )
    service = UpdatesService(
        FakeMetadataProvider(PackageInstallMetadata(version="0.1.0", installer="uv")),
        runner,
        state_dir=tmp_path / ".codealmanac",
    )

    result = service.run(RunUpdateRequest(scheduled=True))

    assert result.status == UpdateStatus.COMPLETED
    assert runner.commands == [
        ("uv", "tool", "upgrade", "codealmanac"),
        ("codealmanac", "--version"),
        ("codealmanac", "doctor", "--json"),
    ]
    assert tuple(smoke.exit_code for smoke in result.smoke) == (0, 0)
    assert not (tmp_path / ".codealmanac/update.lock").exists()


def test_scheduled_update_fails_when_smoke_fails(tmp_path: Path):
    runner = ScriptedCommandRunner(
        (
            PackageCommandResult(exit_code=0, stdout="updated\n"),
            PackageCommandResult(exit_code=1, stderr="broken\n"),
            PackageCommandResult(exit_code=0, stdout='{"checks":[]}\n'),
        )
    )
    service = UpdatesService(
        FakeMetadataProvider(PackageInstallMetadata(version="0.1.0", installer="uv")),
        runner,
        state_dir=tmp_path / ".codealmanac",
    )

    result = service.run(RunUpdateRequest(scheduled=True))

    assert result.status == UpdateStatus.FAILED
    assert tuple(smoke.exit_code for smoke in result.smoke) == (1, 0)


def update_service(metadata: PackageInstallMetadata) -> UpdatesService:
    return UpdatesService(
        FakeMetadataProvider(metadata),
        FakeCommandRunner(PackageCommandResult(exit_code=0)),
    )


def write_run_record(state_dir: Path, status: RunStatus) -> None:
    path = state_dir / "repos/repo-id/runs/run_active.json"
    path.parent.mkdir(parents=True)
    now = datetime(2026, 7, 6, tzinfo=UTC)
    record = RunRecord(
        run_id="run_active",
        workspace_id="repo-id",
        operation=RunOperation.INGEST,
        status=status,
        title="Active run",
        created_at=now,
        updated_at=now,
        log_path=Path("runs/run_active.jsonl"),
    )
    path.write_text(record.model_dump_json(indent=2), encoding="utf-8")
