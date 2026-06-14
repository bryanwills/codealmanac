# Docs Almanac Decision Log

Date: 2026-06-13

## 1. Canonical Wiki Content Moves To `docs/almanac/`

Readable wiki pages now belong under `docs/almanac/`. `.almanac/` stays as the
runtime directory for generated local state such as `index.db`, jobs, runs, and
other process artifacts.

Why: the wiki is meant to be read by humans and agents. Putting durable prose
under `docs/` makes it visible in the normal documentation surface instead of
hiding it beside runtime state.

## 2. Canonical Content Is Not Mixed With Runtime State

The indexer reads page source only from `docs/almanac/`. `.almanac/` is runtime
state and is not a second authoring tree.

Why: mixed content roots make every command encode layout policy and create a
permanent compatibility burden. The clean model is easier for humans, agents,
tests, and docs tooling to reason about.

## 3. Nested Pages Use `page_id`

`page_id` in frontmatter can define the stable page slug. This lets sections use
normal docs names like `README.md` without losing stable wiki identities.

Why: folder structure should serve readability. Slugs should remain stable even
when a page moves from `architecture.md` to `architecture/README.md`.

## 4. Topics Remain YAML

`docs/almanac/topics.yaml` is the canonical topic file.

Why: topics are source-controlled organization data. SQLite remains the derived
query index, not the authoring source.

## 5. Scaffold Seeds Structure, Not A Finished Wiki

`almanac init` creates `docs/almanac/README.md`, `topics.yaml`, `_manual/`, and
`_meta/`. It does not attempt to generate subsystem pages.

Why: the scaffold should teach the shape and give agents a contract. Full
coverage requires repo-specific reading and should come from build/garden/capture
runs, not static boilerplate.

## 6. `README.md` Is The Front Door

The canonical orientation page is `docs/almanac/README.md`. Build should not
create `getting-started.md` or `project-overview.md` as a second front door.

Why: this matches normal documentation repositories and keeps the browse tree
obvious to humans.

## 7. The Manual Lives Inside The Wiki

The durable writing guidance lives under `docs/almanac/_manual/`, with local
maintenance conventions under `docs/almanac/_meta/`.

Why: agents and humans should read the same guidance in the same documentation
surface. Prompt changes define agent behavior; the manual makes the behavior
auditable and editable.

## 8. Section READMEs Are Orientation, Not Migration

The initial `concepts/`, `architecture/`, `guides/`, `reference/`,
`decisions/`, `incidents/`, `active/`, and `context/` pages explain what belongs
in each section. They do not claim the old corpus has been semantically
migrated.

Why: the structure should be visible now, while full migration remains a
separate content-quality task.

## 9. Repo Detection Uses The Canonical Docs Directory

A repo is an Almanac wiki when it has `docs/almanac/`.

Why: an initialized wiki may be empty before build writes pages, and a clean
clone must still be discoverable from subfolders. Runtime state alone is not a
wiki marker.

## 10. Topic Commands Write The Canonical Topic File

Topic mutation commands write `docs/almanac/topics.yaml`.

Why: one source of truth is simpler than keeping a compatibility target alive.
Repos that need old data moved should run an explicit one-time migration before
using current commands.

## 11. Health Uses `page_id` For Collision Checks

`almanac health` checks slug collisions across all wiki content roots and uses
`page_id` before filenames.

Why: nested docs pages often use `README.md`; collision detection must match the
same page identity model as the indexer.

## 12. Viewer Front Door Means README

The viewer treats the canonical front door as the README-backed page.

Why: Build no longer creates a second orientation page. One front door keeps the
viewer and docs tree aligned.

## 13. `sources:` Is Canonical Provenance

Page frontmatter uses `sources:` for authored provenance. `type: file` source
entries and inline file/folder wikilinks derive `file_refs` for `--mentions`,
`show --files`, and dead-reference health checks. There is no separate authored
`files:` field.

Why: two authored fields for the same page-to-code relationship can disagree.
One canonical provenance field keeps citation evidence and file mention indexing
aligned.
