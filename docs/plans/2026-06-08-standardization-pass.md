# Standardization Pass

## Goal

Finish the post-refactor cleanup by standardizing user-facing error handling and vocabulary around the lifecycle commands.

## Vocabulary Decision

`capture`, `ingest`, `garden`, `migrate`, `sources`, and `absorb` should not collapse into one name.

- `capture` is the user command for updating the wiki from AI coding sessions.
- `ingest` is the user command for updating the wiki from user-supplied files, folders, PRs, issues, or URLs.
- `garden` is the user command for wiki maintenance that needs agent judgment.
- `migrate legacy-sources` is deterministic wiki-file migration.
- `sources` is wiki frontmatter evidence.
- `absorb` is the internal lifecycle operation that writes wiki knowledge from bounded context. User-facing help should not make users understand Absorb before using capture or ingest.

The concrete cleanup is to make command help and docs use user-facing verbs, while keeping `absorb` in operation metadata, prompts, and run records where it describes the actual runtime operation.

## Error Decision

`OperationError` is too narrow for the whole CLI. The standard shape should be a root `UserFacingError` with:

- `outcome`: `error` or `needs-action`
- `message`: one user-facing sentence
- `fix`: required for `needs-action`
- `data`: optional structured metadata for JSON output

`OperationError` remains as a lifecycle-specific subclass. Command adapters render `UserFacingError` through the same `renderOutcome()` path as normal command results.

## Implementation Targets

- Add root `UserFacingError`.
- Teach CLI rendering and the process-level catch block to render it.
- Make wiki resolution failures structured, especially missing `.almanac/`.
- Use the shared renderer in operation commands.
- Rename ingest input source types from generic `Source` to `IngestSource` so they do not collide conceptually with wiki evidence `sources:`.
- Refresh lifecycle command descriptions and public guide wording so `Absorb` reads as an internal operation, not a prerequisite concept.
