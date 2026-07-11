---
title: Provider Adapters
topics: [architecture, harnesses, providers, agent-runs]
sources:
  - id: yoke-adapter
    type: file
    path: src/codealmanac/integrations/harnesses/yoke/adapter.py
  - id: yoke-events
    type: file
    path: src/codealmanac/integrations/harnesses/yoke/events.py
  - id: yoke-results
    type: file
    path: src/codealmanac/integrations/harnesses/yoke/results.py
  - id: harness-defaults
    type: file
    path: src/codealmanac/integrations/harnesses/__init__.py
  - id: harness-kinds
    type: file
    path: src/codealmanac/services/harnesses/kinds.py
  - id: harness-ports
    type: file
    path: src/codealmanac/services/harnesses/ports.py
  - id: harness-results
    type: file
    path: src/codealmanac/services/harnesses/results.py
  - id: yoke-tests
    type: file
    path: tests/test_yoke_harness_integration.py
---

# Provider Adapters

Provider adapters are the integration edge behind the [harness contract](harness-contract). They translate CodeAlmanac's normalized harness request into provider-specific execution, then translate provider output back into normalized results, events, transcripts, and optional changed-file reports. The current default adapter family is `YokeHarnessAdapter`, which is instantiated once for Claude and once for Codex [@yoke-adapter] [@harness-defaults].

This boundary keeps lifecycle workflows provider-neutral. Build, ingest, garden, queue workers, and job logs consume the same result shape no matter which provider ran the agent. Provider quirks stay in `integrations/harnesses/yoke/`, which is where readiness projection, provider options, timeout settings, event mapping, and result conversion live [@yoke-adapter] [@yoke-events] [@yoke-results].

## Shared Adapter Responsibilities

Every adapter implements the same service-owned contract: `check()` reports readiness and `run()` returns a `HarnessRunResult` [@harness-ports] [@harness-results]. `YokeHarnessAdapter.check()` calls the Yoke readiness check and projects it into `HarnessReadiness`; missing binaries, timeouts, and Yoke errors become unavailable readiness results instead of escaping as provider exceptions [@yoke-adapter].

`YokeHarnessAdapter.run()` forwards the exact rendered prompt, model, working directory, and optional lifecycle agent kind into Yoke run options, then projects the finished Yoke run into CodeAlmanac's normalized result model [@yoke-adapter] [@yoke-tests]. The adapter does not run a Git change probe around provider execution. `changed_files` remains part of the result model, but the real Yoke-backed provider path returns provider output, events, and transcript metadata without computing a repository diff [@harness-results] [@yoke-results] [@yoke-tests].

## Provider Options

The supported harness kinds are `codex` and `claude`, and default app construction registers one Yoke adapter for each kind [@harness-kinds] [@harness-defaults]. `create_yoke_harness()` uses Yoke's `Harness` with the selected provider, the run working directory, a lifecycle agent, and full-access permissions with approval disabled and network disabled [@yoke-adapter].

Codex runs through Yoke's Codex app-server surface with `danger-full-access`, approval `never`, network disabled, and an ephemeral app-server option [@yoke-adapter]. Claude runs with the file/search/shell/helper-agent tool set, `permission_mode="dontAsk"`, partial messages enabled, no settings sources, and an empty strict MCP config [@yoke-adapter]. Tests lock these provider-specific options because lifecycle runs depend on noninteractive provider behavior [@yoke-tests].

## Event And Result Projection

`YokeEventProjector` maps Yoke events into `HarnessEvent` values. It preserves provider ids, tool display data, token usage, tool inputs and results, provider session ids, source thread ids, and actor information when Yoke provides those fields [@yoke-events]. Unknown future Yoke event kinds project to the normalized `unknown` event kind and keep JSON-safe payloads, so a provider event addition does not break run logging [@yoke-events] [@yoke-tests].

Helper-agent events are normalized at this boundary. For Codex, helper actors are identified from source thread ids; for Claude, helper actors are derived from provider parent tool-use ids. The projector emits spawn, wait, and completion events once per helper lifecycle so job logs can show helper activity without parsing raw provider transcripts [@yoke-events] [@yoke-tests].

`project_run()` turns the Yoke run status, output, failure, provider session id, and events into `HarnessRunResult` [@yoke-results]. It ensures the event stream ends with exactly one `done` event and attaches the projected failure data to that terminal event when the provider reports a failure [@yoke-results] [@yoke-tests].

## Adding Providers

A new provider should be added by extending the adapter family, not by branching lifecycle workflows. The [add a harness provider adapter](../../guides/add-a-harness-provider-adapter) guide covers the mechanical path; architecturally, the provider must satisfy the same readiness, request, result, event, and transcript contract. It should only populate `changed_files` when the adapter has an intentional, tested mechanism for that field.

Model choice is a separate configuration concern. The [controlled model catalog](../../decisions/controlled-model-catalog) decision explains why CodeAlmanac owns its supported runner and model configuration instead of discovering arbitrary provider models at runtime.
