import sys

from codealmanac.cli.render.common import (
    index_summary,
    print_json_model,
    print_json_rows,
)
from codealmanac.cli.render.style import style
from codealmanac.services.index.models import IndexRefreshResult, SearchPageResult

MANY_RESULTS_THRESHOLD = 50


def render_search(
    rows: tuple[SearchPageResult, ...],
    json_output: bool,
    slugs_only: bool = False,
    limited: bool = False,
) -> None:
    if json_output:
        print_json_rows(rows)
        return
    if len(rows) == 0:
        print("# 0 results", file=sys.stderr)
        return
    for row in rows:
        print(f"{style.BLUE}{row.slug}{style.RST}")
        if not slugs_only and row.summary is not None and row.summary.strip():
            print(f"  {row.summary.strip()}")
    if not limited and len(rows) > MANY_RESULTS_THRESHOLD:
        print(
            f"codealmanac: {len(rows)} results — "
            "consider --limit or a narrower query",
            file=sys.stderr,
        )


def render_reindex(result: IndexRefreshResult, json_output: bool) -> None:
    if json_output:
        print_json_model(result)
        return
    print(f"reindexed: {index_summary(result)}")
