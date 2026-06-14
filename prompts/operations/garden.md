# Garden Operation

You are improving an existing Almanac wiki as a whole graph.

The base prompt modules define the wiki purpose, page-selection rules, folder
structure, and writing syntax. Follow them.

Garden is cultivation. The goal is not activity; the goal is a wiki that is
more coherent, readable, current, and trustworthy.

## Algorithm

1. Inspect pages, folders, topics, links, hubs, referenced files, and cited
   sources where useful.
2. Find graph problems: duplicate pages, thin placeholders, stale claims,
   missing anchors, missing links, bloated pages, confusing folders, noisy
   topics, broken references, unsupported claims, and old active notes.
3. Prefer synthesis over logs. Fold date-stamped fragments into evolving pages
   when chronology is not itself important.
4. Merge overlapping pages. Split pages whose title can no longer describe the
   subject cleanly. Preserve useful history in the surviving page.
5. Move pages to the folder where a new maintainer would expect to browse them.
6. Improve topic neighborhoods after folder placement is clear.
7. Create or revise hubs when a dense cluster needs reading order and
   interpretation.
8. Re-read edited areas as a new maintainer. Verify that leads, links,
   frontmatter, citations, folders, and page boundaries make the wiki easier to
   use.

You may create, update, rewrite, move, merge, split, archive by prose, retopic,
relink, or create hub/index pages when that improves the wiki. No-op is valid if
the wiki is already coherent enough for the current pass.

Do not churn the wiki just to show activity. Do not rewrite unrelated pages for
style. Make broad changes only when the graph shape justifies them.

## Helper Agents

If the provider supports helper/subagents and the wiki is broad enough, use
them for bounded audits: duplicate detection, stale reference checks, folder
review, topic cluster review, hub candidates, source grounding, or one dense
area of the graph.

The main agent owns final synthesis, page boundaries, folders, topics, links,
hubs, and final prose.

## Output Standard

The output is a more coherent `docs/almanac/` wiki. Every edit should make the
project memory easier for a human maintainer or future coding agent to
understand, navigate, or trust.
