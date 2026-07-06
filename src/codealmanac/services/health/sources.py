from pathlib import Path
from typing import Any

import frontmatter
from yaml import YAMLError

from codealmanac.services.health.models import ValidationIssue
from codealmanac.services.wiki.frontmatter import parse_source_item
from codealmanac.services.wiki.paths import iter_page_paths, page_id_for_path


def source_shape_issues(almanac_path: Path) -> tuple[ValidationIssue, ...]:
    issues: list[ValidationIssue] = []
    for path in iter_page_paths(almanac_path):
        issues.extend(page_source_shape_issues(almanac_path, path))
    return tuple(issues)


def page_source_shape_issues(
    almanac_path: Path,
    page_path: Path,
) -> tuple[ValidationIssue, ...]:
    try:
        post = frontmatter.loads(page_path.read_text(encoding="utf-8"))
    except (OSError, YAMLError, ValueError) as error:
        return (
            source_issue(
                almanac_path,
                page_path,
                f"frontmatter could not be parsed: {error.__class__.__name__}",
            ),
        )
    sources = post.metadata.get("sources")
    if sources is None:
        return ()
    if not isinstance(sources, list | tuple):
        return (
            source_issue(almanac_path, page_path, "sources must be a list"),
        )
    return tuple(
        issue
        for index, source in enumerate(sources, start=1)
        for issue in source_entry_issues(almanac_path, page_path, index, source)
    )


def source_entry_issues(
    almanac_path: Path,
    page_path: Path,
    index: int,
    raw_source: Any,
) -> tuple[ValidationIssue, ...]:
    source = parse_source_item(raw_source)
    if source is None:
        return (
            source_issue(
                almanac_path,
                page_path,
                f"source #{index} must include id, supported type, and target",
            ),
        )
    if source.target is None:
        return (
            source_issue(
                almanac_path,
                page_path,
                f"source {source.source_id} [{source.source_type.value}] "
                "is missing a target",
            ),
        )
    return ()


def source_issue(
    almanac_path: Path,
    page_path: Path,
    message: str,
) -> ValidationIssue:
    return ValidationIssue(
        category="sources",
        message=message,
        page=page_id_for_path(almanac_path, page_path),
        path=page_path.relative_to(almanac_path).as_posix(),
    )
