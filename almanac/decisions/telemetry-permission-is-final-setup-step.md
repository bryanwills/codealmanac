---
title: Telemetry Permission Is Final Setup Step
topics: [decisions, setup, config, product]
sources:
  - id: telemetry-plan-transcript
    type: conversation
    path: /Users/divitsheth/.codex/sessions/2026/07/15/rollout-2026-07-15T15-13-22-019f67d7-7966-7571-b190-551f5db09c4a.jsonl
    note: Conversation that settled the setup order and telemetry permission requirements.
  - id: setup-tui
    type: file
    path: src/codealmanac/cli/dispatch/setup_tui.py
    note: Current interactive setup ordering and default-selection behavior.
  - id: setup-selections
    type: file
    path: src/codealmanac/cli/dispatch/setup_wizard/models.py
    note: Current setup selection model.
  - id: config-models
    type: file
    path: src/codealmanac/services/config/models.py
    note: Current supported config keys and user config model.
---

# Telemetry Permission Is Final Setup Step

Telemetry permission is a planned setup decision, not current runtime behavior. Future telemetry work should add telemetry as the last onboarding choice, after the user has already chosen the runner, instruction installation, model, wiki maintenance, product updates, and change-handling policy [@telemetry-plan-transcript]. The current wizard has six steps and the current config model has no telemetry key, so this decision records the intended product contract before implementation [@setup-tui] [@setup-selections] [@config-models].

## Status

Accepted for upcoming telemetry implementation. Not implemented in the current code. Implementers should update this page when `telemetry.enabled` becomes part of the config model and setup flow [@config-models] [@telemetry-plan-transcript].

## Context

Setup already asks several consent-like questions: where to install agent instructions, which local harness and model should run lifecycle jobs, whether wiki maintenance and product updates should be automated, and whether agents may commit wiki changes [@setup-tui]. The planned telemetry prompt is different because it asks permission to send anonymous usage information outside the machine. It therefore belongs after the user understands the local automation choices, not before them [@telemetry-plan-transcript].

The transcript also separates telemetry from product content. The planned copy says telemetry helps prioritize improvements and identify broken flows, while explicitly excluding code, paths, prompts, transcripts, and error text from collection [@telemetry-plan-transcript].

## Decision

The intended interactive setup order is:

1. AI provider.
2. Add instructions to `AGENTS.md` or `CLAUDE.md`.
3. Provider model.
4. Wiki maintenance.
5. Product updates.
6. Change handling.
7. Telemetry permission.

The telemetry screen should default to "Yes" and mark that option Recommended, while keeping a visible and functional "No thanks" option [@telemetry-plan-transcript]. The screen copy should explain that sharing anonymous usage helps focus improvements and fix broken experiences faster, and it must state that code, paths, prompts, transcripts, and error text are never collected [@telemetry-plan-transcript].

Non-interactive setup follows the same policy. `setup --yes` should accept telemetry, and users who bypass onboarding without an explicit choice should receive a one-time telemetry notice instead of silent enablement [@telemetry-plan-transcript].

## Consequences

Telemetry state belongs in user config as `telemetry.enabled`, and the public config surface should let users later run `codealmanac config set telemetry.enabled false` [@telemetry-plan-transcript]. That requires extending the config model and config command key list, because the current `ConfigKey` enum only covers `auto_commit`, `harness.*`, and `automation.*` keys [@config-models].

Setup implementation should keep telemetry selection in the same shaped setup data path as the other choices. The current `SetupSelections` model carries targets, harness, model, update, commit, sync, and garden settings; telemetry should be added there rather than handled as a side effect hidden in rendering code [@setup-selections].

This decision does not define the telemetry transport, event schema, storage backend, or redaction implementation. Those are separate architecture decisions. This page only fixes the setup and config contract that future telemetry work must preserve [@telemetry-plan-transcript].
