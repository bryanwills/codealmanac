import shutil
import subprocess
from pathlib import Path

import pytest
from conftest import runtime_index_path
from pydantic import ValidationError

from codealmanac.app import create_app
from codealmanac.core.errors import NotFoundError, ValidationFailed
from codealmanac.core.models import AppConfig
from codealmanac.services.harnesses.models import (
    HarnessKind,
    HarnessReadiness,
    HarnessRunResult,
    HarnessRunStatus,
)
from codealmanac.services.harnesses.requests import RunHarnessRequest
from codealmanac.services.health.requests import HealthCheckRequest
from codealmanac.services.runs.models import RunOperation, RunStatus
from codealmanac.services.workspaces.models import WorkspaceRegistryStatus
from codealmanac.services.workspaces.requests import (
    DropWorkspaceRequest,
    InitializeWorkspaceRequest,
    RegisterWorkspaceRequest,
    SelectWorkspaceRequest,
)
from codealmanac.services.workspaces.roots import is_initialized_almanac_root
from codealmanac.workflows.build.requests import RunBuildRequest


class BuildWritingHarnessAdapter:
    kind = HarnessKind.CODEX

    def __init__(self):
        self.requests: list[RunHarnessRequest] = []

    def check(self) -> HarnessReadiness:
        return HarnessReadiness(
            kind=self.kind,
            available=True,
            message="codex ready",
        )

    def run(self, request: RunHarnessRequest) -> HarnessRunResult:
        self.requests.append(request)
        page = request.cwd / "almanac/architecture/build-flow.md"
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text(
            """---
title: Build Flow
topics: [getting-started]
sources: []
---
# Build Flow

Build creates the first useful wiki for this repository.
""",
            encoding="utf-8",
        )
        return HarnessRunResult(
            kind=self.kind,
            status=HarnessRunStatus.SUCCEEDED,
            output_text="built wiki",
            summary="built wiki",
            changed_files=(page,),
        )


def test_initialize_creates_almanac_wiki_and_registry(
    tmp_path: Path,
    isolated_home: Path,
):
    repo = tmp_path / "Example Repo"
    repo.mkdir()
    app = create_app(
        AppConfig(registry_path=isolated_home / ".codealmanac/registry.json")
    )

    workspace = app.workflows.build.initialize(
        InitializeWorkspaceRequest(path=repo, description="test wiki")
    )

    assert workspace.name == "example-repo"
    assert (repo / "almanac/README.md").is_file()
    assert (repo / "almanac/topics.yaml").is_file()
    assert (repo / "almanac/getting-started.md").is_file()
    assert not (repo / "almanac/manual").exists()
    assert not (repo / ".gitignore").exists()
    assert app.workspaces.list()[0].description == "test wiki"


def test_initialize_starter_wiki_has_no_health_noise(
    tmp_path: Path,
    isolated_home: Path,
):
    repo = tmp_path / "repo"
    repo.mkdir()
    app = create_app(
        AppConfig(registry_path=isolated_home / ".codealmanac/registry.json")
    )
    app.workflows.build.initialize(InitializeWorkspaceRequest(path=repo))

    report = app.health.check(HealthCheckRequest(cwd=repo))

    assert report.empty_topics == ()
    assert report.broken_links == ()
    assert report.dead_refs == ()


def test_initialize_rejects_configured_almanac_root(
    tmp_path: Path,
    isolated_home: Path,
):
    repo = tmp_path / "repo"
    repo.mkdir()

    with pytest.raises(ValidationError, match="fixed at almanac"):
        InitializeWorkspaceRequest(
            path=repo,
            almanac_root=Path("docs/almanac"),
            name="repo",
        )


