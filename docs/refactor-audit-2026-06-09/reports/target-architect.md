# Target Architect Report: CodeAlmanac `.almanac`

Goal:
Critically audit `/Users/rohan/Desktop/Projects/codealmanac/.almanac` from a target-architect perspective to determine which wiki architecture, page neighborhoods, topic boundaries, page shapes, evidence practices, and gardening workflows should be preserved, simplified, removed, or redesigned.

Non-goals:
- Do not edit implementation code.
- Do not edit `.almanac/pages`.
- Do not treat the current wiki graph as justified merely because `almanac health` passes.
- Do not recommend page-type schema or folder machinery unless a concrete query or maintenance need exists.

## Evidence inspected

- `.almanac/README.md`
- `.almanac/topics.yaml`
- `.almanac/pages` inventory, metadata, approximate word counts, wikilinks, source counts, and backlink counts
- `almanac topics`, `almanac topics show ... --descendants`, `almanac health`, and selected `almanac show` outputs
- `MANUAL.md`
- `/Users/rohan/Desktop/Projects/openalmanac/docs/ideas/codebase-wiki.md`
- Selected current wiki pages: `wiki-organization-primitives`, `source-provenance`, `lifecycle-architecture`, `wiki-lifecycle-operations`, `capture-flow`, `capture-automation`, `process-manager-runs`, `almanac-product-family`, `github-native-wiki-maintenance`, `almanac-serve`, and `sessionend-hook`

## Executive diagnosis

The current wiki has strong raw primitives and weak editorial architecture.

The storage model is correct: flat pages, double-bracket links, topic DAG, file/source references, lineage metadata, implicit reindexing, local viewer, and Git-reviewed markdown. Do not replace that with folders, page-type frontmatter, or a separate docs tree as the source of truth.

The current graph is also not healthy in the sense that matters for future agents. It has 52 active markdown pages and 14 topics, but the topic DAG leaks across unrelated axes, long pages carry too many jobs, source lists are bloated and weakly cited, and several pages are product or competitor notes masquerading as architecture context. The wiki is mechanically linked but not yet shaped as an agent-first architecture memory system.

The most important target move is not a new schema. It is a gardening rewrite around canonical neighborhoods:

- front door
- architecture map
- lifecycle operations
- wiki model
- storage and retrieval
- provider runtime
- CLI and local operations
- product strategy
- prior art and competition

Each neighborhood needs an anchor or hub page that routes future agents. Leaf pages should explain one subject, contract, decision, flow, failure mode, or external reference. Pages that only exist because a session had material should be merged or deleted unless they still change how CodeAlmanac should be built.

## Current architecture map

The current `.almanac` model is:

```text
.almanac/
  README.md          repo-specific notability bar and writing conventions
  topics.yaml        topic DAG
  pages/             flat markdown page corpus
  index.db           derived local index
  jobs/              ignored job/runtime state in current implementation
```

The wiki README states the right product contract: write pages only for non-obvious knowledge that helps a future coding agent. It names decisions, failure modes, cross-file flows, constraints, subsystems, integrations, product conclusions, and distilled external references as notable. It also says the primary reader is an AI coding agent and the page style should be dense, factual, linked, and source-backed.

The codebase-wiki spec agrees with the same core: pages are atomic interlinked markdown, topics are a multi-parent DAG, `.almanac/README.md` carries conventions and the notability bar, `files:` or structured `sources:` power file-aware retrieval, and lineage metadata is reserved for fundamental reversals.

`MANUAL.md` adds the architectural standard this wiki should teach future agents: evolve the codebase so features fit, build seams early and machinery late, separate decisions from mechanisms, keep raw external shapes at boundaries, use structured contracts over text scraping, and refuse features that do not fit the current shape.

That means the wiki should not be a changelog. It should be the repo's architecture memory: the pages a future agent reads before changing a subsystem.

## Useful complexity to preserve

Preserve these primitives:

