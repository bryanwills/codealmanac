# Product Slop And Open Questions

This file tracks behavior that may be making the architecture more complicated
than necessary. Do not change these behaviors during the refactor unless Rohan
explicitly decides they are not product requirements.

## Public `config` Command

Observation:

- `codealmanac --help` exposes `config`.
- `README.md` documents `codealmanac config set auto_commit false`.
- Tests cover `codealmanac config set`.
- `docs/python-port-live-agreement.md` also contains an older line saying not
  to add a public `config` command until a later agreement requires it.

Architectural cost:

The config service is legitimate either way, but a public config command adds
parser, dispatch, rendering, tests, and user-facing support burden.

Question:

Is the narrow public `config set` surface now an intentional product decision,
or did it slip in because setup needed a way to persist `auto_commit`?

Current refactor stance:

Preserve behavior. Treat the contradictory live-agreement line as stale until
Rohan decides otherwise.

## Setup Raw Terminal Choice UI

Observation:

- `cli/dispatch/setup_tui.py` and `cli/render/setup.py` implement an
  interactive raw-mode setup choice flow.
- The terminal output and cards are rich product polish, but they add a lot of
  bespoke rendering mechanics.

Architectural cost:

The CLI now owns a mini terminal UI system, not just command output rendering.

Question:

Is raw-mode interactive setup a core product requirement, or would plain flags
plus polished noninteractive output be enough?

Current refactor stance:

Preserve behavior and isolate the machinery so it does not spread.

## Setup Default Auto-Update

Observation:

- The live agreement says plain `setup --yes` installs sync, Garden, and daily
  update automation.
- Scheduled update has lock, editable-install detection, active-run checks, and
  post-update smoke checks.

Architectural cost:

Auto-update creates global locking, package-manager detection, scheduler
commands, install-method support, and smoke-check behavior.

Question:

Is default scheduled product update essential for v1 trust, or should it be an
explicit opt-in because package self-mutation is a large support surface?

Current refactor stance:

Preserve behavior. Keep update automation as an explicit service boundary.

## Full Uninstall Removes The Installed Tool

Observation:

- The live agreement says `uninstall` removes CodeAlmanac-owned instructions,
  automation, global state, and the installed binary when supported.

Architectural cost:

Self-uninstall requires package-manager detection and command execution from
inside the tool that may remove itself.

Question:

Is binary removal part of the product promise, or should uninstall mean
"remove CodeAlmanac local state and agent hooks" while package managers own
the installed executable?

Current refactor stance:

Preserve behavior. Keep package uninstall behind the setup service port.

## `build` As A Lifecycle Operation

Observation:

- `build` appears beside `ingest` and `garden` as an AI page-writing workflow.
- `init` also exists as a non-AI wiki bootstrap command.

Architectural cost:

The distinction is clear after reading docs, but the product words are close:
one initializes the tree, the other asks an agent to build wiki content.

Question:

Is `build` the right public word, or does it invite confusion with package
builds and index rebuilds?

Current refactor stance:

Preserve behavior and names. Improve internal boundaries only.
