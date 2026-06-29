import sqlite3
from pathlib import Path

from codealmanac.app import create_app
from codealmanac.core.models import AppConfig
from codealmanac.services.pages.requests import ShowPageRequest
from codealmanac.services.search.requests import SearchPagesRequest
from codealmanac.services.workspaces.requests import InitializeWorkspaceRequest


def test_search_indexes_pages_topics_mentions_and_links(
    tmp_path: Path,
    isolated_home: Path,
):
    repo = tmp_path / "repo"
    repo.mkdir()
    app = create_app(AppConfig(registry_path=isolated_home / ".almanac/registry.json"))
    app.build.initialize(InitializeWorkspaceRequest(path=repo))
    write_page(
        repo,
        "auth-flow.md",
        """---
title: Auth Flow
summary: How sign-in moves through the app.
topics: [auth]
files:
  - src/auth/
---
# Auth Flow

Login checks [[src/auth/session.py]] and links to [[session-store]].
""",
    )
    write_page(
        repo,
        "session-store.md",
        """---
title: Session Store
topics: [auth]
---
# Session Store

Session persistence details.
""",
    )

    rows = app.search.search(
        SearchPagesRequest(cwd=repo, query="login", topics=("auth",))
    )
    mentioned = app.search.search(
        SearchPagesRequest(cwd=repo, mentions="src/auth/session.py")
    )
    page = app.pages.show(ShowPageRequest(cwd=repo, slug="session-store"))

    assert [row.slug for row in rows] == ["auth-flow"]
    assert [row.slug for row in mentioned] == ["auth-flow"]
    assert page.wikilinks_in == ("auth-flow",)


def test_search_auto_registers_existing_wiki(
    tmp_path: Path,
    isolated_home: Path,
):
    repo = tmp_path / "repo"
    (repo / ".almanac/pages").mkdir(parents=True)
    write_page(repo, "note.md", "# Note\n\nUniqueNeedle context.\n")
    app = create_app(AppConfig(registry_path=isolated_home / ".almanac/registry.json"))

    rows = app.search.search(SearchPagesRequest(cwd=repo, query="uniqueneedle"))

    assert [row.slug for row in rows] == ["note"]
    assert app.workspaces.list()[0].root_path == repo


def test_search_rebuilds_stale_existing_index_schema(
    tmp_path: Path,
    isolated_home: Path,
):
    repo = tmp_path / "repo"
    repo.mkdir()
    app = create_app(AppConfig(registry_path=isolated_home / ".almanac/registry.json"))
    app.build.initialize(InitializeWorkspaceRequest(path=repo))
    write_page(repo, "note.md", "# Note\n\nStaleSchemaNeedle context.\n")
    db_path = repo / ".almanac/index.db"
    with sqlite3.connect(db_path) as connection:
        connection.execute("CREATE TABLE pages (slug TEXT PRIMARY KEY)")
        connection.execute("PRAGMA user_version = 1")

    rows = app.search.search(SearchPagesRequest(cwd=repo, query="staleschemaneedle"))

    assert [row.slug for row in rows] == ["note"]


def write_page(repo: Path, name: str, body: str) -> None:
    path = repo / ".almanac/pages" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
