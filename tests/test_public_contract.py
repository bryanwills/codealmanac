import tomllib
from pathlib import Path

import pytest

from codealmanac.cli.main import build_parser

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = PROJECT_ROOT / "src/codealmanac"

FORBIDDEN_TOP_LEVEL_COMMANDS = (
    "absorb",
    "capture",
    "connect",
    "login",
    "mcp",
    "sdk",
    "source",
    "sources",
    "upload",
    "use",
)


def test_public_entry_point_is_codealmanac_only():
    pyproject = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text())

    scripts = pyproject["project"]["scripts"]

    assert scripts == {"codealmanac": "codealmanac.cli.main:main"}


@pytest.mark.parametrize("command", FORBIDDEN_TOP_LEVEL_COMMANDS)
def test_local_cli_rejects_hosted_and_alias_commands(
    command: str,
    capsys,
):
    parser = build_parser()

    with pytest.raises(SystemExit):
        parser.parse_args((command,))

    output = capsys.readouterr()
    assert "invalid choice" in output.err


def test_local_cli_help_does_not_advertise_hosted_or_alias_commands():
    help_text = build_parser().format_help()

    for command in FORBIDDEN_TOP_LEVEL_COMMANDS:
        assert f" {command}" not in help_text


def test_python_package_does_not_expose_sdk_or_mcp_modules():
    module_paths = {
        path.relative_to(PACKAGE_ROOT)
        for path in PACKAGE_ROOT.rglob("*.py")
        if "__pycache__" not in path.parts
    }

    assert no_path_component(module_paths, "sdk")
    assert no_path_component(module_paths, "mcp")


def no_path_component(paths: set[Path], component: str) -> bool:
    return all(component not in path.parts and path.stem != component for path in paths)
