# Smells And Findings

Date: 2026-06-09

## Finding 1: The Wiki Is Mechanically Healthy But Editorially Undergardened

Classification: Redesign

Evidence:

- `almanac health` reports zero orphans, stale pages, dead refs, broken links, broken cross-wiki links, missing sources, duplicate sources, empty topics, empty pages, and slug collisions.
- The same health run reports 347 unused sources, 29 legacy-frontmatter pages, and 135 ambiguous legacy source targets.
- `wiki-organization-primitives` already states that pages, links, and topics are enough for storage but not enough for coherence as capture volume grows.

Why it exists today:

The storage/indexing primitives landed before the editorial navigation model. Capture and Garden can create and update pages, but hubs, anchors, split/merge decisions, and redirect behavior remain mostly prompt conventions.

Architectural cost:

Agents can find pages by search, but they cannot reliably know which page is canonical, which page is a hub, and which page is historical without reading too much.

Recommendation:

Add hub pages and stronger garden rules before adding new frontmatter schema. Treat this as an information architecture rewrite, not a database rewrite.

Confidence: High

## Finding 2: Source Provenance Is The Highest-Risk Quality Failure

Classification: Simplify

Evidence:

- Health found 347 unused source IDs.
- Approximate source/citation gaps include `almanac-serve` with 36 sources and 2 cited IDs, `capture-automation` with 41 sources and 7 cited IDs, `automation` with 31 sources and 1 cited ID, `provider-lifecycle-boundary` with 30 sources and no cited IDs, and `harness-providers` with 30 sources and 1 cited ID.
- Several pages still include legacy string source entries after structured source migration.

Why it exists today:

The migration converted source lists mechanically. Many page source lists still represent "files inspected" rather than "evidence for claims".

Why that reason is not good enough:

The product promise is cited project memory. A source list that the prose does not cite is weaker than no source list because it looks authoritative while hiding which source supports which claim.

Architectural cost:

Garden and health will keep reporting noise. Future agents may trust claims because a page has many sources even when those sources are unrelated or historical.

Recommendation:

Run a source-hygiene garden pass before broad page rewrites. For each high-gap page, either cite the relevant source next to the claim or delete the source entry. Prefer code, tests, prompts, plans, commits, and current web docs for current claims. Keep local transcripts only for rationale or historical context.

Confidence: High

## Finding 3: Capture-To-Sync Vocabulary Drift Is Now Encoded In Slugs

Classification: Redesign

Evidence:

- `capture-automation.md` has title "Sync Automation".
- `capture-flow.md` has title "Sync Flow".
- `capture-ledger.md` has title "Sync Ledger".
- `sessionend-hook` is archived and superseded by `capture-automation`.
- The current public command surface appears to have moved toward `almanac sync`.

Why it exists today:

The product renamed the automatic session-memory coordinator from capture sweep to sync, but the existing page slugs were kept.

Architectural cost:

Slugs teach future agents vocabulary. If titles and slugs disagree, agents search both words, copy old terms into new work, and may reintroduce dead command names.

Recommendation:

Create an explicit rename plan. Preferred: rename current pages to `sync-automation`, `sync-flow`, and `sync-ledger`, then leave archived redirect/lineage pages for `capture-*` slugs once redirect behavior exists. If redirect behavior does not exist yet, keep the old slugs temporarily but add a sync hub that explains the vocabulary transition.

Confidence: High

## Finding 4: Several Pages Are Acting As Hubs And Deep Dives At The Same Time

Classification: Split

Evidence:

- `github-native-wiki-maintenance` is 831 lines and covers product loop, trigger policy, PR UX, hosted runtime, source tools, permissions, check-run actions, MVP validation, and deployment concerns.
- `capture-automation` is 726 lines and covers sync contract, hooks, scheduler, migration cleanup, activation baseline, incidents, implementation caveats, and source provenance.
- `almanac-product-family` is 320 lines and covers general product model, local/team modes, GUI loop, CLI loop, directory shape, and review wedge.

