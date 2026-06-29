import ast
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src/codealmanac"


def test_cli_workflows_and_services_do_not_import_integrations():
    checked_roots = (
        SRC_ROOT / "cli",
        SRC_ROOT / "workflows",
        SRC_ROOT / "services",
    )

    offenders = [
        path
        for root in checked_roots
        for path in root.rglob("*.py")
        if imports_integration(path)
    ]

    assert offenders == []


def imports_integration(path: Path) -> bool:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if is_integration_import(alias.name):
                    return True
        if (
            isinstance(node, ast.ImportFrom)
            and node.module is not None
            and is_integration_import(node.module)
        ):
            return True
    return False


def is_integration_import(module: str) -> bool:
    return module == "codealmanac.integrations" or module.startswith(
        "codealmanac.integrations."
    )
