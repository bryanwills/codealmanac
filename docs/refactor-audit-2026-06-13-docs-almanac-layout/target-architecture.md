# Target Architecture

## Desired Shape

The codebase should have one explicit wiki workspace boundary:

```text
WikiWorkspace
  repoRoot
  mode: legacy-only | canonical-only | mixed
  contentRootsForRead()
  canonicalContentRoot()
  topicFilesForIndexing()
  topicFileForMutation()
  runtimeDir()
  indexDbPath()
  reviewYamlPath()
  frontDoorPageIds()
```

This object should be cheap and deterministic. It should not open SQLite and it
should not invoke AI. It should only inspect filesystem markers and return
paths plus migration mode.

## What Would Move

- `src/paths.ts` keeps global path concerns and root walking, but returns a
  `repoRoot`.
- `src/wiki/locations.ts` becomes the workspace/layout module rather than a bag
  of helpers.
- `src/wiki/topics/paths.ts` either disappears or delegates to
  `WikiWorkspace.topicFileForMutation()`.
- `src/wiki/indexer/index.ts`, `src/wiki/health/index.ts`,
  `src/jobs/snapshots.ts`, `src/operations/build.ts`, `src/operations/garden.ts`,
  `src/viewer/api.ts`, and setup code stop making local layout decisions.

## Page Discovery

Create one page-discovery module used by indexer, health, snapshots, and build
counts:

```text
discoverWikiPages(workspace)
  -> roots
  -> candidates with parsed frontmatter
  -> canonical slug from page_id or filename
  -> display path
  -> collision groups
```

The indexer can then index planned pages, while health can report skipped or
colliding pages without duplicating slug logic.

## Migration State

Migration state should be explicit:

- `legacy-only`: `.almanac/pages` and maybe `.almanac/topics.yaml`; topic
  commands mutate legacy files.
- `canonical-only`: `docs/almanac`; topic commands mutate canonical files.
- `mixed`: both roots exist; canonical content and topics win, legacy pages stay
  readable until migrated.

Explicit state makes review and debugging easier than re-reading helper
conditions.
