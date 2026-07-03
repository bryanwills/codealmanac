# Slice 8 Plan: Local Worker Workspaces

Date: 2026-07-02.
Status: planned.

## Goal

Add the local engine workspace contract used before engine execution.

This slice creates deterministic per-run directories and a Git-native detached
worktree at the expected head SHA. It does not run the model, select sources,
or deliver changes.

## Contract

Local engine workspaces live under:

```text
~/.codealmanac/workspaces/<run-id>/
  repo/
  sources/
  run/
```

Call shape:

```python
workspace = app.engine_workspaces.prepare(
    PrepareEngineWorkspaceRequest(
        run_id=run.id,
        repository_root_path=repo.local_root_path,
        expected_head_sha=run.expected_head_sha,
    )
)

engine = app.engine_runs.prepare(
    PrepareEngineRunRequest(
        repo_path=workspace.paths.repo_path,
        sources_path=workspace.paths.sources_path,
        ...
    )
)
```

## Ownership

```text
services/engine_workspaces/
  models.py      # path/result models
  requests.py    # prepare/remove commands
  ports.py       # GitWorktreeManager protocol
  store.py       # filesystem layout only
  service.py     # prepare/remove verbs

integrations/workspaces/git/worktree.py
  GitDetachedWorktreeManager
```

The service owns product verbs and paths. The Git integration owns
`git worktree add --detach` and `git worktree remove --force`.

## Decisions

- Use a detached worktree at `expected_head_sha`, not a copied repository.
  This uses Git's native object store and keeps the run snapshot deterministic.
- Do not create `repo/` before calling Git; `git worktree add` owns that path.
- Create `sources/` and `run/` as empty directories now. Later source bundling
  and engine artifact code will populate them by reference.
- Default behavior rejects an existing run workspace. Run ids should be unique;
  destructive replacement needs an explicit later verb.
- Do not make this public CLI yet. It is an app/service seam for the local
  worker.

## Tests

- Default engine workspace root is `~/.codealmanac/workspaces`.
- Preparing a workspace creates `sources/` and `run/`, calls the Git worktree
  port with the expected SHA, and returns typed paths.
- Existing workspace paths raise a conflict instead of being silently removed.
- The concrete Git integration creates a real detached worktree at a commit SHA.
- Architecture tests keep Git/subprocess mechanics out of the service/store.

## Docs

- Update worklog, verification matrix, progress, and next-agent brief.
- Send a RelayForge update after verification and push.
