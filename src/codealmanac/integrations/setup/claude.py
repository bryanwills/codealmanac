from pathlib import Path

from codealmanac.cloud.setup.models import InstructionChange, SetupTarget
from codealmanac.integrations.setup.managed_blocks import collapse_blank_lines
from codealmanac.integrations.setup.text_files import read_text_if_present

CLAUDE_IMPORT_LINE = "@~/.claude/codealmanac.md"


def install_claude_instructions(home: Path, guide: str) -> InstructionChange:
    claude_dir = home / ".claude"
    claude_dir.mkdir(parents=True, exist_ok=True)
    guide_path = claude_dir / "codealmanac.md"
    claude_md_path = claude_dir / "CLAUDE.md"

    touched: list[Path] = []
    if read_text_if_present(guide_path) != guide:
        guide_path.write_text(guide, encoding="utf-8")
        touched.append(guide_path)

    existing = read_text_if_present(claude_md_path)
    next_body = ensure_import_line(existing)
    if next_body != existing:
        claude_md_path.write_text(next_body, encoding="utf-8")
        touched.append(claude_md_path)

    return InstructionChange(
        target=SetupTarget.CLAUDE,
        changed=len(touched) > 0,
        paths=tuple(touched) or (guide_path, claude_md_path),
        message=(
            "Installed Claude instructions"
            if len(touched) > 0
            else "Claude instructions already installed"
        ),
    )


def uninstall_claude_instructions(home: Path) -> InstructionChange:
    claude_dir = home / ".claude"
    guide_path = claude_dir / "codealmanac.md"
    claude_md_path = claude_dir / "CLAUDE.md"
    touched: list[Path] = []

    if guide_path.exists():
        guide_path.unlink()
        touched.append(guide_path)

    existing = read_text_if_present(claude_md_path)
    if existing != "":
        next_body = remove_import_line(existing)
        if next_body != existing:
            if next_body.strip() == "":
                claude_md_path.unlink(missing_ok=True)
            else:
                claude_md_path.write_text(next_body, encoding="utf-8")
            touched.append(claude_md_path)

    return InstructionChange(
        target=SetupTarget.CLAUDE,
        changed=len(touched) > 0,
        paths=tuple(touched),
        message=(
            "Removed Claude instructions"
            if len(touched) > 0
            else "Claude instructions were not installed"
        ),
    )


def ensure_import_line(contents: str) -> str:
    if has_import_line(contents):
        return contents
    separator = "" if contents == "" else "\n" if contents.endswith("\n") else "\n\n"
    return f"{contents}{separator}{CLAUDE_IMPORT_LINE}\n"


def remove_import_line(contents: str) -> str:
    eol = "\r\n" if "\r\n" in contents else "\n"
    lines = contents.splitlines()
    kept = [line for line in lines if line.strip() != CLAUDE_IMPORT_LINE]
    if len(kept) == len(lines):
        return contents
    body = eol.join(kept)
    if contents.endswith(("\n", "\r\n")) and body != "":
        body += eol
    return collapse_blank_lines(body)


def has_import_line(contents: str) -> bool:
    return any(line.strip() == CLAUDE_IMPORT_LINE for line in contents.splitlines())
