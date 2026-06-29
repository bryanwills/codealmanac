from pathlib import Path

from codealmanac.core.models import CodeAlmanacModel


class SearchPageResult(CodeAlmanacModel):
    slug: str
    title: str | None
    summary: str | None
    updated_at: int
    archived_at: int | None
    superseded_by: str | None
    topics: tuple[str, ...]


class PageFileReference(CodeAlmanacModel):
    path: str
    is_dir: bool


class CrossWikiReference(CodeAlmanacModel):
    wiki: str
    target: str


class PageView(CodeAlmanacModel):
    slug: str
    title: str | None
    summary: str | None
    file_path: Path
    updated_at: int
    archived_at: int | None
    superseded_by: str | None
    topics: tuple[str, ...]
    file_refs: tuple[PageFileReference, ...]
    wikilinks_out: tuple[str, ...]
    wikilinks_in: tuple[str, ...]
    cross_wiki_links: tuple[CrossWikiReference, ...]
    body: str


class IndexRefreshResult(CodeAlmanacModel):
    changed: int
    removed: int
    pages_indexed: int
    files_seen: int
    files_skipped: int
