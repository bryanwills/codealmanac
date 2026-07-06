from datetime import UTC, datetime
from pathlib import Path

from codealmanac.services.repositories.models import Repository
from codealmanac.services.repositories.store import RepositoryStore


def test_repository_store_remembers_repository(tmp_path: Path):
    store = RepositoryStore(tmp_path / "codealmanac.db")
    root = tmp_path / "repo"
    repository = Repository(
        repository_id="repo-1",
        name="repo",
        description="Test repository",
        root_path=root,
        almanac_root=Path("almanac"),
        almanac_path=root / "almanac",
        registered_at=datetime(2026, 7, 6, tzinfo=UTC),
    )

    stored = store.remember(repository)

    assert stored.to_repository() == repository
    assert store.find_by_repository_id("repo-1") == stored
    assert store.list() == [stored]


def test_repository_store_replaces_repositories(tmp_path: Path):
    store = RepositoryStore(tmp_path / "codealmanac.db")
    first = Repository(
        repository_id="repo-1",
        name="repo-one",
        description="",
        root_path=tmp_path / "one",
        almanac_root=Path("almanac"),
        almanac_path=tmp_path / "one/almanac",
        registered_at=datetime(2026, 7, 6, tzinfo=UTC),
    )
    second = Repository(
        repository_id="repo-2",
        name="repo-two",
        description="",
        root_path=tmp_path / "two",
        almanac_root=Path("almanac"),
        almanac_path=tmp_path / "two/almanac",
        registered_at=datetime(2026, 7, 6, tzinfo=UTC),
    )

    store.remember(first)
    store.replace([store.remember(second)])

    assert store.find_by_repository_id("repo-1") is None
    assert [record.repository_id for record in store.list()] == ["repo-2"]