- Flat page identity under `.almanac/pages`.
- Stable kebab-case slugs.
- `[[...]]` links for pages, files, folders, and cross-wiki refs.
- Topic DAG as classification, not folder hierarchy.
- `sources:` as evidence and `sources[type=file]` as file-aware retrieval input.
- `archived_at`, `superseded_by`, and `supersedes` for fundamental reversals.
- `almanac serve` as the human browse layer over graph primitives.
- Garden as the operation that can merge, split, archive, relink, retopic, and no-op.
- The rule from `wiki-organization-primitives`: metadata is for facts the system queries mechanically; editorial meaning belongs in slugs, leads, links, topics, hubs, and prose.

Do not add `subject:` or `type:` frontmatter as a shortcut for cleanup. That would create a second hidden taxonomy and make future agents reconcile page type, topic, title, hub placement, and prose. The current problem is editorial drift, not missing metadata.

## Main architectural objections

### 1. The topic DAG mixes inheritance with orthogonal classification

Evidence:
- `agents` is a child of both `flows` and `stack`.
- `wiki-design` is a child of both `systems` and `decisions`.
- `prompt-system` is a child of both `agents` and `wiki-design`.
- `almanac topics show flows --descendants` pulls in external references and product pages such as `codex-supermemory`, `farzapedia`, `opendeepwiki`, `superpaper`, and `just-in-time-context-surfacing`.
- `almanac topics show systems --descendants` pulls in product strategy and competitive research through `wiki-design`.

Diagnosis:
The DAG currently treats broad concerns as parent-child inheritance, but many of these concepts are overlays. `agents` is not a subtype of `stack`; it contains runtime providers, prompts, external agent tools, and lifecycle flows. `wiki-design` is not simply a subsystem; it is partly product doctrine, partly prompt doctrine, partly storage doctrine, and partly architecture rationale.

Recommendation:
Flatten the top-level DAG around domain neighborhoods and use multi-tagging for page roles. Avoid parent edges between orthogonal axes. A page can belong to `flows` and `provider-runtime` without making every provider page a descendant of `flows`.

### 2. The wiki lacks an explicit front door

Evidence:
- The page inventory has no `getting-started.md`, but `almanac-serve` says the home route treats `.almanac/pages/getting-started.md` as the single markdown-backed front door.
- `lifecycle-architecture` is a reading map but has only one backlink.
- `wiki-organization-primitives` has stronger centrality than the intended architecture map.

Diagnosis:
Future agents need a first page that says what to read for a code change, product change, prompt change, provider change, source-provenance change, sync change, and viewer change. Right now the likely entry point is whichever search result wins.

Recommendation:
Create one front-door hub, probably `getting-started.md` or `codealmanac-map.md`. Because the viewer already privileges `getting-started.md`, use that slug unless there is a product reason not to. The page should be a map, not a tutorial.

### 3. Several pages are overgrown session composites

Evidence:
- `github-native-wiki-maintenance` is about 12,266 words with 65 sources.
- `capture-automation` is about 6,983 words with 37 sources.
- `almanac-product-family` is about 4,907 words.
- `wiki-organization-primitives` is about 4,646 words.
- `evidence-bundles` is about 4,077 words.
- `almanac-serve` is about 3,208 words.
- `company-brain` is about 3,063 words.

Diagnosis:
These pages carry current contract, history, rationale, implementation details, product strategy, incidents, open questions, and prior art in the same body. That is not how an agent retrieves architecture. It forces the next agent to skim a journal entry when it needs a contract.

Recommendation:
Split long pages by reader question:

- What is current?
- How does it run?
- What contract must I preserve?
- Why was this chosen?
- What broke before?
- What remains open?

History that explains a current invariant can stay. Chronological session accumulation should not.

### 4. Source provenance exists as a product doctrine but not as page discipline

Evidence:
- `almanac health` reports no orphans, no dead refs, no broken links, no broken xwiki links, and no slug collisions.
- The same health run reports 347 unused sources, 29 legacy-frontmatter pages, and 135 ambiguous legacy sources.
- `source-provenance` says source lists should explain relevance and support claims, not collect everything the agent inspected.

Diagnosis:
The graph passes structural health while failing evidence hygiene. A source list with dozens of uncited paths is not neutral provenance; it is a residue of how the page was generated.

Recommendation:
Treat source cleanup as part of the gardening rewrite. Migrate legacy `files:` where safe, delete or rewrite unsupported source entries, keep only evidence that supports claims, and cite non-obvious claims close to the claim. Do not ask Garden to invent citations mechanically.

