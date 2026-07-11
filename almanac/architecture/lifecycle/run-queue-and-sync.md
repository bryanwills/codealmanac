---
title: Run Queue And Sync
topics: [architecture, lifecycle, runs]
sources:
  - id: run_queue
    type: file
    path: src/codealmanac/workflows/run_queue/service.py
    note: Queueing, worker spawning, scheduled Garden, and drain entrypoint.
  - id: run_worker
    type: file
    path: src/codealmanac/workflows/run_queue/worker.py
    note: Worker drain loop and queued run execution.
  - id: run_models
    type: file
    path: src/codealmanac/services/runs/models.py
    note: Run specs, queue drain result, and run statuses.
  - id: sync_workflow
    type: file
    path: src/codealmanac/workflows/sync/service.py
    note: Transcript sync workflow and queue integration.
  - id: affiliation-decision
    type: file
    path: almanac/decisions/repository-affiliation-belongs-in-repository-service.md
    note: Decision that future transcript checkout matching belongs in the repository service.
---

# Run Queue And Sync

The run queue stores ingest and garden work as durable run records with specs, then starts a local worker to drain queued work [@run_queue] [@run_models]. Sync is a scanner that can enqueue ingest work; it is not itself a page-writing lifecycle operation [@sync_workflow].

This page connects the [Run Ledger](../../concepts/run-ledger) concept to lifecycle execution. The exact states and event shapes are in [Run States And Events](../../reference/runs/run-states-and-events).

## Queueing

`RunQueue.queue_ingest(...)` and `queue_garden(...)` select the target repository, build a durable run spec, and call the run service to queue the work [@run_queue]. `start_ingest(...)` and `start_garden(...)` queue the work and then spawn a worker process [@run_queue].

Scheduled Garden iterates registered repositories and skips repositories that already have an active garden run [@run_queue]. When at least one run is queued, it spawns one worker from the first queued repository root [@run_queue].

## Worker Drain

`RunQueueWorker.drain(...)` acquires a worker lock through the run service before it drains queued records [@run_worker]. If the lock is unavailable, the drain result reports `lock_acquired=False` [@run_worker] [@run_models].

For each queued run, the worker reads the stored spec and calls `IngestWorkflow.run_started(...)` or `GardenWorkflow.run_started(...)` with the existing run id [@run_worker]. A queued run without a durable spec is marked failed rather than guessed from process state [@run_worker].

## Sync Boundary

Sync discovers local transcript candidates and queues ordinary ingest runs through this queue boundary [@sync_workflow]. That keeps transcript discovery separate from authorship: sync decides what should be ingested, while ingest remains the operation that writes pages.

Future worktree support should keep that boundary. Sync may need to ask repositories which registered wiki owns a transcript working directory, but the affiliation decision belongs in the repository service rather than in sync-specific provider or workspace checks [@affiliation-decision]. See [Repository Affiliation Belongs In Repository Service](../../decisions/repository-affiliation-belongs-in-repository-service).
