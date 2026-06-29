# Python Port Verification Matrix

Updated: 2026-06-29

This matrix tracks evidence for the full active goal. Empty or weak evidence
means the goal remains active.

| Requirement | Implementation evidence | Test/live evidence | Remaining risk |
|---|---|---|---|
| Fresh Python codebase | `pyproject.toml`, `src/codealmanac/`, `tests/` | `uv run pytest`, `uv run ruff check .` passed on 2026-06-29 | Only the first scaffold exists; most product services remain pending. |
| Based on live agreement | `docs/python-port-live-agreement.md`, `src/codealmanac/app.py`, service/workflow packages | first tests exercise CLI -> app -> build workflow -> workspaces/wiki | Need future architecture tests as more services appear. |
| Cosmic Python actively considered | `docs/reference/cosmic-python/`, `docs/python-port/`, `app.py` composition root, service-layer tests | tests call workflow/service and CLI surfaces instead of private helpers | Need deeper store/index transaction tests in later slices. |
| CLI exists as `codealmanac` only | `[project.scripts] codealmanac = "codealmanac.cli.main:main"` | `uv run codealmanac --help` passed on 2026-06-29 | Current CLI only implements `init` and `list`. |
| SQLite-backed wiki/index behavior | pending | pending | Requires index schema and query tests. |
| Workflows: build, ingest, sync, garden | pending | pending | Not scaffolded. |
| Integrations behind service ports | ownership map drafted | pending | Ports/adapters not implemented yet. |
| Prompts/manual surfaces | pending | pending | Must avoid old npm prompt layout assumptions. |
| Tests and live verification | pytest/ruff configured in `pyproject.toml` | `uv run pytest`, `uv run ruff check .`, `uv run codealmanac --help`, live temp `init`/`list` passed | Need broader live checks as commands land. |
| Frequent review | pending | pending | Need code review checkpoints after meaningful slices. |
| No hosted CLI/MCP/SDK/aliases | live agreement records exclusion | pending | Need tests/rg checks once CLI exists. |

## Gates For First Slice

| Gate | Command | 2026-06-29 result |
|---|---|
| Formatting/lint | `uv run ruff check .` | passed |
| Tests | `uv run pytest` | 5 passed |
| CLI import | `uv run codealmanac --help` | passed |
| Live init smoke | `HOME=<tmp>/home uv run codealmanac init <temp repo>` | passed |
