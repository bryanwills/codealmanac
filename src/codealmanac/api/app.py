from pathlib import Path

from fastapi import FastAPI

from codealmanac.api.errors import register_error_handlers
from codealmanac.api.routes import ApiContext, register_routes
from codealmanac.api.static_routes import register_static_routes
from codealmanac.app import CodeAlmanac


def create_api_app(
    codealmanac: CodeAlmanac,
    cwd: Path,
    wiki: str | None = None,
) -> FastAPI:
    api = FastAPI(title="CodeAlmanac Local Viewer")
    register_error_handlers(api)
    register_routes(
        api,
        ApiContext(codealmanac=codealmanac, cwd=cwd, scope_wiki=wiki),
    )
    register_static_routes(api)

    return api
