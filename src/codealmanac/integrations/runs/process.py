import subprocess
from pathlib import Path

from codealmanac.runs.ledger.models import RunWorkerSpawnResult
from codealmanac.runs.ledger.requests import SpawnRunWorkerRequest


class SubprocessRunWorkerSpawner:
    def spawn(self, request: SpawnRunWorkerRequest) -> RunWorkerSpawnResult:
        command = worker_command(request)
        child = subprocess.Popen(
            command,
            cwd=request.cwd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        return RunWorkerSpawnResult(
            child_pid=child.pid,
            command=tuple(command),
        )


def worker_command(request: SpawnRunWorkerRequest) -> list[str]:
    command = [
        "codealmanac-run-worker",
        "--cwd",
        str(Path(request.cwd)),
    ]
    if request.wiki is not None:
        command.extend(("--wiki", request.wiki))
    return command
