# Subagent Briefs

Date: 2026-06-09

Four sidecar agents were dispatched during this audit. They were asked not to edit implementation code or `.almanac` pages, and to write only their assigned reports under `docs/refactor-audit-2026-06-09/reports/`.

## Boundary Critic

Assigned report: `reports/boundary-critic.md`

Prompt summary:

Find mixed responsibilities, misleading page neighborhoods, weak topic boundaries, hidden policy, bad dependency between documentation concepts, and places where product/business notes distort engineering wiki retrieval.

Status: integrated into `README.md`, `source-map.md`, `smells.md`, `target-architecture.md`, and `refactor-roadmap.md`.

Main findings:

- The storage model is sound; the topic graph is overloaded.
- `agents` is the clearest junk-drawer topic.
- Product strategy, prior art, and current engineering architecture need separate neighborhoods.
- `fundraising` should not remain a first-class codebase topic unless it shapes product architecture.

## Feature Skeptic

Assigned report: `reports/feature-skeptic.md`

Prompt summary:

Identify pages, topics, workflows, compatibility stories, and product/market memory that may not deserve to exist in the codebase wiki or should be moved, merged, archived, or reframed.

Status: integrated into `feature-questions.md`, `README.md`, and `refactor-roadmap.md`.

Main findings:

- Product and market pages belong only when they name an implementation or positioning consequence.
- `github-native-wiki-maintenance` should split into product anchor, PR loop, hosted runner, source tools, and risks.
- Weak competitor/inspiration pages should merge into landscape or doctrine pages.
- Hosted deployment and fundraising material should move out unless it records current architecture constraints.

## Hand-Rolled Machinery Critic

Assigned report: `reports/hand-rolled-critic.md`

Prompt summary:

Inventory custom documentation taxonomy, page type conventions, source provenance model, link syntax, and gardening workflow. Compare against standard architecture documentation practices and recommend keep, replace, simplify, wrap, or research.

Status: integrated into `hand-rolled-inventory.md`, `smells.md`, `target-architecture.md`, and `refactor-roadmap.md`.

Main findings:

- Keep the custom graph model: flat pages, topic DAG, wikilinks, sources, health, and Garden.
- Add the missing `getting-started` page.
- Migrate legacy source strings and legacy `files:` provenance.
- Define or delete casual metadata such as `status` and `verified`.
- Update public guidance that still teaches the old provenance model.

## Target Architect

Assigned report: `reports/target-architect.md`

Prompt summary:

Propose a cleaner wiki architecture from first principles for CodeAlmanac as an agent-first repo wiki. Recommend page neighborhoods, topic taxonomy changes, page shapes, archive/merge policy, and staged gardening roadmap.

Status: integrated into `target-architecture.md`, `source-map.md`, and `refactor-roadmap.md`.

Main findings:

- The weak layer is editorial architecture, not storage.
- Add a front door, hubs, anchors, and page-shape contracts.
- Re-scope roots around architecture, lifecycle, storage, CLI, provider runtime, prompt system, wiki model, product strategy, prior art, competitive research, automation, and viewer.
- Treat decisions, flows, constraints, failure modes, and reference as overlays or page shapes.

## Integrated Synthesis

The audit now recommends:

- keep flat markdown, topics, wikilinks, sources, health, and Garden
- add `getting-started` and hubs before schema
- clean topic retrieval and source provenance before broad splitting
- split sync and GitHub-native pages by reader task
- gate product strategy pages by implementation consequence
- add external-reference treatment for non-current architecture inputs
- resolve capture/sync vocabulary drift with hub guidance now and redirect/alias behavior later
- define or delete `status` and `verified`
- update exported guidance so new pages do not recreate legacy provenance
