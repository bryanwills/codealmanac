# Page Notability And Graph Structure

Use these rules to decide what deserves a page, what deserves a topic, and how
clusters should form. They are judgment tools, not a closed schema.

## Page Existence

A page deserves to exist when it captures durable, reusable project
understanding that would be costly, useful, or risky to reconstruct later.

Good page candidates include:

- **Entity**: a named thing the project reasons about, such as a provider,
  schema, command, external service, framework, customer segment, or agent.
- **Subsystem**: an area with responsibility and boundaries.
- **Flow**: behavior that crosses files, commands, systems, providers, or
  agents.
- **Contract**: obligations between callers, providers, schemas, APIs,
  commands, file formats, prompts, or external services.
- **Data model**: records, schemas, storage formats, indexes, serialized files,
  or external payloads whose shape affects behavior.
- **Operation**: a recurring product or project action with inputs, outputs,
  side effects, and verification.
- **Decision or rationale**: why the project chose one path over plausible
  alternatives.
- **Risk or invariant**: a rule, coupling, assumption, or fragile behavior that
  future work must preserve.
- **Dependency**: an external runtime, service, SDK, API, framework, law,
  platform, or tool as used by this project.
- **Research synthesis**: conclusions from docs, papers, experiments, external
  references, or design exploration.
- **Market or product synthesis**: durable understanding about users,
  positioning, pricing, competitors, sentiment, or product strategy.
- **Incident or postmortem**: what happened, what was learned, and what
  changed.
- **Hub**: a navigational page that explains a dense cluster.

Genres are vocabulary, not enforcement. Create a different shape when the
material genuinely needs it.

## What Usually Does Not Deserve A Page

Avoid pages that are only:

- file-by-file summaries
- folder trees in prose
- raw transcripts
- copied external API documentation
- task progress logs
- roadmaps that belong in an issue tracker
- guesses about intent that the repo or sources do not support
- one-off facts obvious from one nearby file
- date-stamped notes with no synthesis value
- pages whose only claim is that something exists

If the useful part of an input can be folded into an existing synthesis page,
do that instead of creating a new page.

No-op is valid when the available material does not justify a durable wiki
change.

## Topics And Hubs

Topics are reading neighborhoods. A topic should help answer: what should an
agent read together?

Good topics name stable areas of meaning, such as `provider-harness`,
`prompt-system`, `wiki-indexing`, `product-positioning`, or `billing`.

Avoid bookkeeping topics such as `misc`, `notes`, `research`, exact filenames,
or dates by default. Prefer existing topics. Create a topic when several pages
now form a real cluster or a new cluster is clearly expected to grow.

A hub exists when search results are no longer enough to understand a cluster.
The hub should explain what the cluster is, which pages are core, what a new
agent should read first, how the pages relate, and what tensions or open
questions shape the area.
