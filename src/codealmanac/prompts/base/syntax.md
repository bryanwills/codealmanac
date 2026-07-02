# Page Syntax And Writing Conventions

Pages are Markdown files under `pages/` inside the configured Almanac root.
Use kebab-case slugs. The filename is the stable page identity.

Use natural names when possible: `stripe.md`, `postgres.md`,
`claude-agent-sdk.md`, `agent-tools-market.md`, or `pricing-sensitivity.md`
are better than genre-prefixed names when the subject itself is clear.

## Frontmatter

Use YAML frontmatter when it helps indexing and future agents.

Common fields:

```yaml
---
title: Human Readable Title
summary: One direct sentence explaining what this page helps future agents understand.
topics: [topic-one, topic-two]
sources:
  - id: implementation-file
    type: file
    path: src/path/to/file.py
    note: Supports the page's code claims.
  - id: external-docs
    type: web
    url: https://example.com/docs
    retrieved_at: 2026-07-02
    note: Supports the external dependency claims.
status: active
verified: 2026-07-02
external_version: "api-or-doc-version-if-relevant"
---
```

Use `summary:` as the page's search-result snippet: one factual sentence, not
a paragraph. It should explain what the page is about and why an agent would
open it.

Use structured `sources:` for evidence. Use `type: file` for repo files, tests,
prompts, migrations, and config; `type: pr` for pull requests; `type: issue`
for GitHub issues or equivalent issue-tracker items; and `type: web` for
external URLs. Use other source types for transcripts, notes, market reads,
research inputs, commits, or other material that supports the page.

Every source needs a stable `id` and a `note` explaining what the source
supports. Cite non-obvious claims with `[@source-id]`. Do not cite a source you
did not inspect.

Do not emit legacy `files:` on new pages. Do not add fields mechanically.
Frontmatter should make the page more retrievable, grounded, or maintainable.

## Wikilinks

Use one `[[...]]` syntax:

- `[[page-slug]]` links to another wiki page.
- `[[src/indexer/schema.py]]` references a repo file.
- `[[src/indexer/]]` references a repo folder.

Do not create new cross-wiki links. If old pages contain cross-wiki links, do
not expand that pattern.

Page wikilinks must resolve. Link only to existing page slugs or pages you
create or update in this run. If no page exists and you are not creating it,
write the name as plain text instead of leaving a broken `[[...]]` link.

Link the first meaningful mention of a related page in a section. Do not link
every repeated word. A page with no inbound or outbound links is suspect.

## Grounding

Ground non-obvious claims in code, tests, docs, sources, commits, prior wiki
pages, or explicit user-provided context.

Code is current truth for present-tense runtime behavior. Conversations, old
pull requests, old commits, and incident notes are historical evidence unless
the claim is verified against current code, tests, config, or current external
docs.

Do not pretend uncertainty is fact. If a claim matters and cannot be grounded,
either omit it or mark it as an open question.

For external docs or research, cite the source and preserve the conclusion that
matters to this project. Do not copy long external passages into the wiki.

## Page Shape

Start with a lead. The lead should stand alone: a future agent should know what
the page is about, why it exists, and whether to keep reading.

After the lead, use sections based on the page's job. Common sections include:

- What it is in this project
- Where it lives
- How it works
- What we use
- What we do not use
- Contracts and assumptions
- Related flows
- Current synthesis
- Open questions
- Verification
- Related pages

Use prose for explanation. Use bullets for real lists. Use tables only for
structured comparison.

## Style And Scope

Be direct, factual, and dense. Write for future coding agents.

Avoid generic tutorials, vague claims, marketing prose, unsupported rationale,
transcript language, file summaries, and conclusions that do not connect to
future work.

Update only files inside the configured Almanac root unless the operation
explicitly says otherwise. Do not edit application code during lifecycle wiki
operations.
