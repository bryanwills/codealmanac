# Slice 106 - Source Address Resolution Boundaries

## Scope

Keep `SourcesService` as the service-facing facade and move source-address
syntax parsing out of `services/sources/service.py`.

## Why Now

After slice 105, `services/sources/service.py` became the largest production
file. It currently mixes service orchestration with GitHub shorthand parsing,
Git range/diff parsing, transcript source parsing, HTTP URL validation,
GitHub URL decomposition, local path classification, file fingerprinting, and
prompt-hint constants.

Cosmic Python chapter 04 frames the service layer as the entrypoint for use
cases and separates orchestration logic from interfacing code. The service
should express "resolve these user inputs," "discover transcripts," and
"inspect source runtime," while address syntax mechanics should be named and
testable separately.

## In Scope

- Move source prompt hints and address parsing to
  `services/sources/address_resolution.py`.
- Move transcript discovery ordering to `services/sources/transcripts.py`.
- Keep `SourcesService.resolve(...)`, `discover_transcripts(...)`, and
  `inspect_runtime(...)` public behavior unchanged.
- Add an architecture test that keeps URL parsing, hashing, and source-family
  resolver functions out of `service.py`.

## Out of Scope

- New source kinds.
- Changes to source address syntax.
- Changes to `SourceAddress -> SourceRef -> SourceBrief -> SourceRuntime`.
- Changes to source runtime adapters.

## Verification

- Focused source service tests.
- Focused ingest/source runtime tests that exercise resolved refs.
- Architecture boundary test.
- Service-level source-resolution dogfood.
- Full pytest, Ruff, and diff hygiene.
