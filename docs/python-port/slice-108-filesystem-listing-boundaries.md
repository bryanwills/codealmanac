# Slice 108 - Filesystem Listing Boundaries

## Scope

Split filesystem directory listing internals while preserving
`FilesystemSourceRuntimeAdapter` behavior.

## Why Now

After slice 107, `integrations/sources/filesystem/listing.py` is the largest
production module. It owns directory document assembly, default ignore rules,
configured root ignore handling, `.gitignore` loading, Python directory walking,
Git `ls-files` integration, Git status parsing, Git repo-root probing, and
subprocess failure tolerance.

Cosmic Python chapter 04 separates orchestration from interfacing code, and
chapter 13 keeps concrete dependency wiring explicit. Applied here:
`listing.py` should assemble the directory document and choose Git-vs-walk
source policy, while Git command mechanics, ignore specs, and filesystem walks
live in named modules.

## In Scope

- Move ignore defaults and `.gitignore` handling to
  `integrations/sources/filesystem/ignore.py`.
- Move Python directory walking to `walk.py`.
- Move Git directory listing, status parsing, repo-root probing, and Git command
  tolerance to `git.py`.
- Keep `listing.py` as the directory document assembly facade.
- Add an architecture guard that keeps Git command/status parsing, `pathspec`,
  and recursive walking out of `listing.py`.

## Out of Scope

- Source selection policy changes.
- New ignore patterns.
- New source kinds or candidate concepts.
- Changes to rendered filesystem runtime text.

## Verification

- Focused filesystem runtime tests.
- Focused directory selection tests.
- Architecture guard for filesystem listing boundaries.
- Service-level filesystem directory runtime dogfood.
- Full pytest, Ruff, and diff hygiene.
