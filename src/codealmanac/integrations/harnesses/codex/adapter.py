import subprocess
import tempfile
from pathlib import Path

from codealmanac.integrations.harnesses.command import (
    CommandRunner,
    SubprocessCommandRunner,
    first_line,
)
from codealmanac.integrations.harnesses.git_status import (
    changed_paths,
    git_status_snapshot,
)
from codealmanac.services.harnesses.models import (
    HarnessKind,
    HarnessReadiness,
    HarnessRunResult,
    HarnessRunStatus,
)
from codealmanac.services.harnesses.requests import RunHarnessRequest

CODEX_COMMAND = "codex"
CODEX_RUN_TIMEOUT_SECONDS = 900
CODEX_STATUS_TIMEOUT_SECONDS = 10


class CodexCliHarnessAdapter:
    kind = HarnessKind.CODEX

    def __init__(
        self,
        runner: CommandRunner | None = None,
        command: str = CODEX_COMMAND,
        run_timeout_seconds: int = CODEX_RUN_TIMEOUT_SECONDS,
        status_timeout_seconds: int = CODEX_STATUS_TIMEOUT_SECONDS,
    ):
        self.runner = runner or SubprocessCommandRunner()
        self.command = command
        self.run_timeout_seconds = run_timeout_seconds
        self.status_timeout_seconds = status_timeout_seconds

    def check(self) -> HarnessReadiness:
        try:
            result = self.runner.run(
                self.command,
                ("login", "status"),
                Path.cwd(),
                self.status_timeout_seconds,
            )
        except FileNotFoundError:
            return HarnessReadiness(
                kind=self.kind,
                available=False,
                message="codex not found on PATH",
            )
        except subprocess.TimeoutExpired:
            return HarnessReadiness(
                kind=self.kind,
                available=False,
                message="codex login status timed out",
            )
        if result.returncode != 0:
            return HarnessReadiness(
                kind=self.kind,
                available=False,
                message=first_line(result.stderr, result.stdout)
                or f"codex login status exited {result.returncode}",
            )
        return HarnessReadiness(
            kind=self.kind,
            available=True,
            message=first_line(result.stdout, result.stderr) or "codex authenticated",
        )

    def run(self, request: RunHarnessRequest) -> HarnessRunResult:
        before = git_status_snapshot(self.runner, request.cwd)
        try:
            with tempfile.TemporaryDirectory(prefix="codealmanac-codex-") as tempdir:
                output_path = Path(tempdir) / "last-message.txt"
                result = self.runner.run(
                    self.command,
                    codex_exec_args(request.cwd, output_path),
                    request.cwd,
                    self.run_timeout_seconds,
                    request.prompt,
                )
                output_text = output_file_text(output_path)
        except FileNotFoundError:
            return failed_result("codex not found on PATH")
        except subprocess.TimeoutExpired:
            return failed_result("codex run timed out")
        after = git_status_snapshot(self.runner, request.cwd)
        changed_files = changed_paths(request.cwd, before, after)
        if result.returncode != 0:
            return failed_result(
                first_line(result.stderr, result.stdout)
                or f"codex exited {result.returncode}",
                changed_files,
            )
        if output_text == "":
            return failed_result(
                first_line(result.stdout, result.stderr)
                or "codex produced no final message",
                changed_files,
            )
        return HarnessRunResult(
            kind=self.kind,
            status=HarnessRunStatus.SUCCEEDED,
            output_text=output_text,
            summary=first_line(output_text),
            changed_files=changed_files,
        )


def codex_exec_args(cwd: Path, output_path: Path) -> tuple[str, ...]:
    return (
        "exec",
        "--config",
        "mcp_servers={}",
        "--config",
        'approval_policy="never"',
        "--cd",
        str(cwd),
        "--ephemeral",
        "--sandbox",
        "workspace-write",
        "--ignore-rules",
        "--color",
        "never",
        "--output-last-message",
        str(output_path),
        "-",
    )


def output_file_text(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8").strip()


def failed_result(
    output_text: str,
    changed_files: tuple[Path, ...] = (),
) -> HarnessRunResult:
    return HarnessRunResult(
        kind=HarnessKind.CODEX,
        status=HarnessRunStatus.FAILED,
        output_text=output_text,
        changed_files=changed_files,
    )
