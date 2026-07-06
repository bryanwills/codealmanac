from codealmanac.cli.render.common import print_json_model
from codealmanac.services.health.models import ValidationIssue, ValidationResult
from codealmanac.services.index.models import HealthReport


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


def render_validate(result: ValidationResult, json_output: bool) -> None:
    if json_output:
        print_json_model(result)
        return
    status = "ok" if result.ok else "failed"
    print(f"validate: {status}")
    print(f"wiki: {result.workspace_name}")
    print(f"path: {result.almanac_path}")
    if result.index is not None:
        print(f"index: {result.index.pages_indexed} pages")
    if result.ok:
        return
    print(f"issues: {len(result.issues)}")
    for issue in result.issues:
        print(f"  {format_validation_issue(issue)}")


def format_validation_issue(issue: ValidationIssue) -> str:
    parts = [issue.category]
    if issue.page:
        parts.append(issue.page)
    if issue.path:
        parts.append(issue.path)
    parts.append(issue.message)
    return "\t".join(parts)
