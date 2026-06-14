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

Subagent reports are integrated into `smells.md`, `target-architecture.md`, and
`refactor-roadmap.md` after they return.
