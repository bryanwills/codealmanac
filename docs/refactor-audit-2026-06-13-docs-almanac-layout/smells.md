# Smells

## 1. Wiki Layout Is Still A Helper Set, Not A Boundary

**Classification:** Redesign.

The new `src/wiki/locations.ts` is useful, but callers still combine helpers
manually. Root detection, topic mutation, indexing, snapshots, health, setup,
and viewer each make small local choices about what "the wiki" means.

This is better than hard-coded paths, but it is not yet an architecture. A
future migration step could easily update one helper path and miss a semantic
choice such as "canonical topics shadow legacy topics" or "legacy-only repos
keep legacy topic writes."

Recommendation: introduce a `WikiWorkspace` or `WikiLayout` boundary that
answers higher-level questions:

- Which content roots are readable?
- Which content root is canonical for new pages?
- Which topics file should be read?
- Which topics file should be mutated?
- Which runtime paths should be created?
- Is this repo legacy-only, canonical, or mixed migration state?

## 2. The Name `findNearestAlmanacDir` Is Now False

**Classification:** Simplify.

`findNearestAlmanacDir()` now finds a repo with `.almanac/` or
`docs/almanac/`, not just an Almanac directory. The old name will keep teaching
new callers the wrong mental model.

Recommendation: rename it to `findNearestWikiRoot()` or
`findNearestAlmanacRoot()` in a follow-up. Keep a temporary compatibility export
only if necessary.

## 3. Legacy Compatibility Is Scattered

**Classification:** Simplify.

Legacy support appears in indexer root precedence, topic write-path selection,
viewer front-door fallback, setup page counts, health collision detection, and
prompt language. Each piece is reasonable, but the migration state is implicit.

Recommendation: make migration state explicit in the layout boundary:
`legacy-only`, `canonical-only`, or `mixed`. Then callers can switch on a shared
state instead of re-deriving compatibility locally.

## 4. Health Duplicates Indexer Page Discovery

**Classification:** Redesign.

`src/wiki/health/index.ts` now repeats enough of indexer page discovery to
detect collisions with `page_id`. That fixes correctness, but it creates a
second slug-planning implementation.

Recommendation: extract an indexer page-discovery function that returns planned
page identities, display paths, skipped files, and collisions. The indexer and
health should share it.

## 5. Topics Have Two Different Resolution Semantics

**Classification:** Redesign.

Indexing uses "canonical topics if canonical exists, otherwise legacy." Topic
commands use "canonical topics if actual canonical file exists; otherwise
legacy if legacy exists; otherwise choose by docs root." These are intentionally
different, but the distinction is buried in helper names.

Recommendation: name the two APIs by intent:

- `topicFilesForIndexing()`
- `topicFileForMutation()`

Then tests can pin the difference without relying on comments.

## 6. Viewer Route Names Preserve Old Product Language

**Classification:** Simplify.

The viewer still uses `/getting-started` as the route to show the front door.
The route works and is compatible, but the product language is now README/front
door.

Recommendation: add a canonical `/start` or `/front-door` route later, keep
`/getting-started` as a redirect/fallback, and update tests to prefer the new
route.

## 7. Error Messages Still Mention Only `.almanac/`

**Classification:** Simplify.

Several user-facing errors still say "no .almanac/ found" even though
`docs/almanac/` is now a valid wiki marker. The behavior is mostly correct
after root-detection fixes, but the language is stale.

Recommendation: change missing-wiki messages to "no Almanac wiki found" and
include both accepted markers in the fix text.
