from pathlib import Path

from codealmanac.app import CodeAlmanac
from codealmanac.services.viewer.requests import (
    ViewerOverviewRequest,
    ViewerPageRequest,
    ViewerSearchRequest,
    ViewerTopicRequest,
)


def test_viewer_overview_search_and_topic_use_index_read_model(
    viewer_repo: tuple[Path, CodeAlmanac],
):
    repo, app = viewer_repo

    overview = app.viewer.overview(ViewerOverviewRequest(cwd=repo))
    search = app.viewer.search(ViewerSearchRequest(cwd=repo, query="login"))
    topic = app.viewer.topic(ViewerTopicRequest(cwd=repo, slug="auth"))

    assert overview.workspace.name == "repo"
    assert overview.featured_page is not None
    assert overview.featured_page.slug == "getting-started"
    assert "auth-flow" in [page.slug for page in overview.pages]
    assert [page.slug for page in search.pages] == ["auth-flow"]
    assert [page.slug for page in topic.pages] == ["auth-flow", "session-store"]


def test_viewer_page_renders_markdown_and_reader_relationships(
    viewer_repo: tuple[Path, CodeAlmanac],
):
    repo, app = viewer_repo

    page = app.viewer.page(ViewerPageRequest(cwd=repo, slug="auth-flow"))

    assert page.title == "Auth Flow"
    assert page.outgoing_links == ("session-store",)
    assert page.related_pages[0].slug == "session-store"
    assert [ref.path for ref in page.file_refs] == ["src/auth/session.py"]
    assert '<a href="#/page/session-store">Session Store</a>' in page.html
    assert "<code>src/auth/session.py</code>" in page.html
    assert "<code>[[session-store]]</code>" in page.html
    assert "<script>" not in page.html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in page.html


def test_viewer_page_reports_backlinks(
    viewer_repo: tuple[Path, CodeAlmanac],
):
    repo, app = viewer_repo

    page = app.viewer.page(ViewerPageRequest(cwd=repo, slug="session-store"))

    assert page.backlinks == ("auth-flow",)
    assert page.related_pages[0].slug == "auth-flow"
