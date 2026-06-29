from enum import StrEnum
from pathlib import Path

from codealmanac.core.models import CodeAlmanacModel


class WikilinkKind(StrEnum):
    PAGE = "page"
    FILE = "file"
    FOLDER = "folder"
    CROSS_WIKI = "xwiki"


class FileReference(CodeAlmanacModel):
    path: str
    original_path: str
    is_dir: bool


class PageLink(CodeAlmanacModel):
    kind: WikilinkKind
    target: str


class FileLink(CodeAlmanacModel):
    kind: WikilinkKind
    ref: FileReference


class FolderLink(CodeAlmanacModel):
    kind: WikilinkKind
    ref: FileReference


class CrossWikiLink(CodeAlmanacModel):
    kind: WikilinkKind
    wiki: str
    target: str


Wikilink = PageLink | FileLink | FolderLink | CrossWikiLink


class ParsedFrontmatter(CodeAlmanacModel):
    page_id: str | None = None
    title: str | None = None
    summary: str | None = None
    topics: tuple[str, ...] = ()
    files: tuple[str, ...] = ()
    archived_at: int | None = None
    superseded_by: str | None = None
    body: str


class PageDocument(CodeAlmanacModel):
    slug: str
    title: str
    summary: str | None
    file_path: Path
    relative_path: str
    content_hash: str
    updated_at: int
    archived_at: int | None
    superseded_by: str | None
    topics: tuple[str, ...]
    file_refs: tuple[FileReference, ...]
    page_links: tuple[str, ...]
    cross_wiki_links: tuple[tuple[str, str], ...]
    body: str