def test_build_without_root_uses_registered_almanac_tree(
    tmp_path: Path,
    isolated_home: Path,
):
    repo = tmp_path / "repo"
    repo.mkdir()
    app = create_app(
        AppConfig(registry_path=isolated_home / ".codealmanac/registry.json")
    )
    app.workflows.build.initialize(
        InitializeWorkspaceRequest(
            path=repo,
            name="docs-root",
            description="registered wiki",
        )
    )

    result = app.workflows.build.build(InitializeWorkspaceRequest(path=repo / "src"))

    assert result.workspace.name == "docs-root"
    assert result.workspace.description == "registered wiki"
    assert result.workspace.almanac_root == Path("almanac")
    assert result.workspace.almanac_path == repo / "almanac"


def test_initialize_rejects_dot_almanac_root(
    tmp_path: Path,
    isolated_home: Path,
):
    repo = tmp_path / "repo"
    repo.mkdir()

    with pytest.raises(ValidationError, match="fixed at almanac"):
        InitializeWorkspaceRequest(
            path=repo,
            almanac_root=Path(".almanac"),
            name="repo",
        )


def test_resolve_ignores_unregistered_dot_almanac_root(
    tmp_path: Path,
    isolated_home: Path,
):
    repo = tmp_path / "repo"
    (repo / ".almanac").mkdir(parents=True)
    (repo / ".almanac/topics.yaml").write_text("topics: []\n", encoding="utf-8")
    app = create_app(
        AppConfig(registry_path=isolated_home / ".codealmanac/registry.json")
    )

    with pytest.raises(NotFoundError):
        app.workspaces.resolve(repo / "src")


def test_resolve_prefers_nearest_initialized_root_over_broad_parent_registry(
    tmp_path: Path,
    isolated_home: Path,
):
    projects = tmp_path / "Projects"
    repo = projects / "codealmanac"
    (repo / "almanac").mkdir(parents=True)
    (repo / "almanac/README.md").write_text(
        "---\ntopics: [concepts]\n---\n# Wiki\n\nRoot page.\n",
        encoding="utf-8",
    )
    (repo / "almanac/topics.yaml").write_text("topics: []\n", encoding="utf-8")
    app = create_app(
        AppConfig(registry_path=isolated_home / ".codealmanac/registry.json")
    )
    app.workspaces.register(
        RegisterWorkspaceRequest(
            root_path=projects,
            almanac_root=Path("almanac"),
            name="projects",
        )
    )

    workspace = app.workspaces.resolve(repo)

    assert workspace.root_path == repo
    assert workspace.almanac_root == Path("almanac")
    assert workspace.almanac_path == repo / "almanac"


def test_initialized_wiki_requires_topics_yaml_and_readme(tmp_path: Path):
    readme_only = tmp_path / "readme-only"
    topics_only = tmp_path / "topics-only"
    pages_only = tmp_path / "old-pages-only"
    initialized = tmp_path / "initialized"
    readme_only.mkdir()
    topics_only.mkdir()
    (pages_only / "pages").mkdir(parents=True)
    initialized.mkdir()
    (readme_only / "README.md").write_text("# Not enough\n", encoding="utf-8")
    (topics_only / "topics.yaml").write_text("topics: []\n", encoding="utf-8")
    (initialized / "README.md").write_text(
        "---\ntopics: [concepts]\n---\n# Wiki\n\nRoot page.\n",
        encoding="utf-8",
    )
    (initialized / "topics.yaml").write_text("topics: []\n", encoding="utf-8")

    assert is_initialized_almanac_root(readme_only) is False
    assert is_initialized_almanac_root(topics_only) is False
    assert is_initialized_almanac_root(pages_only) is False
    assert is_initialized_almanac_root(initialized) is True


def test_readme_only_almanac_folder_does_not_auto_register_parent(
    tmp_path: Path,
    isolated_home: Path,
):
    projects = tmp_path / "Projects"
    repo = projects / "codealmanac"
    sibling = projects / "almanac"
    repo.mkdir(parents=True)
    sibling.mkdir()
    (sibling / "README.md").write_text("# Separate project\n", encoding="utf-8")
    app = create_app(
        AppConfig(registry_path=isolated_home / ".codealmanac/registry.json")
    )

    with pytest.raises(NotFoundError):
        app.workspaces.resolve(repo)

    assert app.workspaces.list() == []


