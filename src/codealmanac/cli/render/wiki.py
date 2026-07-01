import argparse
import sys

from codealmanac.cli.render.common import (
    index_summary,
    page_word,
    print_json_model,
    print_json_rows,
    print_lines,
)
from codealmanac.services.index.models import (
    HealthReport,
    IndexRefreshResult,
    PageView,
    SearchPageResult,
    TopicDetail,
    TopicSummary,
)
from codealmanac.services.tagging.models import TaggingResult
from codealmanac.services.topics.models import (
    TopicEdgeMutationResult,
    TopicMutationAction,
    TopicMutationResult,
    TopicRewriteMutationResult,
)


def render_search(rows: tuple[SearchPageResult, ...], json_output: bool) -> None:
    if json_output:
        print_json_rows(rows)
        return
    if len(rows) == 0:
        print("# 0 results", file=sys.stderr)
        return
    for row in rows:
        print(row.slug)


def render_reindex(result: IndexRefreshResult, json_output: bool) -> None:
    if json_output:
        print_json_model(result)
        return
    print(f"reindexed: {index_summary(result)}")


def render_page(page: PageView, args: argparse.Namespace) -> None:
    if args.json:
        print_json_model(page)
        return
    if args.body:
        print(body_with_trailing_newline(page.body), end="")
        return
    if args.links:
        print_lines(page.wikilinks_out)
        return
    if args.backlinks:
        print_lines(page.wikilinks_in)
        return
    if args.files:
        print_lines(tuple(ref.path for ref in page.file_refs))
        return
    if args.topics:
        print_lines(page.topics)
        return
    if args.meta:
        print(metadata_header(page))
        return
    if args.lead:
        print(first_paragraph(page.body))
        return
    print(body_with_trailing_newline(page.body), end="")


def metadata_header(page: PageView) -> str:
    lines = [
        f"slug: {page.slug}",
        f"title: {page.title or ''}",
        f"path: {page.file_path}",
    ]
    if page.summary:
        lines.append(f"summary: {page.summary}")
    if page.topics:
        lines.append(f"topics: {', '.join(page.topics)}")
    if page.sources:
        lines.append("sources:")
        for source in page.sources:
            target = f" {source.target}" if source.target else ""
            note = f" - {source.note}" if source.note else ""
            lines.append(
                f"  {source.source_id} [{source.source_type.value}]{target}{note}"
            )
    return "\n".join(lines)


def first_paragraph(body: str) -> str:
    paragraphs = [part.strip() for part in body.split("\n\n") if part.strip()]
    return paragraphs[0] if paragraphs else ""


def body_with_trailing_newline(body: str) -> str:
    if body == "" or body.endswith("\n"):
        return body
    return f"{body}\n"


def render_topics(rows: tuple[TopicSummary, ...]) -> None:
    for row in rows:
        title = row.title or row.slug
        print(f"{row.slug}\t{row.page_count}\t{title}")


def render_topic(topic: TopicDetail) -> None:
    print(f"slug: {topic.slug}")
    print(f"title: {topic.title or ''}")
    if topic.description:
        print(f"description: {topic.description}")
    if topic.parents:
        print(f"parents: {', '.join(topic.parents)}")
    if topic.children:
        print(f"children: {', '.join(topic.children)}")
    if topic.pages:
        print("pages:")
        for slug in topic.pages:
            print(f"  {slug}")
    else:
        print("pages: none")


def render_topic_mutation(result: TopicMutationResult) -> None:
    print(f"{result.slug}: {result.action.value}")


def render_topic_edge_mutation(result: TopicEdgeMutationResult) -> None:
    if result.action == TopicMutationAction.NO_EDGE:
        print(f"no edge {result.child} -> {result.parent}")
        return
    if result.action == TopicMutationAction.ALREADY_LINKED:
        print(f"edge {result.child} -> {result.parent} already exists")
        return
    print(f"{result.action.value} {result.child} -> {result.parent}")


def render_topic_rewrite_mutation(result: TopicRewriteMutationResult) -> None:
    if result.action == TopicMutationAction.UNCHANGED:
        print(f"topic {result.slug} unchanged")
        return
    if result.action == TopicMutationAction.RENAMED:
        print(
            f"renamed {result.slug} -> {result.new_slug} "
            f"({result.pages_updated} {page_word(result.pages_updated)} updated)"
        )
        return
    if result.action == TopicMutationAction.DELETED:
        print(
            f"deleted {result.slug} "
            f"({result.pages_updated} {page_word(result.pages_updated)} untagged)"
        )
        return
    print(f"{result.slug}: {result.action.value}")


def render_health(report: HealthReport, json_output: bool) -> None:
    if json_output:
        print_json_model(report)
        return
    render_health_section("orphans", tuple(item.slug for item in report.orphans))
    render_health_section(
        "dead_refs",
        tuple(f"{item.slug}\t{item.path}" for item in report.dead_refs),
    )
    render_health_section(
        "broken_links",
        tuple(
            f"{item.source_slug}\t{item.target_slug}" for item in report.broken_links
        ),
    )
    render_health_section(
        "broken_xwiki",
        tuple(
            f"{item.source_slug}\t{item.target_wiki}:{item.target_slug}"
            for item in report.broken_xwiki
        ),
    )
    render_health_section(
        "empty_topics",
        tuple(item.slug for item in report.empty_topics),
    )
    render_health_section(
        "empty_pages",
        tuple(item.slug for item in report.empty_pages),
    )
    render_health_section(
        "missing_source_citations",
        tuple(
            f"{item.slug}\t{item.source_id}"
            for item in report.missing_source_citations
        ),
    )
    render_health_section(
        "unused_sources",
        tuple(f"{item.slug}\t{item.source_id}" for item in report.unused_sources),
    )
    render_health_section(
        "duplicate_sources",
        tuple(f"{item.slug}\t{item.source_id}" for item in report.duplicate_sources),
    )


def render_health_section(name: str, rows: tuple[str, ...]) -> None:
    if not rows:
        print(f"{name} (0): ok")
        return
    print(f"{name} ({len(rows)}):")
    for row in rows:
        print(f"  {row}")


def render_tagging(changed_label: str, unchanged_label: str, result: TaggingResult):
    if result.changed_topics:
        print(f"{result.slug}: {changed_label} {', '.join(result.changed_topics)}")
        return
    unchanged = ", ".join(result.requested_topics)
    print(f"{result.slug}: {unchanged_label} {unchanged}")
