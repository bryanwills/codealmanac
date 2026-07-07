from datetime import UTC, datetime
from pathlib import Path

import pytest

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


def test_repository_name_is_a_shared_pydantic_boundary(tmp_path: Path):
    repository = Repository(
        repository_id="repo-1",
        name="  repo  ",
        description="",
        root_path=tmp_path / "repo",
        almanac_root=Path("almanac"),
        almanac_path=tmp_path / "repo/almanac",
        registered_at=datetime(2026, 7, 6, tzinfo=UTC),
    )

    assert repository.name == "repo"
    with pytest.raises(ValueError):
        Repository(
            repository_id="repo-1",
            name="  ",
            description="",
            root_path=tmp_path / "repo",
            almanac_root=Path("almanac"),
            almanac_path=tmp_path / "repo/almanac",
            registered_at=datetime(2026, 7, 6, tzinfo=UTC),
        )


def test_repository_store_updates_existing_repository(tmp_path: Path):
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
    changed = Repository(
        repository_id="repo-1",
        name="repo-renamed",
        description="Updated",
        root_path=tmp_path / "one",
        almanac_root=Path("almanac"),
        almanac_path=tmp_path / "one/almanac",
        registered_at=datetime(2026, 7, 7, tzinfo=UTC),
    )

    store.remember(first)
    store.remember(changed)

    record = store.find_by_repository_id("repo-1")
    assert record is not None
    assert record.name == "repo-renamed"
    assert record.description == "Updated"
    assert record.registered_at == first.registered_at
    assert [item.repository_id for item in store.list()] == ["repo-1"]
