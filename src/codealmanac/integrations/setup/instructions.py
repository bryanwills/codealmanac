from importlib import resources
from pathlib import Path

from codealmanac.core.paths import home_dir
from codealmanac.services.setup.models import InstructionChange, SetupTarget

CODEALMANAC_START = "<!-- codealmanac:start -->"
CODEALMANAC_END = "<!-- codealmanac:end -->"
CLAUDE_IMPORT_LINE = "@~/.claude/codealmanac.md"


class FileInstructionInstaller:
    def __init__(self, home: Path | None = None):
        self._home = home

    def install(
        self,
        targets: tuple[SetupTarget, ...],
    ) -> tuple[InstructionChange, ...]:
        guide = read_agent_guide()
        changes: list[InstructionChange] = []
        for target in targets:
            if target == SetupTarget.CODEX:
                changes.append(self._install_codex(guide))
            elif target == SetupTarget.CLAUDE:
                changes.append(self._install_claude(guide))
            else:
                raise ValueError(f"unsupported setup target: {target.value}")
        return tuple(changes)

    def uninstall(
        self,
        targets: tuple[SetupTarget, ...],
    ) -> tuple[InstructionChange, ...]:
        changes: list[InstructionChange] = []
        for target in targets:
            if target == SetupTarget.CODEX:
                changes.append(self._uninstall_codex())
            elif target == SetupTarget.CLAUDE:
                changes.append(self._uninstall_claude())
            else:
                raise ValueError(f"unsupported setup target: {target.value}")
        return tuple(changes)

    @property
    def home(self) -> Path:
        return self._home or home_dir()

    def _install_codex(self, guide: str) -> InstructionChange:
        codex_dir = self.home / ".codex"
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

    def _uninstall_codex(self) -> InstructionChange:
        touched: list[Path] = []
        for agents_path in (
            self.home / ".codex" / "AGENTS.md",
            self.home / ".codex" / "AGENTS.override.md",
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

    def _install_claude(self, guide: str) -> InstructionChange:
        claude_dir = self.home / ".claude"
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

    def _uninstall_claude(self) -> InstructionChange:
        claude_dir = self.home / ".claude"
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


def read_agent_guide() -> str:
    resource = resources.files("codealmanac.services.setup").joinpath("agent-guide.md")
    return resource.read_text(encoding="utf-8").strip() + "\n"


def resolve_codex_agents_path(codex_dir: Path) -> Path:
    override_path = codex_dir / "AGENTS.override.md"
    override_body = read_text_if_present(override_path)
    if override_body.strip() != "":
        return override_path
    return codex_dir / "AGENTS.md"


def format_managed_block(guide: str) -> str:
    return f"{CODEALMANAC_START}\n{guide.strip()}\n{CODEALMANAC_END}"


def upsert_managed_block(contents: str, block: str) -> str:
    start = contents.find(CODEALMANAC_START)
    end = contents.find(CODEALMANAC_END)
    if start != -1 and end != -1 and end > start:
        after_end = end + len(CODEALMANAC_END)
        return f"{contents[:start]}{block}{contents[after_end:]}"
    separator = "" if contents == "" else "\n" if contents.endswith("\n") else "\n\n"
    return f"{contents}{separator}{block}\n"


def remove_managed_block(contents: str) -> str:
    start = contents.find(CODEALMANAC_START)
    end = contents.find(CODEALMANAC_END)
    if start == -1 or end == -1 or end < start:
        return contents
    after_end = end + len(CODEALMANAC_END)
    return collapse_blank_lines(f"{contents[:start]}{contents[after_end:]}")


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


def read_text_if_present(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def collapse_blank_lines(contents: str) -> str:
    while "\n\n\n" in contents:
        contents = contents.replace("\n\n\n", "\n\n")
    if contents.strip() != "" and contents.endswith("\n\n"):
        contents = contents.rstrip("\n") + "\n"
    return contents.lstrip("\n")
