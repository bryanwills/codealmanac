---
title: Refactoring
summary: Change architecture freely, never behavior; the baseline commit defines behavior.
topics: [style, decisions]
sources:
  - id: manual
    type: file
    path: MANUAL.md
    note: Provisional-special-cases and dead-layer rules.
  - id: cli-tests
    type: file
    path: tests/test_cli.py
    note: Behavior tests pinning observable output.
  - id: architecture-tests
    type: file
    path: tests/test_architecture.py
    note: Architecture tests pinning module layout.
---

# Refactoring

A refactor is given a baseline commit and full freedom over code organization — move files, rename modules, introduce or collapse layers, adopt a library — under one constraint: **behavior does not change**. Behavior means everything observable at the baseline commit: stdout and stderr bytes (terminal rendering included), exit codes, and what gets written to disk and databases. If a better architecture wants different output, that is a feature proposal, not a refactor.

Tests come in two classes with two rules. Behavior tests (CLI output, workflows, services) [@cli-tests] may never be weakened — only mechanical updates like import paths. Architecture tests, which pin module layout and size caps [@architecture-tests], should be updated when the layout legitimately changes; updating them is part of proposing the new shape, not cheating. Behavior is additionally proven by running the real thing: capture real command output at the baseline, re-run after the change, and diff.

Every change cites its smell — boundary pressure, mixed reasons to change, a dishonest name, a hand-rolled library duplicate. No churn: no drive-by renames, no reformat-only diffs. Existing special cases are provisional, not protected; one-off flags, fallback paths, and compatibility shims left behind by earlier sessions are the primary prey, and dead layers are deleted once callers have moved [@manual].

Work lands as small commits, each buildable and test-passing, each naming its smell in the message, so the run can be reviewed and bisected afterwards. And refusal is a valid output: if something cannot be made clean without changing behavior, the right move is a written flag proposing the behavior change — not a clever workaround [@manual].
