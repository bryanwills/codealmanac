# CodeAlmanac Architecture Refactor Audit

Date: 2026-07-03
Status: active design notes

This folder tracks the architecture cleanup pass for both repositories:

- `codealmanac`: public Python package, CLI, local engine, local control plane, local wiki reader.
- `codealmanac-hosted`: hosted frontend, FastAPI backend, GitHub App/webhooks, WorkOS, billing, Modal worker, production deployments.

The goal is not cosmetic file movement. The goal is to make the codebase feel newly built around the product model we converged on:

```text
trigger -> source bundle -> run -> delivery -> wiki
```

That model exists in both local and cloud, but the implementations differ.

## Current Judgment

The current code works better than it reads.

The main problem is naming and package shape:

- `services/` and `workflows/` overlap.
- `runs`, `engine_runs`, `local_runs`, `local_jobs`, and `run_queue` are too close to one another.
- Hosted has a broad `updates` service that actually contains trigger policy, run records, source bundling, worker orchestration, cancellation, completion, and delivery.
- Hosted Modal code lives as top-level `backend/modal_app`, even though it is a first-class worker edge of the hosted product.
- Hosted package name is still `almanac`; long term it should become `codealmanac_hosted`.

The refactor should be product-area-first, not layer-first.

## Design Principle

Separate by reason to change:

- `web` changes when HTTP/API shape changes.
- `cli` changes when terminal UX changes.
- `worker` changes when Modal/local worker execution changes.
- `integrations` change when providers change.
- product domains change when product nouns change.

The public CLI names do not need to dictate package names. The package should make the internal product model obvious.