### 5. Product and competitor pages are valuable but overrepresented in the agent-first repo wiki

Evidence:
- `product-positioning` and descendants contain 18 pages.
- Several competitor pages are under 1,100 words and mostly preserve one research pass: `nessie`, `moxie-docs`, `opendeepwiki`, `dosu`, `agentmemory-competitor`, `codex-supermemory`, and `mem0`.
- `github-native-wiki-maintenance`, `almanac-product-family`, `company-brain`, and `open-source-almanac` carry broader product strategy and have many backlinks.

Diagnosis:
The wiki has absorbed product strategy and competitive research because those discussions shape the project. That is legitimate. The current shape still makes product research compete with architecture memory for attention. A future coding agent searching `agents`, `flows`, or `systems` should not have to traverse every external-memory product reference.

Recommendation:
Keep product strategy as a distinct neighborhood. Collapse low-signal competitor pages into a smaller prior-art structure unless each page has a durable CodeAlmanac-specific conclusion that future implementation depends on.

## Target wiki architecture

The target model should be:

```text
README.md
  states notability, source policy, writing policy, topic policy

getting-started
  front door and reading map for future agents

Architecture neighborhood
  codealmanac-architecture or lifecycle-architecture as hub
  storage-and-retrieval hub
  provider-runtime hub
  cli-and-local-operations hub
  viewer-and-human-browse hub

Wiki model neighborhood
  wiki-organization-primitives anchor
  source-provenance
  wikilink-syntax
  topic-dag
  page-shapes-and-gardening policy

Lifecycle neighborhood
  wiki-lifecycle-operations anchor
  build-operation
  ingest-operation
  capture-flow
  sync-automation
  capture-ledger
  process-manager-runs
  operation-prompts

Product strategy neighborhood
  almanac-product-family anchor
  github-native-wiki-maintenance anchor or hub
  open-source-almanac
  customer-segmentation
  almanac-business-model
  hosted-deployment-environment, if not merged

Prior art neighborhood
  competitive-landscape hub
  memory-systems-prior-art
  documentation-tools-prior-art
  company-brain, if retained as category anchor
```

This architecture keeps pages as the unit of reading and neighborhoods as the unit of understanding. It follows the existing doctrine in `wiki-organization-primitives`: hubs route and leaves explain.

## Recommended page neighborhoods

### Front door

Add:
- `getting-started.md`

Purpose:
Tell future agents where to start. It should include a short read order:

- Changing lifecycle operations: read `lifecycle-architecture`, `wiki-lifecycle-operations`, `process-manager-runs`, `harness-providers`.
- Changing sync or automation: read `capture-flow`, `capture-automation`, `capture-ledger`, `automation`.
- Changing wiki storage or retrieval: read `sqlite-indexer`, `source-provenance`, `wikilink-syntax`, `topic-dag`, `global-registry`.
- Changing prompts or page-writing behavior: read `operation-prompts`, `wiki-organization-primitives`, `source-provenance`.
- Changing product/GitHub direction: read `almanac-product-family`, `github-native-wiki-maintenance`, `open-source-almanac`.

Do not make this page a general explanation of CodeAlmanac. It should be an agent routing map.

### Lifecycle operations

Keep:
- `lifecycle-architecture`
- `wiki-lifecycle-operations`
- `build-operation`
- `ingest-operation`
- `capture-flow`
- `capture-ledger`
- `process-manager-runs`
- `harness-providers`
- `operation-prompts`

Rewrite shape:
- `lifecycle-architecture` should become the hub and gain backlinks from the pages it routes.
- `wiki-lifecycle-operations` should stay the semantic contract for Build, Absorb, and Garden.
- `capture-flow` should own current sync-to-Absorb runtime behavior.
- `capture-automation` should be renamed or split because it currently means both scheduler automation and historical capture design.

Split candidate:
- `capture-automation` into:
  - `sync-automation` for current scheduler contract
  - `sync-cost-control-incident` or `capture-sweep-recursion` for the 2026-05-28 cost incident
  - `legacy-hook-migration` only if `sessionend-hook` is not enough

### Storage and retrieval

Keep:
- `sqlite-indexer`
- `source-provenance`
- `wikilink-syntax`
- `topic-dag`
- `global-registry`

