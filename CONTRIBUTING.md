# Contributing to CodeAlmanac

CodeAlmanac is a local codebase wiki for AI coding agents. A good contribution
keeps the command surface scriptable, the wiki artifact repo-owned, and the
code shape easy for the next maintainer to extend.

## Start Here

```bash
git clone https://github.com/AlmanacCode/codealmanac.git
cd codealmanac
uv sync
uv run codealmanac --help
```

For local CLI testing, prefer `uv run codealmanac ...` from the checkout. To
test the installed package path, use `uv tool install --force .` in a disposable
environment.

## Development Checks

Run these before opening a pull request:

```bash
uv run pytest
uv run ruff check .
uv build
```

Use focused pytest runs while developing, then run the full suite before review.

## Working With The Codebase

- Read `README.md`, `MANUAL.md`, and `docs/concepts.md` for the product model.
- Search the local `.almanac/` wiki before changing a real subsystem.
- Keep changes local-first. Repo wiki data lives under the configured Almanac
  root, which defaults to `almanac/`. User state lives in `~/.codealmanac/`.
- Keep commands scriptable. Avoid interactive prompts in CLI flows.

## Tests And Fixtures

Tests use pytest. Tests that touch user state should use the `isolated_home`
fixture so they write under a temp `~/.codealmanac/`, not the real registry.

Prefer creating real initialized wikis through:

```python
app.workflows.build.initialize(InitializeWorkspaceRequest(path=repo))
```

Synthetic wiki fixtures must include both source markers:

```text
<almanac-root>/topics.yaml
<almanac-root>/pages/
```

`README.md` alone is not a wiki marker.

## Pull Request Shape

A good pull request includes:

- A clear problem statement.
- The design choice, including rejected alternatives when architecture changes.
- Tests or a short explanation of why no automated test is useful.
- Any docs or wiki updates needed for future agents.

Keep pull requests buildable and scoped. Avoid unrelated formatting churn.

## Commit Conventions

Use the existing commit style:

- `feat(slice-N): <summary>` for new slice work.
- `fix(slice-N-review): <summary>` for review fixes.
- `docs: <summary>` for documentation-only changes.
- `refactor(slice-N): <summary>` for structural cleanup within a slice.
