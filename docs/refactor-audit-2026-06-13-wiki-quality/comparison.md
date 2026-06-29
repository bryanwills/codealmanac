# Comparison

## Reverie

Reverie is the strongest current example.

What works:

- It has a local guide at `wiki/_meta/wiki-conventions.md`.
- It has a readable primary folder shape: `people/`, `organizations/`,
  `legal/`, and `accounts/`.
- Pages are about durable subjects, not source files.
- Source notes explain what each source supports.
- Citations sit near factual claims.
- Sensitive records are summarized with explicit non-reproduction rules.
- Health is clean: no unused sources, no missing sources, no legacy frontmatter.

The pages feel like articles. A page owns one subject, gives a lead, then
sections the reader would actually need.

## CodeAlmanac

CodeAlmanac still has strong pages, especially around provider boundaries,
sync flow, source provenance, and wiki organization doctrine. The problem is
not lack of knowledge.

What degraded:

- Pages often became dense memory deposits instead of clean reader articles.
- Source lists often record everything inspected, not only evidence used.
- Some pages mix current architecture, migration history, product strategy,
  research notes, and prompt doctrine.
- Broad topics such as `agents` and `product-positioning` are carrying too much
  navigation weight.
- The flat page list hides page families and makes coverage harder to see.
- Prompt guidance accumulated project philosophy inline and started to drift.
- Health catches graph integrity, but not whether the page is the right shape.

The failure mode is not "no guidance." It is guidance without a compact,
maintained editorial mechanism.

## General Almanac Manual

General Almanac's newer doctrine is cleaner:

- prompts stay thin;
- detailed doctrine lives in `wiki/_manual/`;
- local rules live in `wiki/_meta/wiki-conventions.md`;
- pages are subject articles;
- sources are evidence;
- conflicts and source gaps are first-class;
- folders are a browse surface, not identity;
- Garden updates both pages and local conventions.

That model should be adapted back to CodeAlmanac, but code wikis need their own
page families.

## What To Preserve From CodeAlmanac

Keep:

- markdown pages as source of truth;
- source/citation frontmatter;
- double-bracket links;
- topic DAG as reading neighborhoods;
- `almanac health`;
- lifecycle operations;
- Garden as the maintenance loop;
- code-specific retrieval by file mentions;
- "intelligence in prompts, not pipelines."

Do not replace this with a strict schema or proposal/apply workflow.

## What To Import From Reverie / General Almanac

Import:

- a manual-first guidance model;
- local wiki conventions as a maintained page;
- primary browse shelves or folders;
- article leads as the retrieval unit;
- source notes that say exactly what is supported;
- citation discipline as a quality gate;
- explicit source-gap/conflict prose;
- Garden responsibility for keeping conventions current.
