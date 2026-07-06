import sys

from codealmanac.cli.render.common import print_json_model, print_json_rows
from codealmanac.cli.render.style import EM_DASH, pad_visible, style
from codealmanac.services.workspaces.models import (
    DropWorkspaceResult,
    WorkspaceListResult,
)


def render_workspace_list(result: WorkspaceListResult, json_output: bool) -> None:
    if json_output:
        print_json_rows(result.items)
        return
    if len(result.items) == 0:
        print(
            f"{style.DIM}no wikis registered. "
            f"run `codealmanac init` in a repo to create one.{style.RST}"
        )
        return
    name_width = min(
        30,
        max(len(item.workspace.name) for item in result.items),
    )
    for item in result.items:
        workspace = item.workspace
        name = pad_visible(workspace.name, name_width)
        description = workspace.description or EM_DASH
        print(f"{style.BLUE}{style.BOLD}{name}{style.RST}  {description}")
        print(f"{' ' * name_width}  {style.DIM}{workspace.root_path}{style.RST}")


def render_workspace_drop(result: DropWorkspaceResult, json_output: bool) -> None:
    if json_output:
        print_json_model(result)
        return
    if len(result.dropped) == 0:
        print("# 0 wikis dropped", file=sys.stderr)
        return
    for workspace in result.dropped:
        print(f"dropped {workspace.name} ({workspace.root_path})")
