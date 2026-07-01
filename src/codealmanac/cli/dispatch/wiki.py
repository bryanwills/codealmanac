import argparse
from pathlib import Path

from codealmanac.app import CodeAlmanac
from codealmanac.cli.render.root import (
    render_health,
    render_page,
    render_reindex,
    render_search,
    render_tagging,
    render_topic,
    render_topic_edge_mutation,
    render_topic_mutation,
    render_topic_rewrite_mutation,
    render_topics,
    render_workspace_drop,
    render_workspace_list,
)
from codealmanac.services.health.requests import HealthCheckRequest
from codealmanac.services.index.requests import ReindexRequest
from codealmanac.services.pages.requests import ShowPageRequest
from codealmanac.services.search.requests import SearchPagesRequest
from codealmanac.services.tagging.requests import TagPageRequest, UntagPageRequest
from codealmanac.services.topics.requests import (
    CreateTopicRequest,
    DeleteTopicRequest,
    DescribeTopicRequest,
    LinkTopicRequest,
    ListTopicsRequest,
    RenameTopicRequest,
    ShowTopicRequest,
    UnlinkTopicRequest,
)
from codealmanac.services.workspaces.requests import DropWorkspaceRequest

WIKI_COMMANDS = frozenset(
    (
        "health",
        "list",
        "reindex",
        "search",
        "serve",
        "show",
        "tag",
        "topics",
        "untag",
    )
)


def is_wiki_command(command: str | None) -> bool:
    return command in WIKI_COMMANDS


def dispatch_wiki(args: argparse.Namespace, app: CodeAlmanac) -> int:
    if args.command == "list":
        return dispatch_list(args, app)
    if args.command == "search":
        rows = app.search.search(
            SearchPagesRequest(
                cwd=Path.cwd(),
                wiki=args.wiki,
                query=args.query,
                topics=tuple(args.topic),
                mentions=args.mentions,
                include_archive=args.include_archive,
                archived=args.archived,
                limit=args.limit,
            )
        )
        render_search(rows, json_output=args.json)
        return 0
    if args.command == "show":
        page = app.pages.show(
            ShowPageRequest(cwd=Path.cwd(), wiki=args.wiki, slug=args.slug)
        )
        render_page(page, args)
        return 0
    if args.command == "topics":
        return dispatch_topics(args, app)
    if args.command == "health":
        report = app.health.check(HealthCheckRequest(cwd=Path.cwd(), wiki=args.wiki))
        render_health(report, json_output=args.json)
        return 0
    if args.command == "reindex":
        result = app.index.reindex(ReindexRequest(cwd=Path.cwd(), wiki=args.wiki))
        render_reindex(result, json_output=args.json)
        return 0
    if args.command == "serve":
        return run_serve(app, args)
    if args.command == "tag":
        result = app.tagging.tag(
            TagPageRequest(
                cwd=Path.cwd(),
                wiki=args.wiki,
                slug=args.slug,
                topics=tuple(args.topics),
            )
        )
        render_tagging("tagged", "already tagged", result)
        return 0
    if args.command == "untag":
        result = app.tagging.untag(
            UntagPageRequest(
                cwd=Path.cwd(),
                wiki=args.wiki,
                slug=args.slug,
                topics=tuple(args.topics),
            )
        )
        render_tagging("untagged", "not tagged", result)
        return 0
    raise AssertionError(f"unhandled wiki command: {args.command}")


def dispatch_list(args: argparse.Namespace, app: CodeAlmanac) -> int:
    if args.drop is not None:
        result = app.workspaces.drop(
            DropWorkspaceRequest(selector=args.drop, base_path=Path.cwd())
        )
        render_workspace_drop(result, json_output=args.json)
        return 0
    if args.drop_missing:
        result = app.workspaces.drop_missing()
        render_workspace_drop(result, json_output=args.json)
        return 0
    render_workspace_list(app.workspaces.list_registry(), json_output=args.json)
    return 0


def dispatch_topics(args: argparse.Namespace, app: CodeAlmanac) -> int:
    if args.topic_command == "show":
        topic = app.topics.show(
            ShowTopicRequest(
                cwd=Path.cwd(),
                wiki=args.wiki,
                slug=args.slug,
                include_descendants=args.descendants,
            )
        )
        render_topic(topic)
        return 0
    if args.topic_command == "create":
        result = app.topics.create(
            CreateTopicRequest(
                cwd=Path.cwd(),
                wiki=args.wiki,
                name=args.name,
                parents=tuple(args.parent),
            )
        )
        render_topic_mutation(result)
        return 0
    if args.topic_command == "describe":
        result = app.topics.describe(
            DescribeTopicRequest(
                cwd=Path.cwd(),
                wiki=args.wiki,
                slug=args.slug,
                description=args.description,
            )
        )
        render_topic_mutation(result)
        return 0
    if args.topic_command == "link":
        result = app.topics.link(
            LinkTopicRequest(
                cwd=Path.cwd(),
                wiki=args.wiki,
                child=args.child,
                parent=args.parent,
            )
        )
        render_topic_edge_mutation(result)
        return 0
    return dispatch_topic_rewrite(args, app)


def dispatch_topic_rewrite(args: argparse.Namespace, app: CodeAlmanac) -> int:
    if args.topic_command == "unlink":
        result = app.topics.unlink(
            UnlinkTopicRequest(
                cwd=Path.cwd(),
                wiki=args.wiki,
                child=args.child,
                parent=args.parent,
            )
        )
        render_topic_edge_mutation(result)
        return 0
    if args.topic_command == "rename":
        result = app.topics.rename(
            RenameTopicRequest(
                cwd=Path.cwd(),
                wiki=args.wiki,
                old_slug=args.old_slug,
                new_slug=args.new_slug,
            )
        )
        render_topic_rewrite_mutation(result)
        return 0
    if args.topic_command == "delete":
        result = app.topics.delete(
            DeleteTopicRequest(
                cwd=Path.cwd(),
                wiki=args.wiki,
                slug=args.slug,
            )
        )
        render_topic_rewrite_mutation(result)
        return 0
    topics = app.topics.list(ListTopicsRequest(cwd=Path.cwd(), wiki=args.wiki))
    render_topics(topics)
    return 0


def run_serve(app: CodeAlmanac, args: argparse.Namespace) -> int:
    import uvicorn

    from codealmanac.server.app import create_server_app

    server = create_server_app(app, Path.cwd(), args.wiki)
    print(f"codealmanac viewer: http://{args.host}:{args.port}")
    uvicorn.run(server, host=args.host, port=args.port, log_level="warning")
    return 0