@pytest.mark.parametrize("root", [Path("/tmp/almanac"), Path("../almanac")])
def test_initialize_rejects_roots_outside_repo(
    tmp_path: Path,
    isolated_home: Path,
    root: Path,
):
    repo = tmp_path / "repo"
    repo.mkdir()
    app = create_app(
        AppConfig(registry_path=isolated_home / ".codealmanac/registry.json")
    )

    with pytest.raises(ValueError):
        app.workflows.build.initialize(
            InitializeWorkspaceRequest(
                path=repo,
                almanac_root=root,
                name="repo",
            )
        )


def test_initialize_is_idempotent_and_preserves_existing_pages(
    tmp_path: Path,
    isolated_home: Path,
):
    repo = tmp_path / "repo"
    repo.mkdir()
    app = create_app(
        AppConfig(registry_path=isolated_home / ".codealmanac/registry.json")
    )
    app.workflows.build.initialize(InitializeWorkspaceRequest(path=repo, name="repo"))
    readme = repo / "almanac/README.md"
    readme.write_text("user edit\n", encoding="utf-8")

    workspace = app.workflows.build.initialize(
        InitializeWorkspaceRequest(path=repo / "src", name="renamed")
    )

    assert workspace.root_path == repo
    assert workspace.name == "renamed"
    assert readme.read_text(encoding="utf-8") == "user edit\n"
    assert not (repo / "almanac/manual").exists()


def test_build_refreshes_wiki_and_rebuilds_index(
    tmp_path: Path,
    isolated_home: Path,
):
    repo = tmp_path / "repo"
    repo.mkdir()
    app = create_app(
        AppConfig(registry_path=isolated_home / ".codealmanac/registry.json")
    )

    result = app.workflows.build.build(
        InitializeWorkspaceRequest(path=repo, name="repo")
    )

    assert result.workspace.name == "repo"
    assert result.index.pages_indexed == 2
    assert result.index.files_seen == 2
    assert runtime_index_path(isolated_home, result.workspace).is_file()
    assert not (repo / "almanac/index.db").exists()


def test_run_build_uses_harness_prompt_and_records_build_operation(
    tmp_path: Path,
    isolated_home: Path,
):
    repo = tmp_path / "repo"
    repo.mkdir()
    initialize_git(repo)
    adapter = BuildWritingHarnessAdapter()
    app = create_app(
        AppConfig(registry_path=isolated_home / ".codealmanac/registry.json"),
        harness_adapters=(adapter,),
    )

    result = app.workflows.build.run(
        RunBuildRequest(
            path=repo,
            harness=HarnessKind.CODEX,
            name="repo",
            guidance="Write the smallest useful first wiki.",
        )
    )

    assert result.run is not None
    assert result.run.operation == RunOperation.BUILD
    assert result.run.status == RunStatus.DONE
    assert result.run.summary == "built wiki"
    assert result.index.pages_indexed == 3
    assert result.safety is not None
    assert repo / "almanac/README.md" in result.safety.changed_files
    assert repo / "almanac/architecture/build-flow.md" in result.safety.changed_files
    assert "Build Operation" in adapter.requests[0].prompt
    assert '"manual_documents": [' in adapter.requests[0].prompt
    assert "Phase 1: Scan And Plan" in adapter.requests[0].prompt
    assert "Use read-only research sub-agents" in adapter.requests[0].prompt
    assert "Use writing sub-agents" in adapter.requests[0].prompt
    assert "Write the smallest useful first wiki." in adapter.requests[0].prompt
    assert "pages/" not in adapter.requests[0].prompt
    assert "[[" not in adapter.requests[0].prompt


