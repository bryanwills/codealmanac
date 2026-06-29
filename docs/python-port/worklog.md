# Python Port Worklog

## 2026-06-29

- Active goal created for a full Python rewrite using
  `docs/python-port-live-agreement.md`, Cosmic Python guidance, slow
  development, frequent review, tests, live CLI checks, and small verified
  commits.
- Current branch is `codex/python-port-archive-existing-code`.
- Existing TypeScript/Node implementation is staged under `archive/code/`.
- Local Cosmic Python reference exists as Markdown-only files under
  `docs/reference/cosmic-python/`.
- Read `MANUAL.md`, `CLAUDE.md`, `.almanac/README.md`,
  `docs/python-port-live-agreement.md`, and the CodeAlmanac Cosmic Python
  guide.
- First implementation pressure is the Python spine: packaging, CLI entrypoint,
  application composition root, workspace service, and a test harness.
- Committed archive/docs baseline as `4520812`.
- Added the first Python scaffold: `pyproject.toml`, `src/codealmanac/`,
  `tests/`, `codealmanac` console script, `create_app(...)`, workspace registry
  service, wiki scaffold service, and build workflow-backed `init`.
- Verified first scaffold with `uv run pytest`, `uv run ruff check .`,
  `uv run codealmanac --help`, and an isolated live `codealmanac init` plus
  `codealmanac list` smoke run.
- Committed the first Python scaffold as `a803f63`.
- Review pass tightened the workspace registry write path: temp files now use
  unique same-directory names, duplicate workspace names compare
  case-insensitively, and selector helpers have explicit registry-entry types.
- Re-verified the review fix with `uv run pytest`, `uv run ruff check .`, and
  an isolated live `codealmanac init` plus `codealmanac list` smoke run.

## Current Hypothesis

Start with the smallest useful spine, not with all product commands. A thin CLI
and composition root will make later services additive. The first slice should
prove that the repo can install, invoke `codealmanac`, initialize a `.almanac/`,
and run tests through service/CLI entrypoints.

## Next Hypothesis

The next slice should add the SQLite read-model spine before AI lifecycle
commands. That means `database/`, `wiki` page parsing, `index` service/search
schema, and `search`/`show` CLI commands over initialized `.almanac/pages/`.
