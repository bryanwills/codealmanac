# Slice 71: Production conversation-trigger smoke

## Scope

Prove the launched cloud pipeline uses captured conversations when a maintained
branch is pushed.

The required production behavior is:

1. a Codex capture credential uploads a completed, routable turn for
   `AlmanacCode/codealmanac` on a test branch
2. the test branch is enabled as a maintained branch with delivery mode
   `commit`
3. a GitHub branch push triggers a run
4. the run source is `conversation_batch`, not plain `branch`
5. the temporary branch, trigger policy, capture credential, temp home, and
   temp worktree are cleaned up

## Out Of Scope

- Do not change WorkOS/AuthKit.
- Do not change public setup copy unless the smoke exposes a user-facing bug.
- Do not implement rate limits.
- Do not keep the smoke branch or capture credential after verification.
- Do not chase old failed smoke runs from stale worker images.

## Design

The service-layer reference says the use case should sit behind the entrypoint;
the command reference separates user intent from facts. This slice uses the
public CLI for user intent and SQL only for internal proof:

```text
temp HOME + copied cloud auth
  -> codealmanac capture enable --target codex
  -> codealmanac __capture-hook --provider codex < synthetic transcript payload
  -> codealmanac repo triggers enable <smoke-branch> --delivery commit
  -> git push origin <smoke-branch>
  -> codealmanac runs list/show
  -> SQL verifies runs.source_json.kind == "conversation_batch"
```

The synthetic transcript uses a real git checkout on the smoke branch. The
normal capture hook probes that checkout for repo, branch, and head SHA, so the
turn is routed through the same capture path agents use.

## Files

- `docs/codealmanac-launch/worklog.md`
- `docs/codealmanac-launch/progress.md`
- `docs/codealmanac-launch/next-agent-brief.md`
- `docs/codealmanac-launch/verification-matrix.md`

Code changes are only expected if production fails this contract.

## Verification

- Published CLI `0.1.4` can issue and revoke a temporary capture credential.
- `__capture-hook` returns `upload_status: uploaded` and
  `routing_status: routable`.
- GitHub push creates a new production run on the smoke branch.
- The new run has `source.kind == "conversation_batch"`.
- Production run reaches a terminal status or emits enough events to diagnose a
  real worker/provider issue.
- Cleanup leaves no active capture credential, no enabled smoke trigger, and no
  remote smoke branch.

## Cleanup

Always attempt cleanup, even on failure:

```text
codealmanac capture disable --target codex
codealmanac repo triggers disable <smoke-branch>
git push origin --delete <smoke-branch>
git worktree remove <temp-worktree> --force
rm -rf <temp-home>
```

## Failure Rule

If the live run is plain `branch` despite a routable completed turn on the same
repo and branch, inspect and fix hosted conversation claiming before sending the
slice update. If the run is `conversation_batch` but the worker fails, diagnose
the worker/run events before deciding whether this slice needs code.
