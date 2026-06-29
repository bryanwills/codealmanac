# Python Port Verification Matrix

Updated: 2026-06-29

This matrix tracks evidence for the full active goal. Empty or weak evidence
means the goal remains active.

| Requirement | Implementation evidence | Test/live evidence | Remaining risk |
|---|---|---|---|
| Fresh Python codebase | pending | pending | No `src/codealmanac/` scaffold yet. |
| Based on live agreement | `docs/python-port-live-agreement.md` exists | pending | Future code must keep matching it. |
| Cosmic Python actively considered | `docs/reference/cosmic-python/` and `docs/python-port/` steering docs | pending | Need architecture tests and code shape evidence. |
| CLI exists as `codealmanac` only | pending | pending | Need pyproject script and live invocation. |
| SQLite-backed wiki/index behavior | pending | pending | Requires index schema and query tests. |
| Workflows: build, ingest, sync, garden | pending | pending | Not scaffolded. |
| Integrations behind service ports | ownership map drafted | pending | Ports/adapters not implemented yet. |
| Prompts/manual surfaces | pending | pending | Must avoid old npm prompt layout assumptions. |
| Tests and live verification | pending | pending | Need pytest/ruff and live CLI smoke commands. |
| Frequent review | pending | pending | Need code review checkpoints after meaningful slices. |
| No hosted CLI/MCP/SDK/aliases | live agreement records exclusion | pending | Need tests/rg checks once CLI exists. |

## Gates For First Slice

| Gate | Command |
|---|---|
| Formatting/lint | `uv run ruff check .` |
| Tests | `uv run pytest` |
| CLI import | `uv run codealmanac --help` |
| Live init smoke | `uv run codealmanac init <temp repo>` |

The exact commands may change once `pyproject.toml` exists. Update this matrix
when they do.
