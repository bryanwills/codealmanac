from dataclasses import dataclass
from pathlib import Path

from fastapi import FastAPI

from codealmanac.app import CodeAlmanac
from codealmanac.wiki.viewer.models import (
    ViewerFile,
    ViewerOverview,
    ViewerPage,
    ViewerRun,
    ViewerRuns,
    ViewerSearch,
    ViewerTopic,
)
from codealmanac.wiki.viewer.requests import (
    ViewerFileRequest,
    ViewerOverviewRequest,
    ViewerPageRequest,
    ViewerRunRequest,
    ViewerRunsRequest,
    ViewerSearchRequest,
    ViewerTopicRequest,
)


@dataclass(frozen=True)
class ApiContext:
    codealmanac: CodeAlmanac
    cwd: Path
    scope_wiki: str | None = None

    def selected_wiki(self, request_wiki: str | None) -> str | None:
        return self.scope_wiki or request_wiki


def register_routes(api: FastAPI, context: ApiContext) -> None:
    @api.get("/api/overview", response_model=ViewerOverview)
    def overview(wiki: str | None = None) -> ViewerOverview:
        return context.codealmanac.viewer.overview(
            ViewerOverviewRequest(
                cwd=context.cwd,
                wiki=context.selected_wiki(wiki),
                include_workspaces=context.scope_wiki is None,
            )
        )

    @api.get("/api/page/{slug}", response_model=ViewerPage)
    def page(slug: str, wiki: str | None = None) -> ViewerPage:
        return context.codealmanac.viewer.page(
            ViewerPageRequest(
                cwd=context.cwd,
                wiki=context.selected_wiki(wiki),
                slug=slug,
            )
        )

    @api.get("/api/search", response_model=ViewerSearch)
    def search(
        q: str | None = None,
        limit: int = 50,
        wiki: str | None = None,
    ) -> ViewerSearch:
        return context.codealmanac.viewer.search(
            ViewerSearchRequest(
                cwd=context.cwd,
                wiki=context.selected_wiki(wiki),
                query=q,
                limit=limit,
            )
        )

    @api.get("/api/file", response_model=ViewerFile)
    def file_route(
        path: str,
        limit: int = 50,
        wiki: str | None = None,
    ) -> ViewerFile:
        return context.codealmanac.viewer.file(
            ViewerFileRequest(
                cwd=context.cwd,
                wiki=context.selected_wiki(wiki),
                path=path,
                limit=limit,
            )
        )

    @api.get("/api/topic/{slug}", response_model=ViewerTopic)
    def topic(
        slug: str,
        descendants: bool = False,
        wiki: str | None = None,
    ) -> ViewerTopic:
        return context.codealmanac.viewer.topic(
            ViewerTopicRequest(
                cwd=context.cwd,
                wiki=context.selected_wiki(wiki),
                slug=slug,
                include_descendants=descendants,
            )
        )

    @api.get("/api/runs", response_model=ViewerRuns)
    def runs(limit: int | None = None, wiki: str | None = None) -> ViewerRuns:
        return context.codealmanac.viewer.runs(
            ViewerRunsRequest(
                cwd=context.cwd,
                wiki=context.selected_wiki(wiki),
                limit=limit,
            )
        )

    @api.get("/api/runs/{run_id}", response_model=ViewerRun)
    def run(run_id: str, wiki: str | None = None) -> ViewerRun:
        return context.codealmanac.viewer.run(
            ViewerRunRequest(
                cwd=context.cwd,
                wiki=context.selected_wiki(wiki),
                run_id=run_id,
            )
        )