def test_run_build_rejects_non_git_repo_without_registering(
    tmp_path: Path,
    isolated_home: Path,
):
    repo = tmp_path / "repo"
    repo.mkdir()
    adapter = BuildWritingHarnessAdapter()
    app = create_app(
        AppConfig(registry_path=isolated_home / ".codealmanac/registry.json"),
        harness_adapters=(adapter,),
    )

    with pytest.raises(ValidationFailed, match="build requires Git change tracking"):
        app.workflows.build.run(
            RunBuildRequest(
                path=repo,
                harness=HarnessKind.CODEX,
                name="repo",
            )
        )

    assert app.workspaces.list() == []
    assert not (repo / "almanac").exists()
    assert adapter.requests == []


def test_workspace_selection_supports_name_id_and_path(
    tmp_path: Path,
    isolated_home: Path,
):
    repo = tmp_path / "repo"
    repo.mkdir()
    app = create_app(
        AppConfig(registry_path=isolated_home / ".codealmanac/registry.json")
    )
    workspace = app.workflows.build.initialize(InitializeWorkspaceRequest(path=repo))

    by_name = app.workspaces.select(SelectWorkspaceRequest(selector="repo"))

    assert by_name.workspace_id == workspace.workspace_id


def test_workspace_registry_reports_and_drops_missing_wikis(
    tmp_path: Path,
    isolated_home: Path,
):
    live_repo = tmp_path / "live"
    live_repo.mkdir()
    missing_repo = tmp_path / "missing"
    missing_repo.mkdir()
    missing_almanac = tmp_path / "missing-almanac"
    missing_almanac.mkdir()
    index_only = tmp_path / "index-only"
    index_only.mkdir()
    app = create_app(
        AppConfig(registry_path=isolated_home / ".codealmanac/registry.json")
    )
    app.workflows.build.initialize(
        InitializeWorkspaceRequest(path=live_repo, name="live")
    )
    app.workflows.build.initialize(
        InitializeWorkspaceRequest(path=missing_repo, name="missing")
    )
    app.workflows.build.initialize(
        InitializeWorkspaceRequest(path=missing_almanac, name="missing-almanac")
    )
    app.workspaces.register(
        RegisterWorkspaceRequest(root_path=index_only, name="index-only")
    )
    (index_only / "almanac").mkdir()
    (index_only / "almanac/index.db").write_bytes(b"derived")
    remove_tree(missing_repo)
    remove_tree(missing_almanac / "almanac")

    before = app.workspaces.list_registry()
    statuses = {item.workspace.name: item.status for item in before.items}
    result = app.workspaces.drop_missing()

    assert statuses == {
        "live": WorkspaceRegistryStatus.AVAILABLE,
        "missing": WorkspaceRegistryStatus.MISSING_REPO,
        "missing-almanac": WorkspaceRegistryStatus.MISSING_ALMANAC,
        "index-only": WorkspaceRegistryStatus.MISSING_ALMANAC,
    }
    assert tuple(workspace.name for workspace in result.dropped) == (
        "missing",
        "missing-almanac",
        "index-only",
    )
    remaining = tuple(
        item.workspace.name for item in app.workspaces.list_registry().items
    )
    assert remaining == ("live",)


def test_workspace_registry_drops_selected_wiki(
    tmp_path: Path,
    isolated_home: Path,
):
    repo = tmp_path / "repo"
    repo.mkdir()
    app = create_app(
        AppConfig(registry_path=isolated_home / ".codealmanac/registry.json")
    )
    app.workflows.build.initialize(InitializeWorkspaceRequest(path=repo, name="repo"))

    result = app.workspaces.drop(DropWorkspaceRequest(selector="repo"))

    assert tuple(workspace.name for workspace in result.dropped) == ("repo",)
    assert app.workspaces.list_registry().items == ()


def remove_tree(path: Path) -> None:
    shutil.rmtree(path)


def initialize_git(repo: Path) -> None:
    subprocess.run(("git", "init"), cwd=repo, check=True, capture_output=True)
