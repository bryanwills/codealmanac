# Slice 33 - Public Contract Guards

Date: 2026-06-29

## Intent

Make the local-only public surface executable. The live agreement says v1 has
no hosted CLI, no compatibility aliases, no Python SDK, and no MCP server. This
slice adds tests that fail if those surfaces accidentally appear.

## Contract

- The only package script is `codealmanac`.
- Top-level CLI commands reject hosted verbs and aliases:
  `login`, `connect`, `upload`, `capture`, `absorb`, `use`, `sources`,
  `source`, `mcp`, and `sdk`.
- The Python package tree does not expose `sdk` or `mcp` modules.

## Design

The guard lives in `tests/test_public_contract.py` instead of production code.
It checks the installed public shape from three directions:

- `pyproject.toml` entry points
- `argparse` parser behavior
- `src/codealmanac/` package module names

No product command or service code changes were needed.

## Cosmic Python Transfer

Chapter 4 describes the service layer as the main application entrypoint after
the outer adapter has parsed real-world input. This slice protects that
boundary from the other side: the CLI remains an adapter over local use cases
and does not grow hosted or compatibility verbs.

## Verification

- `uv run pytest tests/test_public_contract.py`
- focused architecture/CLI verification with `tests/test_architecture.py`
- full `uv run pytest`
- full `uv run ruff check .`
- live parser smoke through `uv run codealmanac --help`
