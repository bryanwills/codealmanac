from enum import StrEnum
from pathlib import Path

from codealmanac.core.models import CodeAlmanacModel


class ViewerFileKind(StrEnum):
    FILE = "file"
    DIRECTORY = "directory"


class ViewerWorkspace(CodeAlmanacModel):
    workspace_id: str
    name: str
    root_path: Path


class ViewerPageSummary(CodeAlmanacModel):
    slug: str
    title: str | None
    summary: str | None
    topics: tuple[str, ...]
    archived: bool


class ViewerTopicSummary(CodeAlmanacModel):
    slug: str
    title: str | None
    description: str | None
    page_count: int


class ViewerFileReference(CodeAlmanacModel):
    path: str
    is_dir: bool


class ViewerPageSource(CodeAlmanacModel):
    source_id: str
    source_type: str
    target: str | None
    title: str | None
    retrieved_at: str | None
    note: str | None


class ViewerOverview(CodeAlmanacModel):
    workspace: ViewerWorkspace
    workspaces: tuple[ViewerWorkspace, ...]
    page_count: int
    topic_count: int
    pages: tuple[ViewerPageSummary, ...]
    topics: tuple[ViewerTopicSummary, ...]
    featured_page: ViewerPageSummary | None


class ViewerPage(CodeAlmanacModel):
    workspace: ViewerWorkspace
    slug: str
    title: str | None
    summary: str | None
    topics: tuple[str, ...]
    body: str
    html: str
    backlinks: tuple[str, ...]
    outgoing_links: tuple[str, ...]
    file_refs: tuple[ViewerFileReference, ...]
    sources: tuple[ViewerPageSource, ...]
    related_pages: tuple[ViewerPageSummary, ...]


class ViewerSearch(CodeAlmanacModel):
    workspace: ViewerWorkspace
    query: str | None
    pages: tuple[ViewerPageSummary, ...]


class ViewerFile(CodeAlmanacModel):
    workspace: ViewerWorkspace
    path: str
    kind: ViewerFileKind
    pages: tuple[ViewerPageSummary, ...]


class ViewerTopic(CodeAlmanacModel):
    workspace: ViewerWorkspace
    slug: str
    title: str | None
    description: str | None
    parents: tuple[str, ...]
    children: tuple[str, ...]
    pages: tuple[ViewerPageSummary, ...]
