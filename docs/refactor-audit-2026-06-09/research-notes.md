# Research Notes

Date: 2026-06-09

This audit used outside documentation patterns as lenses. None should be copied wholesale into `.almanac`.

## Diataxis

Source: https://diataxis.fr/

Relevant point:

Diataxis organizes documentation around four reader needs: tutorials, how-to guides, reference, and explanation. It is explicitly about content, architecture, and form emerging from user needs.

Application to `.almanac`:

Use Diataxis to ask what a page is doing for the reader. Do not create top-level topics or folders named tutorials/how-to/reference/explanation. CodeAlmanac's primary reader is a coding agent acting on a repo, so the useful translation is:

- how-to: workflow pages for commands and changes
- reference: contracts, schemas, flags, invariants
- explanation: decisions, rationale, failure modes
- tutorial: starting hubs and first-read routes

Recommendation:

Borrow the reader-purpose lens. Reject rigid Diataxis storage.

## Write the Docs / Docs as Code

Source: https://www.writethedocs.org/guide/docs-as-code/

Relevant point:

Docs as Code means writing documentation with development tools: issue trackers, Git, plain text markup, code reviews, and automated tests. It integrates documentation into product-team workflow.

Application to `.almanac`:

This strongly supports repo-owned markdown, Git review, and health checks. It also supports the product choice that `.almanac` changes should be reviewed as code-adjacent project memory, not silently hidden in a hosted graph.

Recommendation:

Keep markdown in-repo. Improve review ergonomics by reducing source noise and adding hubs so reviewers can understand why a wiki diff matters.

## SEI Views And Beyond / ISO 42010

Sources:

- https://www.sei.cmu.edu/library/views-and-beyond-the-sei-approach-for-architecture-documentation/
- https://www.iso-architecture.org/ieee-1471/cm/

Relevant point:

Views and Beyond centers architecture documentation on views. ISO 42010 frames views as addressing stakeholder concerns through viewpoints.

Application to `.almanac`:

This supports the user's preference for explicit architecture documentation primitives: module view, runtime view, allocation view, rationale, glossary, roadmap, and release/config management. But CodeAlmanac should express those as page neighborhoods and hub routes, not as frontmatter types.

Recommendation:

For major subsystems, the hub should answer:

- What parts exist?
- How do they run?
- Where do they live?
- Why were the key choices made?
- What must future changes preserve?

That is the right "views and beyond" adaptation for an agent-first wiki.

## C4 Model

Source: https://c4model.com/diagrams

Relevant point:

C4 uses zoom levels for static structure: system context, containers, components, and code. Its own guidance says teams do not need all levels, only those that add value.

Application to `.almanac`:

Use C4 as a zoom discipline for architecture hubs. A subsystem hub can link to:

- context: why this subsystem exists and what external systems it touches
- container/module: which repo modules own which responsibilities
- component: important internal contracts
- dynamic/deployment support: runtime flows and state placement

Recommendation:

Borrow zoom levels and diagram discipline. Do not make C4 a page taxonomy.

## arc42

Source: https://arc42.org/

Relevant point:

arc42 is a pragmatic template for software architecture documentation and communication. It is process-agnostic and meant for architecture decisions, constraints, building-block views, runtime views, deployment views, risks, and glossary-style shared understanding.

Application to `.almanac`:

arc42 confirms that architecture documentation needs coverage beyond prose essays: context, constraints, building blocks, runtime behavior, deployment/allocation, decisions, quality concerns, risks, and glossary terms.

Recommendation:

Use arc42 as a completeness checklist for important hubs. Do not copy the template as `.almanac` folder structure.

## MADR / ADRs

Source: https://adr.github.io/madr/

Relevant point:

MADR records architecturally significant decisions in Markdown with context/problem, considered options, outcome, consequences, and confirmation. It also recognizes that large projects may need categories.

Application to `.almanac`:

Decision pages should borrow this shape when the page's main job is a decision. The wiki should not become a numbered ADR log because it also stores flows, contracts, failure modes, external references, and product strategy.

Recommendation:

Add decision-page guidance to `.almanac/README.md`: context, options, decision, consequences, current confirmation, related pages. Keep topics and wikilinks as the organization mechanism.

## Pattern Synthesis

The prior art agrees on one thing: documentation needs reader-oriented structure. The current `.almanac` corpus has strong storage primitives but weak reader routing. The target is not "adopt framework X"; it is "make the graph navigable by concern".

Recommended adapted pattern:

```text
hub page
  -> current architecture anchor
  -> runtime flow page
  -> source/allocation page
  -> decision/rationale pages
  -> constraints/failure modes
  -> workflow/how-to pages
  -> external references that shaped this area
```

This fits CodeAlmanac better than a docs-site tree because each page can still belong to multiple topics and be found by file-aware retrieval.