Add or reshape:
- Add a small hub such as `storage-and-retrieval` if these pages remain hard to discover.
- Keep `sqlite-indexer` focused on derived SQLite state and query semantics.
- Keep `source-provenance` focused on evidence and citation policy.
- Keep `topic-dag` and `wikilink-syntax` as reference pages, but link them from the hub and front door.

Delete/collapse candidates:
- If `wikilink-syntax` stays under 300 words and only restates syntax already in README/spec, merge it into `wiki-organization-primitives` or a `wiki-model-reference` page. Keep it separate only if it remains the canonical source for link classification edge cases.
- If `topic-dag` stays under 300 words and only restates implementation, merge it into `wiki-organization-primitives` or `storage-and-retrieval`. Keep it separate only if it owns cycle prevention, retagging behavior, and query implications.

### Provider runtime

Keep:
- `harness-providers`
- `provider-lifecycle-boundary`
- `claude-agent-sdk`
- `global-agent-instructions`
- `agents-md`

Rewrite shape:
- `harness-providers` is the runtime adapter anchor.
- `provider-lifecycle-boundary` should either become a decision page with clear rationale or be merged into `harness-providers`.
- `global-agent-instructions` has six backlinks and zero outbound links. Add outbound links to `agents-md`, `operation-prompts`, `harness-providers`, and setup/install pages.
- `claude-agent-sdk` should remain a stack page only for repo-specific SDK constraints. Generic Claude SDK facts should be deleted unless they affect CodeAlmanac.

### CLI and local operations

Keep:
- `lifecycle-cli`
- `almanac-doctor`
- `automation`
- `self-update`
- `install-time-node-launcher`
- `almanac-serve`
- `verification-workflow`, if it carries repo-specific workflow that is not already in `AGENTS.md` or `MANUAL.md`

Collapse candidates:
- `verification-workflow` is about 228 words and has zero backlinks. Merge into `getting-started`, `.almanac/README.md`, or a `developer-workflow` page unless it grows real non-obvious workflow knowledge.
- `install-time-node-launcher` is short and has one outbound link. Keep only if the launcher is a recurring packaging trap; otherwise merge into `lifecycle-cli` or a packaging/runtime page.

### Wiki model and gardening

Keep:
- `wiki-organization-primitives`
- `source-provenance`
- `documenting-software-architectures`
- `operation-prompts`
- `deep-refactor-audit`, if skills remain repo-owned durable agent behavior

Rewrite shape:
- `wiki-organization-primitives` is too valuable to delete but too long to be an easy policy page. Split the durable doctrine into:
  - `wiki-organization-primitives` as concise current doctrine
  - `subject-neighborhoods-and-hubs` if the examples and browse projection material need their own page
  - `source-provenance` remains separate
  - `garden-operation` if Garden behavior needs a current contract page distinct from operation prompts

Do not turn architecture-documentation lenses into page-type schema. Use them as writing lenses: module view, runtime view, allocation view, rationale, glossary, roadmap, release/config context.

### Product strategy

Keep as anchors:
- `almanac-product-family`
- `github-native-wiki-maintenance`
- `open-source-almanac`
- `customer-segmentation`
- `almanac-business-model`

Split:
- `github-native-wiki-maintenance` should not stay as a 12k-word monolith. Split into:
  - `almanac-for-github`
  - `github-app-permissions`
  - `pr-context-cards`
  - `almanac-update-pr-workflow`
  - `branch-scoped-almanacs`
  - `hosted-viewer-boundary`
  - `github-prior-art-and-competition`
- `almanac-product-family` should split current product model from generalized future product exploration if it keeps growing.

Collapse:
- `hosted-deployment-environment` has zero backlinks. Merge it into `github-native-wiki-maintenance` or a hosted-architecture page unless it becomes an implementation-critical deployment contract.

### Prior art and competition

Keep:
- `company-brain` only if it remains the category anchor.
- `documenting-software-architectures` because it directly shapes wiki doctrine.
- `opendeepwiki` only if it keeps a durable information-architecture lesson.

