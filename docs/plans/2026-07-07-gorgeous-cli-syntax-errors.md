# Gorgeous CLI Syntax Errors Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace raw argparse syntax failures with clear, blue CodeAlmanac screens that explain what happened and what to run next.

**Architecture:** The CLI parser edge raises shaped syntax problems, the command catalog owns command-specific guidance, and the render edge owns all terminal text. Parser modules still define syntax only; dispatch modules still translate parsed args into app calls; services remain untouched.

**Tech Stack:** Python 3.12, argparse, Pydantic models through `CodeAlmanacModel`, `StrEnum`, existing CLI render style helpers, pytest, ruff.

---

## Current Design Notes

Cosmic Python chapter 4 says the service layer defines use cases, but this work belongs below that layer: syntax mistakes happen before a request reaches the app. Chapter 10 frames command objects as intent; here the bad argv becomes a shaped `SyntaxProblem`. Chapter 13 keeps wiring at the entrypoint, so `main()` catches parser-edge errors and calls the renderer.

The clean boundary:

```python
parser = build_parser(command_catalog())

try:
    args = parser.parse_args(argv)
except CliSyntaxError as error:
    render_syntax_problem(error.problem)
    return 2

return dispatch(args)
```

## Task 1: Syntax Models And Catalog

**Files:**
- Create: `src/codealmanac/cli/syntax/models.py`
- Create: `src/codealmanac/cli/syntax/catalog.py`
- Create: `src/codealmanac/cli/syntax/__init__.py`
- Test: `tests/test_cli_syntax.py`

**Steps:**
1. Add `SyntaxProblemKind`, `CommandRow`, `CommandGuide`, and `SyntaxProblem` as Pydantic models and enums.
2. Add a `CommandCatalog` with guides for root, `jobs`, `topics`, `config`, `automation`, `sync`, `search`, and `show`.
3. Add tests proving aliases such as `jobs list` and `topics list` resolve to suggested replacements without using loose dicts.

## Task 2: Parser Error Boundary

**Files:**
- Create: `src/codealmanac/cli/parser/argument_parser.py`
- Modify: `src/codealmanac/cli/parser/root.py`
- Modify: `src/codealmanac/cli/parser/jobs.py`
- Modify: `src/codealmanac/cli/parser/wiki.py`
- Modify: `src/codealmanac/cli/parser/run_commands.py`
- Modify: `src/codealmanac/cli/parser/config.py`
- Modify: `src/codealmanac/cli/parser/automation.py`
- Modify: `src/codealmanac/cli/main.py`
- Test: `tests/test_cli_syntax.py`
- Test: `tests/test_public_contract.py`

**Steps:**
1. Create an `ArgumentParser` subclass that raises `CliSyntaxError` with a shaped `SyntaxProblem`.
2. Make `build_parser()` wire one shared catalog into every subparser through `parser_class`.
3. Keep hidden internal commands hidden from both help and error suggestions.
4. Preserve exit code `2` for syntax errors.

## Task 3: Blue Syntax Renderer

**Files:**
- Create: `src/codealmanac/cli/render/syntax.py`
- Modify: `src/codealmanac/cli/render/root.py`
- Test: `tests/test_cli_syntax.py`
- Test: `tests/test_architecture.py`

**Steps:**
1. Render `◆ codealmanac`, a short heading, the command the user typed, a replacement when available, and a command/option table.
2. Use existing `style.BLUE`, `style.BOLD`, `style.DIM`, and `table()` so output degrades cleanly when captured or piped.
3. Add architecture assertions so syntax rendering stays in `cli/render/syntax.py`.

## Task 4: Public Behavior Tests

**Files:**
- Modify: `tests/test_cli.py`
- Modify: `tests/test_public_contract.py`
- Test: `tests/test_cli_syntax.py`

**Steps:**
1. Replace tests that lock raw argparse wording with tests for readable CodeAlmanac syntax screens.
2. Cover `jobs list`, `topics list`, unknown top-level command, unknown option, required subcommand, and invalid choice.
3. Verify hidden internal commands do not appear in suggestions.

## Task 5: Docs And Verification

**Files:**
- Modify: `almanac/reference/cli/error-and-exit-code-contract.md`
- Modify: `almanac/architecture/cli/terminal-output.md`
- Modify: `almanac/reference/cli/public-command-surface.md`

**Steps:**
1. Update docs to say parser syntax errors are rendered through shaped CLI syntax problems.
2. Run focused tests:
   `uv run pytest tests/test_cli_syntax.py tests/test_cli.py tests/test_public_contract.py tests/test_architecture.py`
3. Run the default gates:
   `uv run pytest`
   `uv run ruff check .`
4. Record remaining risk if full gates expose unrelated failures.
