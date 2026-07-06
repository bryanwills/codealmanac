from codealmanac.cli.render.common import page_word
from codealmanac.cli.render.style import EM_DASH, style, table
from codealmanac.services.index.models import TopicDetail, TopicSummary
from codealmanac.services.topics.models import (
    TopicEdgeMutationResult,
    TopicMutationAction,
    TopicMutationResult,
    TopicRewriteMutationResult,
)


def render_topics(rows: tuple[TopicSummary, ...]) -> None:
    if len(rows) == 0:
        print(
            "no topics. create one with `codealmanac topics create <name>` "
            "or tag a page."
        )
        return
    lines = table(
        ("TOPIC", "PAGES", "TITLE"),
        [
            (
                f"{style.BLUE}{row.slug}{style.RST}",
                f"{style.DIM}({row.page_count} {page_word(row.page_count)}){style.RST}",
                row.title or "",
            )
            for row in rows
        ],
    )
    for line in lines:
        print(line)


def render_topic(topic: TopicDetail, descendants: bool = False) -> None:
    dim = style.DIM
    rst = style.RST
    print(f"{dim}slug:{rst}         {style.BLUE}{topic.slug}{rst}")
    print(f"{dim}title:{rst}        {topic.title or EM_DASH}")
    print(f"{dim}description:{rst}  {topic.description or EM_DASH}")
    parents = ", ".join(topic.parents) if topic.parents else EM_DASH
    print(f"{dim}parents:{rst}      {parents}")
    children = ", ".join(topic.children) if topic.children else EM_DASH
    print(f"{dim}children:{rst}     {children}")
    label = "pages (incl. descendants)" if descendants else "pages"
    print(f"{dim}{label}:{rst}")
    if topic.pages:
        for slug in topic.pages:
            print(f"  {style.BLUE}{slug}{rst}")
    else:
        print(f"  {EM_DASH}")


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