Collapse or delete:
- `nessie`, `moxie-docs`, `dosu`, `agentmemory-competitor`, `codex-supermemory`, and `mem0` should be merged into `competitive-landscape` or `memory-systems-prior-art` unless each page states a specific, durable CodeAlmanac product or architecture consequence in the first paragraph.
- A competitor page that says "this exists and is adjacent" is not enough. It must answer "what should CodeAlmanac copy, reject, or defend against?"

## Topic taxonomy changes

The current taxonomy uses roots such as `stack`, `systems`, `flows`, and `decisions`, then hangs mixed concepts below them. The target taxonomy should separate domain neighborhoods from page-role overlays.

Recommended roots:

```yaml
architecture:
  pages about current system shape, boundaries, invariants, and subsystem maps

lifecycle:
  Build, Absorb, Garden, sync, jobs, operation execution, and write-capable wiki work

storage:
  markdown corpus, SQLite projection, registry, sources, wikilinks, topics, file refs

cli:
  command surface, setup, doctor, automation commands, self-update, local serve

provider-runtime:
  provider adapters, runtime contracts, auth/readiness boundaries, SDK constraints

prompt-system:
  base prompts, operation prompts, writing doctrine, reviewer/Garden guidance

wiki-model:
  page graph, notability, sources, hubs, anchors, neighborhoods, browse projection

product-strategy:
  product family, business model, customer segmentation, open-source route, GitHub product

prior-art:
  external products, books, docs systems, competitor lessons, market references

automation:
  scheduled local behavior and recurring background work

viewer:
  local viewer, hosted viewer implications, human browse surface
```

Recommended overlays:

```yaml
decisions:
  why X over Y; rejected alternatives and current rationale

flows:
  multi-step runtime or operational processes

constraints:
  invariants future changes must preserve

failure-modes:
  incidents, traps, edge cases, and regressions discovered through real runs

reference:
  compact syntax, command, schema, or contract pages
```

Avoid parent edges from overlays to domains. For example, `harness-providers` can be tagged `provider-runtime`, `architecture`, and `reference`; that does not mean every provider-runtime page should become a descendant of `reference` or `flows`.

Specific changes:
- Replace `agents` with narrower topics: `provider-runtime`, `prompt-system`, and `agent-instructions`.
- Keep `stack` only for third-party libraries currently depended on by the implementation. Do not put external competitors or prior-art docs under `stack`.
- Move `wiki-design` toward `wiki-model`. Stop making it a descendant of `systems`.
- Move competitor pages under `prior-art` and, when relevant, `product-strategy`.
- Add `viewer` because `almanac-serve` and hosted browsing are now significant product and implementation surfaces.
- Add `failure-modes` because the current wiki contains real incident knowledge but hides it inside long flow pages.

## Page shape contracts

Use page shapes as editorial contracts, not frontmatter schema.

### Hub page

Job:
Route readers through a dense neighborhood.

Shape:
- Lead states the neighborhood and when to read it.
- "Start here" list with 4-8 pages.
- "Current contracts" list.
- "History or failure modes" list.
- "Open questions" list only when those questions are still current.

Hubs should be short. If a hub starts explaining implementation in depth, split that material into a leaf page.

### Anchor page

Job:
Canonical current truth for a stable subject.

Shape:
- Lead states what the subject is and why CodeAlmanac cares.
- Current behavior.
- Boundaries to preserve.
- Links to flow, decision, failure, and reference pages.
- Sources only for claims that need evidence.

An anchor should usually be 600 to 1,500 words. Longer is allowed only when the subject is genuinely indivisible.

### Contract page

Job:
Name invariants future code must preserve.

Shape:
- Lead states the invariant.
- Why it exists.
- What breaks if violated.
- Files and commands involved.
- Related failure modes.

### Flow page

Job:
Explain a runtime or operational sequence.

Shape:
- Inputs and trigger.
- Main sequence.
- State written.
- Handoff points.
- No-op and failure behavior.
- Debugging commands.

### Decision page

Job:
Explain why the current approach exists.

Shape:
- Decision.
- Context.
- Rejected alternatives.
- Current consequence.
- Conditions that would reopen the decision.

### Failure mode or incident page

Job:
Preserve a trap future work could repeat.

Shape:
- Symptom.
- Root cause.
- Fix or current mitigation.
- Invariant added.
- Affected files or commands.

