import shutil
import subprocess
from pathlib import Path

import pytest
from conftest import runtime_index_path
from pydantic import ValidationError

from codealmanac.app import create_app
from codealmanac.core.errors import AlreadyExists, NotFoundError, ValidationFailed
from codealmanac.services.config.models import AppConfig
from codealmanac.services.harnesses.models import (
    HarnessKind,
    HarnessReadiness,
    HarnessRunResult,
    HarnessRunStatus,
)
from codealmanac.services.harnesses.requests import RunHarnessRequest
from codealmanac.services.health.requests import HealthCheckRequest
from codealmanac.services.repositories.models import RepositoryStatus
from codealmanac.services.repositories.requests import (
    DropRepositoryRequest,
    InitializeRepositoryRequest,
    RegisterRepositoryRequest,
    SelectRepositoryRequest,
)
from codealmanac.services.repositories.roots import is_initialized_almanac_root
from codealmanac.services.runs.models import RunKind, RunStatus
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


def test_initialize_creates_almanac_wiki_and_database(
    tmp_path: Path,
    isolated_home: Path,
):
    repo = tmp_path / "Example Repo"
    repo.mkdir()
    app = create_app(
        AppConfig(database_path=isolated_home / ".codealmanac/codealmanac.db")
    )

    repository = app.workflows.build.initialize(
        InitializeRepositoryRequest(path=repo, description="test wiki")
    )

    assert repository.name == "example-repo"
    assert (repo / "almanac/README.md").is_file()
    assert (repo / "almanac/topics.yaml").is_file()
    assert (repo / "almanac/getting-started.md").is_file()
    assert not (repo / "almanac/manual").exists()
    assert not (repo / ".gitignore").exists()
    assert app.repositories.list()[0].description == "test wiki"


def test_initialize_starter_wiki_has_no_health_noise(
    tmp_path: Path,
    isolated_home: Path,
):
    repo = tmp_path / "repo"
    repo.mkdir()
    app = create_app(
        AppConfig(database_path=isolated_home / ".codealmanac/codealmanac.db")
    )
    app.workflows.build.initialize(InitializeRepositoryRequest(path=repo))

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
        InitializeRepositoryRequest(
            path=repo,
            almanac_root=Path("docs/almanac"),
            name="repo",
        )


def test_build_without_root_targets_exact_path(
    tmp_path: Path,
    isolated_home: Path,
):
    repo = tmp_path / "repo"
    repo.mkdir()
    app = create_app(
        AppConfig(database_path=isolated_home / ".codealmanac/codealmanac.db")
    )
    app.workflows.build.initialize(
        InitializeRepositoryRequest(
            path=repo,
            name="docs-root",
            description="registered wiki",
        )
    )

    source_dir = repo / "src"
    result = app.workflows.build.build(
        InitializeRepositoryRequest(path=source_dir, name="source-dir")
    )

    assert result.repository.name == "source-dir"
    assert result.repository.description == ""
    assert result.repository.root_path == source_dir
    assert result.repository.almanac_root == Path("almanac")
    assert result.repository.almanac_path == source_dir / "almanac"


def test_initialize_rejects_dot_almanac_root(
    tmp_path: Path,
    isolated_home: Path,
):
    repo = tmp_path / "repo"
    repo.mkdir()

    with pytest.raises(ValidationError, match="fixed at almanac"):
        InitializeRepositoryRequest(
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
        AppConfig(database_path=isolated_home / ".codealmanac/codealmanac.db")
    )

    with pytest.raises(NotFoundError):
        app.repositories.resolve(repo / "src")


def test_resolve_prefers_nearest_initialized_root_over_broad_parent_database(
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
        AppConfig(database_path=isolated_home / ".codealmanac/codealmanac.db")
    )
    app.repositories.register(
        RegisterRepositoryRequest(
            root_path=projects,
            almanac_root=Path("almanac"),
            name="projects",
        )
    )

    repository = app.repositories.resolve(repo)

    assert repository.root_path == repo
    assert repository.almanac_root == Path("almanac")
    assert repository.almanac_path == repo / "almanac"


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
        AppConfig(database_path=isolated_home / ".codealmanac/codealmanac.db")
    )

    with pytest.raises(NotFoundError):
        app.repositories.resolve(repo)

    assert app.repositories.list() == []


@pytest.mark.parametrize("root", [Path("/tmp/almanac"), Path("../almanac")])
def test_initialize_rejects_roots_outside_repo(
    tmp_path: Path,
    isolated_home: Path,
    root: Path,
):
    repo = tmp_path / "repo"
    repo.mkdir()
    app = create_app(
        AppConfig(database_path=isolated_home / ".codealmanac/codealmanac.db")
    )

    with pytest.raises(ValueError):
        app.workflows.build.initialize(
            InitializeRepositoryRequest(
                path=repo,
                almanac_root=root,
                name="repo",
            )
        )


