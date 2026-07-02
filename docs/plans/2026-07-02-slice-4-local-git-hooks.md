# Slice 4: Local Git Hook Installer

Date: 2026-07-02.
Status: implemented.

## Goal

Install, repair, and remove the local Git hooks that call the Slice 3 hidden
trigger dispatcher.

This slice does not expose the final public `codealmanac local setup` UX. It
creates the service and file adapter that local setup will call.

## Target Shape

```python
app.local_hooks.install(InstallLocalHooksRequest(repo_root=repo))
app.local_hooks.uninstall(UninstallLocalHooksRequest(repo_root=repo))
```

The installed hook block calls:

```bash
codealmanac __record-local-trigger --kind local_post_commit --cwd "$repo_root"
```

Equivalent blocks are installed for `post-merge` and `post-rewrite`.

## Ownership

- `services/local_hooks` owns product models, requests, and the service facade.
- `integrations/workspaces/git/hooks.py` owns concrete Git hook path resolution
  and hook file writes.
- CLI/setup code should later call `app.local_hooks`; it should not write hook
  files directly.

## Behavior

- Use Git to resolve hook paths with `git rev-parse --git-path hooks/<hook>`.
- Preserve user hook content.
- Upsert one managed CodeAlmanac block per hook.
- Reinstalling an unchanged hook is idempotent.
- Make installed hook files executable.
- Uninstall removes only the managed CodeAlmanac block.
- Hook scripts must never fail the user's Git operation; generated commands end
  with `|| true` and redirect normal output.

## Out Of Scope

- Public `local setup` CLI.
- Branch policy commands.
- Worker run creation from trigger events.
- Shelling out to execute the hook in tests.

## Implementation Plan

1. Add local hook models and request objects.
2. Add a `LocalGitHookManager` port and `LocalHooksService`.
3. Add a Git hook manager integration that upserts/removes managed blocks.
4. Wire `app.local_hooks` in `create_app()`.
5. Add tests for install, repair/idempotency, preserving user content, and
   uninstall.
6. Update launch docs/worklog/verification evidence.

## Verification

Run:

```bash
uv run pytest tests/test_local_hooks.py tests/test_architecture.py
uv run ruff check .
git diff --check
```

Run full `uv run pytest` before committing.

## Result

Implemented `app.local_hooks` with install/uninstall service methods and a Git
hook file adapter.

The adapter installs managed CodeAlmanac blocks into:

```text
post-commit
post-merge
post-rewrite
```

Each block calls `codealmanac __record-local-trigger` with the corresponding
local trigger kind, redirects output, and ends with `|| true` so the user's Git
operation is not blocked.

Focused verification passed:

```text
uv run pytest tests/test_local_hooks.py tests/test_architecture.py
53 passed

uv run ruff check .
passed

git diff --check
passed
```