Why it exists today:

Garden and Absorb kept updating the page that was closest to the subject instead of splitting once subtopics became independently useful.

Architectural cost:

Future agents must read hundreds of lines to answer a narrow question. Page-local citations and links become harder to maintain. Hubs cannot route because they are buried inside the deep dive.

Recommendation:

Split by reader task:

- hub or overview: reading order and current canonical pages
- contract/reference: current behavior and interfaces
- decision: rationale, alternatives, consequences
- failure mode or incident: what broke and how to avoid it
- product strategy: what market/product conclusion affects implementation

Confidence: High

## Finding 5: Product Strategy Belongs, But The Shelf Needs A Gate

Classification: Simplify

Evidence:

- `.almanac/README.md` explicitly allows product and market conclusions that shape how CodeAlmanac is built, positioned, priced, or trusted.
- Product-positioning has 18 pages, competitive-research has 11, and fundraising has 1.
- Pages such as `company-brain`, `dosu`, `moxie-docs`, and `github-native-wiki-maintenance` contain concrete product implications.

Why it exists today:

CodeAlmanac is young enough that product positioning directly affects architecture: hosted versus local, GitHub-native workflows, source connectors, review surfaces, and trust model.

Why that reason can decay:

If every useful market note enters `.almanac`, engineering retrieval gets polluted by pages that do not change code, prompts, packaging, command design, or trust boundaries.

Recommendation:

Keep product pages only when their lead states the affected implementation/product decision. Move broad fundraising, pitch, or market notes to `docs/strategy/` unless they are actively shaping code or repo wiki behavior. Add a product strategy hub that separates "current product truth" from "competitor references".

Confidence: Medium-high

## Finding 6: External References Are Not Clearly Marked As External

Classification: Redesign

Evidence:

- `documenting-software-architectures` is tagged `decisions`, `agents`, `wiki-design`, and `prompt-system`.
- `farzapedia` is tagged `agents`, `decisions`, and `prompt-system`.
- `mem0`, `codex-supermemory`, and `agentmemory-competitor` are competitor or reference pages.

Why it exists today:

The wiki correctly captures external ideas that shaped CodeAlmanac. The topic system lacks a clear "external reference" shelf distinct from current architecture.

Architectural cost:

An agent searching `agents` may get a mix of current provider code, prompt contracts, competitor notes, and writing-system influences. That is too much semantic load for one topic.

Recommendation:

Add either an `external-references` topic or a hub that marks these pages as external inputs. Keep `competitive-research` for market competitors. Keep `stack` for dependencies. Use page leads to say "this is not current implementation; it shaped X".

Confidence: Medium

## Finding 7: Decision Pages Do Not Consistently Carry Decision Shape

Classification: Simplify

Evidence:

- The `decisions` topic has 13 pages.
- Some decision pages, such as `source-provenance`, clearly state product contract, transition contract, and settled boundaries.
- Others read more like subsystem explanations or external reference synthesis without explicit options, rejected alternatives, consequences, or confirmation.

Why it exists today:

The wiki uses topics as loose neighborhoods rather than page-type schema. That is mostly correct, but the decision topic still needs readable decision structure.

Recommendation:

Do not introduce numbered ADR folders. Borrow MADR-style sections only when a page's main job is a decision: context/problem, considered options, outcome, consequences, confirmation/current check. Add this to `.almanac/README.md` as a page-shape convention.

Confidence: Medium

## Finding 8: `global-agent-instructions` Is Nearly Stranded

Classification: Simplify

Evidence:

- The YAML inventory found `global-agent-instructions` has 11 links, all file links, and no page-to-page links.
- It is active and tagged `agents`, `cli`, and `flows`.

Why it matters:

The page may be useful for file-aware retrieval, but wiki graph navigation cannot route a reader from that page to related conceptual pages.

Recommendation:

