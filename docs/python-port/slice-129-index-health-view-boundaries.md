# Slice 129: Index Health View Boundaries

## Scope

Keep `codealmanac health` behavior unchanged while splitting index health read
views by finding family.

## Out of scope

- No new health categories.
- No CLI output changes.
- No schema changes.

## Design

Cosmic Python chapter 4 separates orchestration from lower-level interfacing
code. `health_views.py` should orchestrate `HealthReport` construction, but it
should not also own every SQL query, filesystem existence check, citation regex,
and source-id helper.

The split is:

```python
index.health_views          # HealthReport facade
  -> health_graph_views.py   # page/topic/link/file integrity findings
  -> health_source_views.py  # sources/citations hygiene findings
```

This matches the current local pattern: `views.py` is a facade over read-view
families, and each view-family module owns one query reason to change.

## Verification

- Existing health behavior tests.
- Architecture guard keeping SQL, regex helpers, and finding constructors out
  of `health_views.py`.
- Real checkout dogfood: `codealmanac health --json`.
- Full pytest, Ruff, and diff checks.
