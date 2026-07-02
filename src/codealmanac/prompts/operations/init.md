# Init Operation

You are building the first substantial CodeAlmanac wiki for this repository.

The base prompt modules define the wiki purpose, notability rules, page
structure, and writing syntax. Follow them.

Your job is to perform a deep first construction pass. Create a reusable
project memory layer, not a stub wiki and not a file-tree summary.

## Required Navigation Page

Always create `pages/getting-started.md` under the configured Almanac root as
the canonical front door to the wiki. This page is for navigation through the
wiki, not repository setup or install instructions.

Write it after the initial graph is mostly known so it can route through the
actual pages you created. It should help a future reader avoid overwhelm by
explaining where to start, which pages to read first, which dense clusters
matter, and what to read next for common work areas. Link directly to the most
important pages and local hubs with `[[...]]`.

Use `getting-started.md` for the required orientation role. Do not create a
second front-door page such as `project-overview.md`.

## Tooling Boundary

Init creates a local CodeAlmanac wiki from the current filesystem. Do not use
MCP tools, remote wiki search, hosted Almanac APIs, or external page search
tools for this operation.

Use filesystem reads, shell/search commands, and direct writes under the
configured Almanac root. The wiki may start empty, so an unavailable or empty
local wiki search is not a blocker and is not evidence that the wiki cannot be
updated.

## Algorithm

1. Orient to the corpus: repo layout, commands, package/config files, docs,
   entrypoints, generated outputs, tests, schemas, data files, and external
   dependencies.
2. Build a working map of the repo from multiple angles: entities, subsystems,
   flows, contracts, data models, operations, external systems, product
   concepts, and dense clusters.
3. Investigate important areas deeply enough to explain how they work and how
   they connect. Tests are often the clearest source of intended behavior.
4. Compare code against existing docs and research. Do not copy docs; preserve
   applied conclusions and project-specific meaning.
5. Identify page candidates by future value. Ask whether each page preserves
   understanding that would be costly, useful, or risky to reconstruct later.
6. Design the initial graph: pages, topics, links, and any local hubs.
7. Write detailed, grounded pages directly under `pages/` inside the configured
   Almanac root.
8. Use structured `sources:` frontmatter for evidence. Do not emit legacy
   `files:` on new pages.
9. Re-read the wiki as a future agent. Fix weak leads, duplicate pages,
   unsupported claims, missing links, topic noise, and thin placeholders.

Be thorough. Create many pages when many pages are justified. Do not stay tiny
to be safe. The quality gate is not page count; it is whether each page earns
its place in the project graph.

## Helper Agents

If the provider supports helper agents and the repo is broad enough, use them
for bounded investigation or draft fragments. Good helper tasks include
investigating one subsystem, tracing one flow, reading tests for one area,
checking an external dependency, or identifying page candidates for one
cluster.

The main agent owns final synthesis, page boundaries, topics, links, hubs, and
final prose. Helper output is evidence, not completion.

Do not end with page candidates, pages to add later, or an investigation
report. After helpers return, synthesize their findings into actual markdown
pages now.

## Output Standard

The output is a coherent wiki under the configured Almanac root. It should let
a future agent form a working model of the project faster than by starting from
raw files.
