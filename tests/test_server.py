from pathlib import Path

from fastapi.testclient import TestClient

from codealmanac.app import CodeAlmanac
from codealmanac.server.app import create_server_app


def test_server_serves_static_assets_and_viewer_api(
    viewer_repo: tuple[Path, CodeAlmanac],
):
    repo, app = viewer_repo
    client = TestClient(create_server_app(app, repo))

    index = client.get("/")
    overview = client.get("/api/overview")
    page = client.get("/api/page/auth-flow")
    search = client.get("/api/search", params={"q": "login"})
    file = client.get("/api/file", params={"path": "src/auth/session.py"})
    topic = client.get("/api/topic/auth")
    javascript = client.get("/app.js")
    module = client.get("/assets/viewer/main.js")
    renderers_module = client.get("/assets/viewer/renderers.js")
    api_module = client.get("/assets/viewer/api.js")

    assert index.status_code == 200
    assert "CodeAlmanac" in index.text
    assert "repo-owned wiki" in index.text
    assert "Local knowledge graph" in index.text
    assert 'type="module"' in index.text
    assert javascript.status_code == 200
    assert 'import { startViewer } from "/assets/viewer/main.js";' in javascript.text
    assert javascript.headers["content-type"].startswith("text/javascript")
    assert module.status_code == 200
    assert module.headers["content-type"].startswith("text/javascript")
    assert 'from "./renderers.js"' in module.text
    assert "dataset.railKind" in module.text
    assert renderers_module.status_code == 200
    assert "Sources" in renderers_module.text
    assert api_module.status_code == 200
    assert "/api/file?path=" in api_module.text
    assert overview.json()["workspace"]["name"] == "repo"
    assert page.json()["slug"] == "auth-flow"
    assert page.json()["sources"][0]["source_id"] == "session-file"
    assert page.json()["sources"][0]["target"] == "src/auth/session.py"
    assert '<a href="#/page/session-store">Session Store</a>' in page.json()["html"]
    assert [row["slug"] for row in search.json()["pages"]] == ["auth-flow"]
    assert file.json()["kind"] == "file"
    assert [row["slug"] for row in file.json()["pages"]] == ["auth-flow"]
    assert [row["slug"] for row in topic.json()["pages"]] == [
        "auth-flow",
        "session-store",
    ]


def test_server_maps_product_errors_to_http_statuses(
    viewer_repo: tuple[Path, CodeAlmanac],
):
    repo, app = viewer_repo
    client = TestClient(create_server_app(app, repo))

    response = client.get("/api/page/missing")

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "not_found"


def test_server_maps_request_validation_errors_to_http_statuses(
    viewer_repo: tuple[Path, CodeAlmanac],
):
    repo, app = viewer_repo
    client = TestClient(create_server_app(app, repo))

    response = client.get("/api/search", params={"limit": "-1"})

    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "validation_failed"


def test_server_rejects_invalid_file_reference_paths(
    viewer_repo: tuple[Path, CodeAlmanac],
):
    repo, app = viewer_repo
    client = TestClient(create_server_app(app, repo))

    response = client.get("/api/file", params={"path": "../secret.txt"})

    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "validation_failed"


def test_server_rejects_invalid_static_asset_paths(
    viewer_repo: tuple[Path, CodeAlmanac],
):
    repo, app = viewer_repo
    client = TestClient(create_server_app(app, repo))

    traversal = client.get("/assets/%2E%2E/app.js")
    missing = client.get("/assets/viewer/missing.js")
    unsupported = client.get("/assets/viewer/main.txt")

    assert traversal.status_code == 422
    assert traversal.json()["detail"]["code"] == "validation_failed"
    assert missing.status_code == 404
    assert missing.json()["detail"]["code"] == "not_found"
    assert unsupported.status_code == 422
    assert unsupported.json()["detail"]["code"] == "validation_failed"