Add links from its related pages or fold it into an agent-instructions neighborhood. At minimum link it to `agents-md`, `lifecycle-cli`, `almanac-doctor`, and `install-time-node-launcher` where relevant.

Confidence: High

## Finding 9: The Wiki Has No Canonical Front Door

Classification: Add

Evidence:

- The active page corpus does not include `.almanac/pages/getting-started.md`.
- The corpus has several dense neighborhoods: sync, wiki design, lifecycle operations, provider harness, source provenance, GitHub-native product work, and competitive research.
- Viewer and prompt assumptions already point toward a first-entry page or getting-started surface.

Why it exists today:

Search and topics were enough while the corpus was smaller. Hubs and first-entry routing became necessary only after capture and Garden accumulated enough high-value pages.

Architectural cost:

New agents must infer the first reading path from `almanac search`, topic names, or file names. That makes onboarding dependent on agent luck and can route code work through product or competitor pages before current architecture pages.

Recommendation:

Create `getting-started` as a normal wiki page, not a special schema type. It should point to the main hubs, explain that topics are browse neighborhoods, identify current terminology such as sync versus capture, and state where product and external-reference pages fit.

Confidence: High

## Finding 10: The Topic DAG Mixes Inheritance With Orthogonal Classification

Classification: Redesign

Evidence:

- `agents` contains provider/runtime pages, prompt pages, competitor pages, external references, and wiki-theory pages.
- `documenting-software-architectures` is tagged with current-system topics even though it is mainly an external architecture-documentation reference.
- `competitive-research` and `product-positioning` are useful shelves but can appear in the same retrieval paths as implementation architecture.

Why it exists today:

The DAG is flexible, and adding another broad topic to a relevant page is cheap. Over time, flexible tagging substituted for explicit routing.

Architectural cost:

Search by topic can answer "what mentions this concept" but not "what should I read before changing code in this area." Topic count looks healthy while reader intent stays ambiguous.

Recommendation:

Keep the DAG, but re-scope roots around neighborhoods and add hubs for reading paths. Treat `decisions`, `flows`, `constraints`, `failure-modes`, and `reference` as overlays or page-shape conventions rather than pretending they are the same kind of category as `storage` or `provider-harness`.

Confidence: High

## Finding 11: `status` And `verified` Behave Like Undocumented Schema

Classification: Simplify

Evidence:

- The sidecar inventory found 47 pages with `verified` and 5 without it.
- The same inventory found 32 pages with `status` and 20 without it.
- The README explains topics, links, and sources, but does not define operational semantics for these fields.

Why it exists today:

Frontmatter fields were useful during page creation and review, but they have not become durable query contracts.

Architectural cost:

Optional metadata that looks official teaches agents to trust a field whose meaning is unclear. A page with `verified: true` can still carry stale source lists; a page without `verified` may still be accurate.

Recommendation:

Either define these fields in `.almanac/README.md` and make health/query behavior depend on them, or remove them from pages where they are only editorial residue. Do not let them become pseudo-schema by accident.

Confidence: Medium-high

## Finding 12: Public Guidance Still Teaches The Old Provenance Model

Classification: Fix

Evidence:

- The AGENTS/imported guide still says frontmatter carries `topics:` and `files:` and calls `files:` load-bearing for `almanac search --mentions`.
- The current wiki and source-provenance direction have moved toward structured `sources:` as the canonical evidence model.
- The sidecar inventory found legacy string sources and one legacy `files:` page entry.

Why it exists today:

The implementation and wiki model moved faster than the global guidance copied into agent instructions.

Architectural cost:

Agents following old guidance may create new pages with legacy provenance, causing Garden and health to keep fighting the same migration.

Recommendation:

After the garden rewrite decides the exact source contract, update `.almanac/README.md` and any exported agent guidance so new pages use `sources:` consistently and `files:` is described only as legacy or compatibility behavior if it still exists.

Confidence: High
