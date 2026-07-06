import argparse
from datetime import UTC, datetime

from codealmanac.cli.render.common import print_json_model, print_lines
from codealmanac.cli.render.style import EM_DASH, style
from codealmanac.core.errors import ValidationFailed
from codealmanac.services.index.models import PageView


def render_page(page: PageView, args: argparse.Namespace) -> None:
    if args.json:
        print_json_model(page)
        return
    selected = [
        flag
        for flag, enabled in (
            ("body", args.body),
            ("meta", args.meta),
            ("lead", args.lead),
            ("links", args.links),
            ("backlinks", args.backlinks),
            ("files", args.files),
            ("topics", args.topics),
        )
        if enabled
    ]
    if len(selected) > 1:
        flags = ", ".join(f"--{flag}" for flag in selected)
        raise ValidationFailed(f"show flags conflict: {flags} (pick one)")
    if len(selected) == 0:
        render_full(page)
        return
    view = selected[0]
    if view == "body":
        print(body_with_trailing_newline(page.body), end="")
    elif view == "meta":
        print(metadata_header(page))
    elif view == "lead":
        print(first_paragraph(page.body))
    elif view == "links":
        print_lines(page.page_links_out)
    elif view == "backlinks":
        print_lines(page.page_links_in)
    elif view == "files":
        print_lines(tuple(ref.path for ref in page.file_refs))
    elif view == "topics":
        print_lines(page.topics)


def render_full(page: PageView) -> None:
    print(metadata_header(page))
    if page.body.strip():
        print(f"\n{style.DIM}---{style.RST}\n")
        print(body_with_trailing_newline(page.body), end="")


def metadata_header(page: PageView) -> str:
    dim = style.DIM
    rst = style.RST
    lines = [
        f"{dim}slug:{rst}       {style.BLUE}{page.slug}{rst}",
        f"{dim}title:{rst}      {page.title or EM_DASH}",
    ]
    if page.summary:
        lines.append(f"{dim}summary:{rst}    {page.summary.strip()}")
    topics = ", ".join(page.topics) if page.topics else EM_DASH
    lines.append(f"{dim}topics:{rst}     {topics}")
    if page.file_refs:
        refs = ", ".join(ref.path for ref in page.file_refs)
        lines.append(f"{dim}files:{rst}      {refs}")
    if page.sources:
        lines.append(f"{dim}sources:{rst}")
        for source in page.sources:
            target = f" {source.target}" if source.target else ""
            note = f" - {source.note}" if source.note else ""
            lines.append(
                f"  {source.source_id} [{source.source_type.value}]{target}{note}"
            )
    lines.append(f"{dim}path:{rst}       {page.file_path}")
    updated = datetime.fromtimestamp(page.updated_at, tz=UTC)
    lines.append(f"{dim}updated:{rst}    {updated.isoformat()}")
    if page.page_links_out:
        lines.append(f"{dim}links:{rst}      {', '.join(page.page_links_out)}")
    if page.page_links_in:
        lines.append(f"{dim}backlinks:{rst}  {', '.join(page.page_links_in)}")
    if page.cross_wiki_links:
        xwiki = ", ".join(f"{x.wiki}:{x.target}" for x in page.cross_wiki_links)
        lines.append(f"{dim}xwiki:{rst}      {xwiki}")
    return "\n".join(lines)


def first_paragraph(body: str) -> str:
    paragraphs = [part.strip() for part in body.split("\n\n") if part.strip()]
    return paragraphs[0] if paragraphs else ""


def body_with_trailing_newline(body: str) -> str:
    if body == "" or body.endswith("\n"):
        return body
    return f"{body}\n"
