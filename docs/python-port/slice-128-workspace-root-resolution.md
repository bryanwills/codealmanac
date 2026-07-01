# Slice 128: Workspace Root Resolution

## Scope

Fix current-repo wiki resolution so a broad registered parent workspace cannot
shadow a nearer initialized repo wiki.

## Out of scope

- No hosted or remote workspace behavior.
- No registry schema change.
- No automatic dropping of stale registry entries.

## Design

The resolver should follow the local product mental model: current repo first,
explicit `--wiki` when crossing repos. The initialized wiki marker is
`topics.yaml + pages/`, not `README.md`.

Cosmic Python chapter 13 argues for explicit dependencies at the service
boundary. Here, `WorkspacesService` already owns the registry dependency and
filesystem root discovery; the fix belongs in that service boundary, not in the
CLI command.

Resolution order:

```python
roots = conventional_roots + registered_custom_roots
match = nearest_almanac_root(cwd, roots)
if match:
    return register_or_refresh(match)

selected = nearest_containing_registered_workspace(cwd)
if selected and selected.almanac_path has topics.yaml + pages/:
    return selected

raise NotFoundError
```

`almanac/`, `docs/almanac/`, and `.almanac/` are conventional roots because the
manual presents them as first-class local shapes. Other repo-relative roots are
discoverable after they are recorded in the registry.

## Verification

- Workspace service tests for unregistered `.almanac/` discovery and broad
  parent registry shadowing.
- CLI dogfood in this repo: `uv run codealmanac search ...` resolves the
  current `.almanac/` instead of `/Users/rohan/Desktop/Projects/almanac`.
- Full pytest, Ruff, and diff checks.
