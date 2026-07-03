import subprocess
from pathlib import Path

from codealmanac.cloud.capture.models import CaptureRepositoryState
from codealmanac.core.paths import normalize_path
from codealmanac.integrations.workspaces.git.repository import parse_github_remote

GIT_CAPTURE_TIMEOUT_SECONDS = 10


class GitCaptureRepositoryProbe:
    def read(self, cwd: Path) -> CaptureRepositoryState:
        normalized = normalize_path(cwd)
        root = run_git(normalized, ("rev-parse", "--show-toplevel"))
        if root.returncode != 0:
            return missing_repo(normalized, first_line(root.stderr, root.stdout))
        repository_root = normalize_path(Path(root.stdout.strip()))

        remote = run_git(repository_root, ("remote", "get-url", "origin"))
        if remote.returncode != 0:
            return missing_repo(normalized, first_line(remote.stderr, remote.stdout))
        parsed = parse_github_remote(remote.stdout.strip())
        if parsed is None:
            return missing_repo(normalized, "origin remote is not a GitHub repository")

        head = run_git(repository_root, ("rev-parse", "HEAD"))
        head_sha = head.stdout.strip() if head.returncode == 0 else None
        branch = run_git(repository_root, ("branch", "--show-current"))
        branch_name = branch.stdout.strip() if branch.returncode == 0 else None
        if branch_name == "":
            branch_name = None
        return CaptureRepositoryState(
            cwd=str(normalized),
            repo_available=True,
            repo_full_name=f"{parsed.owner}/{parsed.name}",
            branch=branch_name,
            head_sha=head_sha,
            unavailable_reason=(
                None if branch_name is not None else "detached HEAD has no branch"
            ),
        )


def run_git(cwd: Path, args: tuple[str, ...]) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ("git", *args),
            cwd=cwd,
            text=True,
            capture_output=True,
            timeout=GIT_CAPTURE_TIMEOUT_SECONDS,
            check=False,
        )
    except FileNotFoundError as error:
        return subprocess.CompletedProcess(("git", *args), 127, "", str(error))
    except subprocess.TimeoutExpired as error:
        return subprocess.CompletedProcess(
            ("git", *args),
            124,
            error.stdout or "",
            "git command timed out",
        )


def missing_repo(cwd: Path, reason: str) -> CaptureRepositoryState:
    return CaptureRepositoryState(
        cwd=str(cwd),
        repo_available=False,
        unavailable_reason=reason or "git repository unavailable",
    )


def first_line(*values: str) -> str:
    for value in values:
        lines = [line.strip() for line in value.splitlines() if line.strip()]
        if lines:
            return lines[0]
    return ""
