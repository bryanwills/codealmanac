# Slice 63 - Missing Root Hygiene

Date: 2026-06-30

## Scope

Prevent read and diagnostic commands from creating a repo-local `almanac/`
directory that contains only derived runtime state.

## Decision

An initialized Almanac root is not proven by directory existence. The root must
have a wiki marker: `README.md`, `topics.yaml`, or `pages/`. Runtime artifacts
such as `index.db`, WAL files, and `jobs/` never prove that a wiki exists.

## Implementation

- `services/workspaces/roots.py` owns `is_initialized_almanac_root()`.
- `nearest_almanac_root()` only discovers roots with wiki markers.
- Registry status reports an index-only root as `missing_almanac`.
- `IndexStore` refuses to open SQLite for missing/uninitialized roots.
- `doctor` reports a missing registered root directly and does not cascade into
  index, manual, or health checks for that workspace.
- This repo's `.gitignore` includes default-root runtime artifacts under
  `almanac/`.

## Cosmic Python Note

Chapter 6's Unit of Work pattern is useful when a service operation needs a
single atomic entrypoint over persistent repositories. This slice deliberately
does not add a Unit of Work because the failure is not transactional. The
correct boundary is earlier: validate that the wiki source root exists before
opening the derived SQLite read model.

## Verification

- Targeted missing-root repros:
  `uv run pytest tests/test_diagnostics.py::test_doctor_does_not_materialize_missing_registered_wiki tests/test_build_workflow.py::test_workspace_registry_reports_and_drops_missing_wikis tests/test_read_model.py::test_search_does_not_materialize_missing_registered_wiki -q`
- Adjacent read/diagnostic/build tests:
  `uv run pytest tests/test_diagnostics.py tests/test_read_model.py tests/test_build_workflow.py tests/test_cli.py::test_cli_doctor_json_reports_no_wiki tests/test_cli.py::test_cli_list_json_reports_registry_status tests/test_cli.py::test_cli_list_drop_missing_removes_unreachable_wikis -q`
