from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, Response

from codealmanac.api.static_assets import (
    StaticAssetRequest,
    asset_response,
    read_asset_text,
)


def register_static_routes(api: FastAPI) -> None:
    @api.get("/", include_in_schema=False)
    def index() -> HTMLResponse:
        return HTMLResponse(read_asset_text(StaticAssetRequest(path="index.html")))

    @api.get("/app.js", include_in_schema=False)
    def app_js() -> Response:
        return asset_response("app.js")

    @api.get("/app.css", include_in_schema=False)
    def app_css() -> Response:
        return asset_response("app.css")

    @api.get("/assets/{asset_path:path}", include_in_schema=False)
    def static_asset(asset_path: str) -> Response:
        return asset_response(asset_path)

    @api.get("/{path:path}", include_in_schema=False)
    def fallback(path: str) -> HTMLResponse:
        if path.startswith("api/"):
            raise HTTPException(status_code=404, detail="not found")
        return HTMLResponse(read_asset_text(StaticAssetRequest(path="index.html")))
