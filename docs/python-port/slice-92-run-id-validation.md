# Slice 92 - Shared Run ID Validation

## Scope

Move run-id validation from the viewer adapter into the runs product model.

This slice covers:

- a shared Pydantic-constrained `RunId` type
- replacing hand-rolled viewer run-id character validation
- applying `RunId` to run request models, run records, run log events, and
  workflow requests that accept an existing run id
- tests proving invalid run ids fail before path construction in CLI, service,
  and viewer/server boundaries

Out of scope:

- changing generated run-id format
- changing sync ledger fields such as `pending_run_id`
- changing page-source `run_id` fields for conversation provenance
- changing store file layout under `<almanac-root>/jobs/`

## Current Shape

`ViewerJobRequest` has a local `SAFE_RUN_ID_CHARACTERS` set and a
`field_validator`. Core runs requests such as `ShowRunRequest`,
`ReadRunLogRequest`, `AttachRunRequest`, and `CancelRunRequest` still accept
plain strings. `RunStore` then builds paths such as
`jobs/{run_id}.json`.

That means the browser route is protected, but CLI/service calls can still pass
path-shaped run ids into the store layer.

## Design

```python
# arch: product invariant lives with the product noun
RunId = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, pattern=RUN_ID_PATTERN),
]

class ShowRunRequest(CodeAlmanacModel):
    run_id: RunId

class RunRecord(CodeAlmanacModel):
    run_id: RunId

class ViewerJobRequest(CodeAlmanacModel):
    run_id: RunId
```

Cosmic Python chapter 10 says commands "capture intent" and fail noisily. A
run-inspection command with an invalid run id should fail at request
construction, before it reaches path-based persistence.

## Validation Rule

Generated run ids currently look like:

```text
ingest-20260701105703-b17052e7
```

The shared rule allows ASCII letters, digits, underscore, and hyphen:

```text
^[A-Za-z0-9_-]+$
```

That preserves current generated ids and rejects path separators, dots, spaces,
empty strings, URL-ish strings, and shell-ish punctuation.

## Tests

- Runs request tests reject `../secret`, `run.json`, whitespace-only, and
  space-containing run ids.
- Existing viewer invalid-job test should still pass without a viewer-local
  validator.
- CLI jobs test should reject an invalid run id with a validation error before
  looking for a file.
- Server jobs route should still map invalid run ids to HTTP 422.
