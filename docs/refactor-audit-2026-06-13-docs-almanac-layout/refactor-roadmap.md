# Refactor Roadmap

## Must Do Before Removing Legacy Support

1. Add a dedicated migration command for `.almanac/pages` and
   `.almanac/topics.yaml` into `docs/almanac/`.
2. Share page discovery and slug planning between indexer, health, snapshots,
   and build counting.
3. Rename `findNearestAlmanacDir()` to a root-focused name.
4. Update missing-wiki error messages to mention both `.almanac/` runtime state
   and `docs/almanac/` tracked content.

## Should Do Soon

1. Introduce a `WikiWorkspace` or `WikiLayout` object.
2. Rename topic helper APIs by intent:
   - `topicFilesForIndexing()`
   - `topicFileForMutation()`
3. Add a canonical viewer route for the wiki front door and keep
   `/getting-started` as an alias.
4. Add tests for docs-only query command behavior from nested directories, not
   only root detection and auto-registration.

## Can Wait

1. Full semantic migration of legacy CodeAlmanac pages into `docs/almanac/`.
2. Viewer navigation redesign around section READMEs and hubs.
3. Richer source typing for local cross-repo manual sources.

## Do Not Do

1. Do not make SQLite the source of truth for topics.
2. Do not keep `.almanac/pages` as a permanent parallel authoring surface.
3. Do not add a heavy orchestration workflow for wiki writing; the prompt/manual
   doctrine is the right control surface.
