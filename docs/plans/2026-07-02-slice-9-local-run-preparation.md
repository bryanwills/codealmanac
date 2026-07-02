# Slice 9 Plan: Local Run Preparation

Date: 2026-07-02.
Status: planned.

## Goal

Create the local run preparation workflow that connects trigger claiming,
worker workspace creation, and engine request artifacts.

This slice stops before model execution and delivery. It produces a queued
control run with concrete `source_bundle_ref` and `request_ref` fields.

## Call Shape

```python
prepared = app.workflows.local_runs.prepare_next(
    PrepareNextLocalRunRequest(repository_id=None, branch_id=None)
)
```

If no pending trigger exists, return a typed no-op result.

If a trigger is claimed:

```text
claim_next_trigger
  -> read repository and branch records
  -> create ~/.codealmanac/workspaces/<run-id>/{repo,sources,run}
  -> create detached Git worktree at expected_head_sha
  -> create ~/.codealmanac/runs/<run-id>/request.json
  -> update control run request_ref/source_bundle_ref
  -> append normalized run event
```

## Ownership

- `ControlService` owns control DB reads and run ref updates.
- `WorkerWorkspacesService` owns worker workspace paths and Git worktree port.
- `EngineRunsService` owns engine request artifact creation.
- `LocalRunPreparationWorkflow` owns orchestration across those services.

No public CLI command is added in this slice.

## Required Control Seams

Add:

```python
app.control.get_repository(GetRepositoryRequest(...))
app.control.get_branch(GetBranchRequest(...))
```

Extend:

```python
UpdateControlRunRequest(
    source_bundle_ref=...,
    request_ref=...,
)
```

## Failure Policy

If preparation fails after a trigger has been claimed, mark the control run
`failed`, store the first-line error, and append a run event. This avoids a
claimed trigger with an invisible failure.

## Tests

- No pending trigger returns `prepared=False`.
- Pending local trigger prepares worker workspace and engine request artifact.
- Control run stores `source_bundle_ref` and `request_ref`.
- Run events record preparation.
- Missing repository `local_root_path` fails the run with a normalized error.
- Architecture test keeps orchestration in workflow, not service/store/CLI.

## Docs

- Update worklog, verification matrix, progress, and next-agent brief.
- Send RelayForge update after full verification and push.
