# Refactor Roadmap

## Phase 0: Preserve The Baseline

Goal:

Keep a behavior gate before refactoring.

Changes:

- Keep `uv run pytest`, `uv run ruff check .`, and targeted CLI smoke checks as
  gates.
- Record any baseline behavior questions in `product-slop.md` instead of
  changing behavior.

Verification:

- Full pytest and ruff pass before each milestone commit.

## Phase 1: Split Setup Rendering

Goal:

Make terminal rendering easier to extend without changing setup output.

Changes:

- Extract brand constants/banner behavior from `cli/render/setup.py`.
- Extract generic ANSI terminal helpers from `cli/render/setup.py`.
- Extract interactive setup screen rendering from setup result rendering.
- Keep Rich usage in `cli/render/`.

Why first:

It is the largest production Python file by a wide margin and has a clear
boundary smell.

Risk:

Terminal output is behavior. Use existing tests and focused CLI output checks.

Verification:

- Setup/uninstall CLI tests.
- Architecture tests for Rich boundary.
- Full pytest and ruff.

## Phase 2: Make App Wiring Easier To Scan

Goal:

Keep `app.py` as the composition root while reducing scanning cost.

Changes:

- Group wiring into honest helpers only if the helper names match real
  dependency groups.
- Avoid a generic container or registry.
- Keep concrete integrations wired from the composition root layer.

Why second:

After setup rendering, `app.py` is the largest Python code-shape pressure point
near the top of the architecture.

Risk:

Over-extraction can hide product wiring. Stop if helpers make the file less
obvious.

Verification:

- App import tests through the full suite.
- Focused CLI smoke for `--help` and non-AI commands.

## Phase 3: Rework Architecture Tests Where They Block Good Names

Goal:

Keep architecture tests strong without preserving accidental slice artifacts.

Changes:

- Convert exact-fragment assertions to ownership assertions when refactoring a
  covered boundary.
- Add new architecture tests only for durable boundaries.

Why third:

Tests should move with real architecture changes, not before.

Risk:

Weakening tests could allow old mixed modules to regrow.

Verification:

- Review changed tests against `almanac/style/boundaries.md`.
- Full pytest and ruff.

## Phase 4: Audit Facades

Goal:

Keep stable facades and delete stale import-only husks.

Changes:

- List all facade modules.
- For each one, classify as service boundary, command boundary, package API, or
  stale import compatibility.
- Delete only stale facades with all callers moved.

Why fourth:

Facade deletion is easy to overdo. Do it after the large obvious split.

Risk:

Breaking imports that are part of the intended public internal boundary.

Verification:

- Full pytest and ruff.
- `rg` confirms removed facade imports are gone.

## Phase 5: Repeat With Smaller Local Smells

Goal:

Continue improving until returns diminish.

Candidate areas:

- sync workflow file grouping;
- run store facade;
- setup planning/output names;
- viewer service DTO projection names;
- provider event naming consistency.

Stop condition:

Stop when the next candidate is mostly taste, not boundary pressure, and the
branch has passing gates plus clear docs.
