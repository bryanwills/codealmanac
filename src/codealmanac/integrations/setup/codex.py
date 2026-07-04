from pathlib import Path

from codealmanac.cloud.setup.models import InstructionChange, SetupTarget
from codealmanac.integrations.setup.managed_blocks import (
    format_managed_block,
    remove_managed_block,
    upsert_managed_block,
)
from codealmanac.integrations.setup.text_files import read_text_if_present


def install_codex_instructions(home: Path, guide: str) -> InstructionChange:
    codex_dir = home / ".codex"
    codex_dir.mkdir(parents=True, exist_ok=True)
    agents_path = resolve_codex_agents_path(codex_dir)
    existing = read_text_if_present(agents_path)
    block = format_managed_block(guide)
    next_body = upsert_managed_block(existing, block)
    if next_body == existing:
        return InstructionChange(
            target=SetupTarget.CODEX,
            changed=False,
            paths=(agents_path,),
            message="Codex instructions already installed",
        )
    agents_path.write_text(next_body, encoding="utf-8")
    return InstructionChange(
        target=SetupTarget.CODEX,
        changed=True,
        paths=(agents_path,),
        message="Installed Codex AGENTS instructions",
    )


def uninstall_codex_instructions(home: Path) -> InstructionChange:
    touched: list[Path] = []
    for agents_path in (
        home / ".codex" / "AGENTS.md",
        home / ".codex" / "AGENTS.override.md",
    ):
        existing = read_text_if_present(agents_path)
        if existing == "":
            continue
        removed = remove_managed_block(existing)
        if removed == existing:
            continue
        if removed.strip() == "":
            agents_path.unlink(missing_ok=True)
        else:
            agents_path.write_text(removed, encoding="utf-8")
        touched.append(agents_path)
    return InstructionChange(
        target=SetupTarget.CODEX,
        changed=len(touched) > 0,
        paths=tuple(touched),
        message=(
            "Removed Codex AGENTS instructions"
            if len(touched) > 0
            else "Codex instructions were not installed"
        ),
    )


def resolve_codex_agents_path(codex_dir: Path) -> Path:
    override_path = codex_dir / "AGENTS.override.md"
    override_body = read_text_if_present(override_path)
    if override_body.strip() != "":
        return override_path
    return codex_dir / "AGENTS.md"
