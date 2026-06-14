# Subagent Briefs

## Mill

Scope: read-only audit of the docs/almanac migration architecture and wiki/manual
maintainability.

Prompt focus:

- accidental complexity
- boundary mistakes
- stale legacy assumptions
- maintainability of docs/wiki/manual shape
- what to keep and what to simplify later

Status: timed out before returning a report and was shut down. No Mill findings
are incorporated here.

## Faraday

Scope: read-only audit of touched code boundaries.

Prompt focus:

- paths/root detection
- indexer/query behavior
- topic commands
- health
- viewer
- setup
- hand-rolled path policy
- compatibility layers that may become stale

Status: completed.

Summary:

- No shipping blocker remained after the review fixes.
- The fixed P1 issues were root detection for docs-only wikis and legacy topic
  shadowing.
- The main follow-up is to introduce a `WikiWorkspace` layout boundary with
  methods for read roots, topic files, runtime paths, and front-door page ids.

The completed findings are reflected in `smells.md`, `target-architecture.md`,
and `refactor-roadmap.md`.