def test_initialize_rejects_existing_almanac(
    tmp_path: Path,
    isolated_home: Path,
):
    repo = tmp_path / "repo"
    repo.mkdir()
    app = create_app(
        AppConfig(database_path=isolated_home / ".codealmanac/codealmanac.db")
    )
    app.workflows.build.initialize(InitializeRepositoryRequest(path=repo, name="repo"))
    readme = repo / "almanac/README.md"
    readme.write_text("user edit\n", encoding="utf-8")

    with pytest.raises(AlreadyExists):
        app.workflows.build.initialize(
            InitializeRepositoryRequest(path=repo, name="renamed")
        )

    assert readme.read_text(encoding="utf-8") == "user edit\n"
    assert not (repo / "almanac/manual").exists()


def test_build_refreshes_wiki_and_rebuilds_index(
    tmp_path: Path,
    isolated_home: Path,
):
    repo = tmp_path / "repo"
    repo.mkdir()
    app = create_app(
        AppConfig(database_path=isolated_home / ".codealmanac/codealmanac.db")
    )

    result = app.workflows.build.build(
        InitializeRepositoryRequest(path=repo, name="repo")
    )

    assert result.repository.name == "repo"
    assert result.index.pages_indexed == 2
    assert result.index.files_seen == 2
    assert runtime_index_path(isolated_home, result.repository).is_file()
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
        AppConfig(database_path=isolated_home / ".codealmanac/codealmanac.db"),
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
    assert result.run.kind == RunKind.BUILD
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
        AppConfig(database_path=isolated_home / ".codealmanac/codealmanac.db"),
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

    assert app.repositories.list() == []
    assert not (repo / "almanac").exists()
    assert adapter.requests == []


def test_repository_selection_supports_name_id_and_path(
    tmp_path: Path,
    isolated_home: Path,
):
    repo = tmp_path / "repo"
    repo.mkdir()
    app = create_app(
        AppConfig(database_path=isolated_home / ".codealmanac/codealmanac.db")
    )
    repository = app.workflows.build.initialize(InitializeRepositoryRequest(path=repo))

    by_name = app.repositories.select(SelectRepositoryRequest(selector="repo"))

    assert by_name.repository_id == repository.repository_id


def test_repository_database_reports_and_drops_missing_wikis(
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
        AppConfig(database_path=isolated_home / ".codealmanac/codealmanac.db")
    )
    app.workflows.build.initialize(
        InitializeRepositoryRequest(path=live_repo, name="live")
    )
    app.workflows.build.initialize(
        InitializeRepositoryRequest(path=missing_repo, name="missing")
    )
    app.workflows.build.initialize(
        InitializeRepositoryRequest(path=missing_almanac, name="missing-almanac")
    )
    app.repositories.register(
        RegisterRepositoryRequest(root_path=index_only, name="index-only")
    )
    (index_only / "almanac").mkdir()
    (index_only / "almanac/index.db").write_bytes(b"derived")
    remove_tree(missing_repo)
    remove_tree(missing_almanac / "almanac")

    before = app.repositories.list_database()
    statuses = {item.repository.name: item.status for item in before.items}
    result = app.repositories.drop_missing()

    assert statuses == {
        "live": RepositoryStatus.AVAILABLE,
        "missing": RepositoryStatus.MISSING_REPO,
        "missing-almanac": RepositoryStatus.MISSING_ALMANAC,
        "index-only": RepositoryStatus.MISSING_ALMANAC,
    }
    assert sorted(repository.name for repository in result.dropped) == [
        "index-only",
        "missing",
        "missing-almanac",
    ]
    remaining = tuple(
        item.repository.name for item in app.repositories.list_database().items
    )
    assert remaining == ("live",)


def test_repository_database_drops_selected_wiki(
    tmp_path: Path,
    isolated_home: Path,
):
    repo = tmp_path / "repo"
    repo.mkdir()
    app = create_app(
        AppConfig(database_path=isolated_home / ".codealmanac/codealmanac.db")
    )
    app.workflows.build.initialize(InitializeRepositoryRequest(path=repo, name="repo"))

    result = app.repositories.drop(DropRepositoryRequest(selector="repo"))

    assert tuple(repository.name for repository in result.dropped) == ("repo",)
    assert app.repositories.list_database().items == ()


def remove_tree(path: Path) -> None:
    shutil.rmtree(path)


def initialize_git(repo: Path) -> None:
    subprocess.run(("git", "init"), cwd=repo, check=True, capture_output=True)
