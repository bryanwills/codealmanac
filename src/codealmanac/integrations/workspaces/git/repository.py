import re
import subprocess
from pathlib import Path

from pydantic import field_validator

from codealmanac.core.models import CodeAlmanacModel
from codealmanac.core.paths import normalize_path
from codealmanac.core.text import required_text
from codealmanac.workflows.local_setup.models import LocalRepositoryState

GIT_REPOSITORY_TIMEOUT_SECONDS = 10
GITHUB_HTTPS_RE = re.compile(
    r"^https://github\.com/(?P<owner>[^/]+)/(?P<name>[^/]+?)(?:\.git)?/?$"
)
GITHUB_SSH_RE = re.compile(
    r"^(?:git@github\.com:|ssh://git@github\.com/)"
    r"(?P<owner>[^/]+)/(?P<name>[^/]+?)(?:\.git)?/?$"
)


class GitLocalRepositoryProbe:
    def read(self, cwd: Path) -> LocalRepositoryState:
        normalized = normalize_path(cwd)
        root = run_git(normalized, ("rev-parse", "--show-toplevel"))
        if root.returncode != 0:
            return unavailable(normalized, first_line(root.stderr, root.stdout))
        repository_root = normalize_path(Path(root.stdout.strip()))

        branch = run_git(repository_root, ("branch", "--show-current"))
        if branch.returncode != 0:
            return unavailable(normalized, first_line(branch.stderr, branch.stdout))
        branch_name = branch.stdout.strip()
        if branch_name == "":
            return unavailable(normalized, "detached HEAD has no branch")

        head = run_git(repository_root, ("rev-parse", "HEAD"))
        if head.returncode != 0:
            return unavailable(normalized, first_line(head.stderr, head.stdout))
        head_sha = head.stdout.strip()
        if head_sha == "":
            return unavailable(normalized, "git HEAD is empty")

        remote = run_git(repository_root, ("remote", "get-url", "origin"))
        if remote.returncode != 0:
            return unavailable(normalized, first_line(remote.stderr, remote.stdout))
        parsed = parse_github_remote(remote.stdout.strip())
        if parsed is None:
            return unavailable(normalized, "origin remote is not a GitHub repository")

        default_branch = default_branch_name(repository_root)
        return LocalRepositoryState(
            cwd=normalized,
            available=True,
            repository_root=repository_root,
            branch_name=branch_name,
            head_sha=head_sha,
            provider="github",
            owner_login=parsed.owner,
            name=parsed.name,
            full_name=f"{parsed.owner}/{parsed.name}",
            default_branch=default_branch,
        )


class GitHubRemote(CodeAlmanacModel):
    owner: str
    name: str

    @field_validator("owner", "name")
    @classmethod
    def require_text(cls, value: str) -> str:
        return required_text(value, "GitHub remote text")


def parse_github_remote(value: str) -> GitHubRemote | None:
    for pattern in (GITHUB_HTTPS_RE, GITHUB_SSH_RE):
        match = pattern.match(value)
        if match is not None:
            return GitHubRemote(
                owner=match.group("owner"),
                name=match.group("name"),
            )
    return None


def default_branch_name(repository_root: Path) -> str | None:
    symbolic = run_git(
        repository_root,
        ("symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD"),
    )
    if symbolic.returncode != 0:
        return None
    value = symbolic.stdout.strip()
    if value.startswith("origin/"):
        return value.removeprefix("origin/")
    return value or None


def run_git(cwd: Path, args: tuple[str, ...]) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ("git", *args),
            cwd=cwd,
            text=True,
            capture_output=True,
            timeout=GIT_REPOSITORY_TIMEOUT_SECONDS,
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


def unavailable(cwd: Path, reason: str) -> LocalRepositoryState:
    return LocalRepositoryState(
        cwd=cwd,
        available=False,
        unavailable_reason=reason or "git repository unavailable",
    )


def first_line(*values: str) -> str:
    for value in values:
        lines = [line.strip() for line in value.splitlines() if line.strip()]
        if lines:
            return lines[0]
    return ""
