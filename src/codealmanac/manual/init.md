---
title: Init
topics: [manual]
---

# Init

Init creates the first substantial wiki under the configured Almanac root for a
repo.

The goal is a usable project memory graph, not a file-tree summary and not only
a starter scaffold. A first-build run should create enough grounded pages that
a future agent can understand the repo faster from the wiki than by
rediscovering context from raw files.

Before writing substantive pages, read `manual/README.md`, `manual/pages.md`,
`manual/evidence.md`, `manual/style.md`, `manual/sources.md`, and the
repo-specific `README.md` under the configured Almanac root.

## Required Front Door

Create `pages/getting-started.md` as the canonical front door to the wiki.

`getting-started.md` is for navigation through the wiki. It is not repository
setup documentation. Write it after the graph is mostly known so it can point
to the actual pages and hubs created during the run.

## What To Build

Create pages for durable subjects that future agents will need again:

- major subsystems and service boundaries
- recurring flows and lifecycle operations
- command contracts and storage contracts
- provider, harness, prompt, and external service assumptions
- data models, schemas, indexes, and serialized files
- decisions, constraints, risks, incidents, and gotchas
- product, market, pricing, user, or team context that shapes work

Do not create pages whose only value is that a file or folder exists. Use code
and docs as evidence, not as prose to copy.

## Working Standard

Use filesystem reads, shell/search commands, and direct writes under the
configured Almanac root. The wiki may start empty, so an empty local wiki
search is expected.

Write structured `sources:` frontmatter for non-obvious claims. Link pages with
`[[page-slug]]` only when the target exists or is created in the same run.

Re-read the created wiki as a future agent. Fix weak leads, unsupported claims,
missing links, confusing topics, duplicate pages, and thin placeholders before
the run ends.