Do not bury incidents inside long flow pages when they imply a durable invariant.

### External reference page

Job:
Preserve what CodeAlmanac learned from a third-party product, project, book, or docs system.

Shape:
- What the external thing is.
- Why it matters to CodeAlmanac.
- What to copy.
- What to reject.
- Which current page or product decision it affects.

If that last section is weak, merge the page into a prior-art roundup.

## Archiving, merging, and deletion policy

### Archive

Archive only when the central recommendation or approach is reversed and both old and new pages have value. This matches the codebase-wiki spec. `sessionend-hook` is a correct example: the hook path is obsolete, the scheduler path supersedes it, and migration cleanup still needs historical context.

### Merge

Merge when two pages have the same reader question or when one page is merely a weak slice of another.

Immediate merge candidates:
- `hosted-deployment-environment` into `github-native-wiki-maintenance` or a hosted architecture page.
- `verification-workflow` into `getting-started`, `.almanac/README.md`, or a developer workflow page.
- `provider-lifecycle-boundary` into `harness-providers` unless it is rewritten as a clear decision page.
- `wikilink-syntax` and `topic-dag` into a compact wiki-model reference unless they gain enough edge-case ownership to stand alone.

### Split

Split when a page answers multiple independent future-agent questions.

Immediate split candidates:
- `capture-automation`
- `github-native-wiki-maintenance`
- `almanac-product-family`
- `wiki-organization-primitives`
- `evidence-bundles`, if it mixes current operation boundary with future connector product design

### Delete

Delete or collapse pages that do not change future implementation, product positioning, or agent behavior.

Direct delete/collapse candidates:
- `nessie`
- `moxie-docs`
- `dosu`
- `agentmemory-competitor`
- `codex-supermemory`
- `mem0`
- `opendeepwiki`, unless retained as a wiki-design prior-art page

Do not preserve a page because the source was real. Preserve the durable conclusion, then delete the research residue.

### Redirect or alias

The current model has archive lineage but no lightweight redirect. The target architecture needs a redirect convention before large merge work. Until a first-class redirect exists, prefer one of:

- Merge content and leave no page when no one should search the old slug.
- Archive only when the old page is historical truth.
- Keep a tiny "redirect-style" page only when the old slug is a common search term, with a lead that points to the canonical page.

Do not create dozens of stub redirects. That is another form of graph pollution.

## Staged gardening roadmap

### Phase 0: Freeze the shape before rewriting

Goal:
Prevent this rewrite from becoming another session-driven accumulation.

Changes:
- Decide the target topic list.
- Decide the target hub list.
- Decide which pages are anchors, hubs, leaves, archives, and merge/delete candidates.

Why first:
The current `.almanac/pages` worktree is already dirty. A gardening pass should not mix taxonomy rewrite, source migration, product-page splitting, and implementation refactor fallout.

Verification:
- `git status --short` shows only intended wiki changes for the gardening branch or commit.
- `almanac health` remains free of broken links and slug collisions.

### Phase 1: Add the front door and hubs

Goal:
Make the current graph navigable before deleting or splitting.

Changes:
- Add `getting-started`.
- Rewrite `lifecycle-architecture` as an actual hub, or add `codealmanac-architecture` and link it strongly.
- Add or designate hubs for `wiki-model`, `storage-and-retrieval`, `provider-runtime`, `cli-and-local-operations`, `product-strategy`, and `prior-art`.

Why first:
Hubs give agents stable places to link from and make subsequent merges easier to review.

Verification:
- Backlinks to hubs increase.
- No hub tries to carry deep implementation detail.

### Phase 2: Repair the topic DAG

Goal:
Stop descendant queries from mixing product research, external references, runtime flows, and system architecture.

Changes:
- Add domain topics.
- Convert page-role topics into overlays.
- Remove parent edges that imply false inheritance.
- Retag pages according to primary neighborhood and role.

Why first:
Topic search is one of the main agent entry points. A bad DAG makes good pages feel noisy.

Verification:
- `almanac topics show flows --descendants` no longer returns competitor pages.
- `almanac topics show systems --descendants` no longer returns broad product strategy pages through `wiki-design`.
- `almanac search --topic provider-runtime` returns provider runtime pages, not every agent-adjacent page.

