# Docs Almanac Decision Log

Date: 2026-06-13

## 1. Canonical Wiki Content Moves To `docs/almanac/`

Readable wiki pages now belong under `docs/almanac/`. `.almanac/` stays as the
runtime directory for generated local state such as `index.db`, jobs, runs, and
review queues.

Why: the wiki is meant to be read by humans and agents. Putting durable prose
under `docs/` makes it visible in the normal documentation surface instead of
hiding it beside runtime state.

## 2. Legacy Pages Stay Indexed During Migration

The indexer reads `docs/almanac/` first and `.almanac/pages/` second. If both
roots contain the same page slug, the docs page wins and the legacy page is
skipped with a warning.

Why: existing repos should not lose query coverage while migrating. The new
layout still needs a clear precedence rule so stale legacy pages cannot override
new docs.

## 3. Nested Pages Use `page_id`

`page_id` in frontmatter can define the stable page slug. This lets sections use
normal docs names like `README.md` without losing stable wiki identities.

Why: folder structure should serve readability. Slugs should remain stable even
when a page moves from `architecture.md` to `architecture/README.md`.

## 4. Topics Remain YAML

`docs/almanac/topics.yaml` is the canonical topic file when present. Legacy
`.almanac/topics.yaml` is used only when the canonical file does not exist.

Why: topics are source-controlled organization data. SQLite remains the derived
query index, not the authoring source.

## 5. Scaffold Seeds Structure, Not A Finished Wiki

`almanac init` creates `docs/almanac/README.md`, `topics.yaml`, `_manual/`, and
`_meta/`. It does not attempt to generate subsystem pages.

Why: the scaffold should teach the shape and give agents a contract. Full
coverage requires repo-specific reading and should come from build/garden/capture
runs, not static boilerplate.
