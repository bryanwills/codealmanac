# Wiki Syntax

Pages are Markdown files under `pages/` inside the configured Almanac root,
with YAML frontmatter. Use kebab-case slugs and stable page titles.

Use `topics:` for topic slugs. Use structured `sources:` entries for evidence
that supports non-obvious claims. Use `[[...]]` wikilinks for pages, files,
folders, and cross-wiki references.

Page wikilinks must resolve. Link only to existing page slugs or pages you
create or update in this run. If no page exists and you are not creating it,
write the name as plain text instead of leaving a broken `[[...]]` link.

Every sentence should contain a specific fact. Prefer neutral prose. Do not
speculate. Do not add promotional language.

Update only files inside the configured Almanac root unless the operation
explicitly says otherwise. Do not edit application code during lifecycle wiki
operations.