### Phase 3: Clean provenance

Goal:
Make sources support claims instead of recording everything an agent inspected.

Changes:
- Run or manually stage the deterministic legacy-source migration where safe.
- Trim unused source entries on heavily sourced pages.
- Add citations near non-obvious claims.
- Leave ambiguous legacy sources only where they still support a claim and the note explains why.

Why first:
Splitting pages with dirty source lists spreads the problem into more files.

Verification:
- `unused-sources` count drops materially.
- `legacy-frontmatter` count drops.
- No generated citations are invented without claim support.

### Phase 4: Split long architecture and product pages

Goal:
Turn monolith pages into readable neighborhoods.

Changes:
- Split `capture-automation` into current contract, incident/failure mode, and migration/history pages.
- Split `github-native-wiki-maintenance` into GitHub product/architecture leaves.
- Split `almanac-product-family` if generalized Almanac exploration keeps drowning current CodeAlmanac product truth.
- Split `wiki-organization-primitives` into concise doctrine plus optional supporting prior-art or browse-projection pages.

Why first:
These pages are the largest sources of cognitive load and source bloat.

Verification:
- Each split page has a clear lead, source list, and backlink path from a hub.
- The old slug either remains the hub or is archived/redirected intentionally.

### Phase 5: Collapse competitor and weak leaf pages

Goal:
Remove research residue.

Changes:
- Merge low-signal competitor pages into `competitive-landscape`, `memory-systems-prior-art`, or `documentation-tools-prior-art`.
- Delete pages whose only durable fact is already represented in a stronger page.
- Keep separate pages only for external references that future implementation should read directly.

Why after hubs:
Deletion is safer once the prior-art neighborhood has a canonical home.

Verification:
- Page count drops or stays stable despite splits.
- Product pages cite prior-art roundups instead of linking through many one-off competitor leaves.

### Phase 6: Harden Garden doctrine

Goal:
Prevent re-accumulation.

Changes:
- Update `.almanac/README.md` after the rewrite to name the new hubs, source discipline, and delete/merge standards.
- Update prompt doctrine only if current prompts do not already enforce create/update/merge/split/archive/no-op.
- Add a recurring Garden checklist for long pages, unused sources, low-link pages, false topic inheritance, and weak external-reference pages.

Why last:
The doctrine should describe the agreed target graph, not the transitional mess.

Verification:
- A future Garden run can explain why it created no page, merged a page, or deleted a weak external reference.

## What should not be done

Do not move `.almanac/pages` into folders as the primary fix. The spec and README are right that flat page identity plus topics and links are the core model. Folders can become a browse projection later, but they should not be the conceptual source of truth for a codebase wiki.

Do not add `type:` or `subject:` frontmatter. That hides editorial work in schema and creates another surface for drift.

Do not preserve competitor pages as a matter of completeness. This is not a market-research vault. It is a repo wiki for future agents.

Do not treat `almanac health` as the final quality gate. It catches structural integrity, not whether the graph is readable, current, or appropriately compressed.

Do not use Garden as a deterministic migration engine. Deterministic source-frontmatter rewrites belong to migration commands; Garden should make editorial judgments.

## Open questions for the owner

1. Should product strategy live indefinitely in this repo wiki, or should some strategy pages move to a separate Almanac once the product has more repositories?
2. Should `getting-started` be the canonical front door because the viewer already recognizes it, or should the project prefer a more explicit slug such as `codealmanac-map` and adjust viewer behavior later?
3. Should low-signal competitor pages be deleted outright after merging conclusions, or kept as tiny redirect-style pages for searchability?
4. Should `company-brain` stay as a category anchor, or should it become one section inside product strategy?
5. Is `docs/almanac/` still a future public/team profile, or should this repo continue treating `.almanac/` as both local and public canonical shape until the hosted product exists?

## Bottom line

The current `.almanac` is not a failed wiki. It is a successful capture corpus that now needs a major Garden pass. Keep the primitives. Rewrite the architecture around front door, hubs, anchors, and leaf contracts. Flatten false topic inheritance. Split the long pages. Merge or delete research residue. Make source lists earn their place. The target is not "more pages"; it is a graph that lets a future agent make a safer code change faster.
