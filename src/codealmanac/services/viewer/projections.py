from codealmanac.services.index.models import (
    PageSourceReference,
    PageView,
    SearchPageResult,
    TopicSummary,
)
from codealmanac.services.viewer.models import (
    ViewerPageSource,
    ViewerPageSummary,
    ViewerTopicSummary,
    ViewerWorkspace,
)
from codealmanac.services.workspaces.models import Workspace


def viewer_workspace(workspace: Workspace) -> ViewerWorkspace:
    return ViewerWorkspace(
        workspace_id=workspace.workspace_id,
        name=workspace.name,
        root_path=workspace.root_path,
    )


def viewer_topic_summary(topic: TopicSummary) -> ViewerTopicSummary:
    return ViewerTopicSummary(
        slug=topic.slug,
        title=topic.title,
        description=topic.description,
        page_count=topic.page_count,
    )


def viewer_page_sources(
    sources: tuple[PageSourceReference, ...],
    citation_order: tuple[str, ...] = (),
) -> tuple[ViewerPageSource, ...]:
    citation_numbers = {
        source_id: index + 1 for index, source_id in enumerate(citation_order)
    }
    return tuple(
        sorted(
            (
                viewer_page_source(
                    source,
                    citation_number=citation_numbers.get(source.source_id),
                )
                for source in sources
            ),
            key=source_sort_key,
        )
    )


def viewer_page_source(
    source: PageSourceReference,
    citation_number: int | None = None,
) -> ViewerPageSource:
    return ViewerPageSource(
        source_id=source.source_id,
        source_type=source.source_type.value,
        target=source.target,
        title=source.title,
        retrieved_at=source.retrieved_at,
        note=source.note,
        citation_number=citation_number,
    )


def source_sort_key(source: ViewerPageSource) -> tuple[int, int, str]:
    if source.citation_number is None:
        return (1, 0, source.source_id)
    return (0, source.citation_number, source.source_id)


def page_summary_from_search(page: SearchPageResult) -> ViewerPageSummary:
    return ViewerPageSummary(
        slug=page.slug,
        title=page.title,
        summary=page.summary,
        topics=page.topics,
    )


def page_summary_from_view(page: PageView) -> ViewerPageSummary:
    return ViewerPageSummary(
        slug=page.slug,
        title=page.title,
        summary=page.summary,
        topics=page.topics,
    )
