from codealmanac.services.index.models import (
    IndexRefreshResult,
    PageView,
    SearchPageResult,
)
from codealmanac.services.index.requests import SearchIndexRequest
from codealmanac.services.index.store import IndexStore
from codealmanac.services.workspaces.service import WorkspacesService


class IndexService:
    def __init__(self, workspaces: WorkspacesService, store: IndexStore):
        self.workspaces = workspaces
        self.store = store

    def ensure_fresh(self, workspace_id: str) -> IndexRefreshResult:
        workspace = self.workspaces.get(workspace_id)
        return self.store.rebuild(workspace.almanac_path)

    def search(
        self,
        workspace_id: str,
        request: SearchIndexRequest,
    ) -> tuple[SearchPageResult, ...]:
        self.ensure_fresh(workspace_id)
        workspace = self.workspaces.get(workspace_id)
        return self.store.search(workspace.almanac_path, request)

    def get_page(self, workspace_id: str, slug: str) -> PageView | None:
        self.ensure_fresh(workspace_id)
        workspace = self.workspaces.get(workspace_id)
        return self.store.get_page(workspace.almanac_path, slug)
