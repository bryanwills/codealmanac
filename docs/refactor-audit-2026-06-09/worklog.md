# Refactor Audit: .almanac Garden

Goal:
Critically audit `.almanac/` as the repo-owned living wiki for codealmanac to determine which page structures, topics, conventions, boundaries, names, abstractions, workflows, and gardening practices should be preserved, simplified, removed, or redesigned.

Core questions:
- Why does each wiki structure exist?
- Is it still needed?
- Is this the simplest shape that can support the product?
- Did this complexity come from real constraints or accidental accumulation?
- Is this hand-rolled documentation architecture justified, or should it follow a standard pattern?
- What would the wiki look like if we designed it cleanly today?

Non-goals:
- Do not modify production code.
- Do not produce a shallow smell list.
- Do not assume the current wiki architecture is justified.
- Do not recommend patterns without explaining concrete movement in the codebase.

Success criteria:
- Current wiki architecture is mapped.
- Major documentation boundaries are judged.
- Questionable pages, topics, and workflows are called out.
- Hand-rolled documentation machinery is compared against standard architecture documentation patterns.
- Accidental complexity is separated from legitimate complexity.
- Prior art, named patterns, and mature documentation practices are researched where useful.
- A target wiki architecture and gardening roadmap are written.

## 2026-06-09 Setup And Constraints

The requested skill is `deep-refactor-audit`, so this is a no-code architecture audit. The writable surface is `docs/refactor-audit-2026-06-09/`. I am not editing implementation code or `.almanac` pages during this pass.

Repo constraints read before the audit:

- `MANUAL.md` says work should reshape the codebase so features fit, and that refusal or re-architecture is valid when a request does not fit the current shape.
- `.almanac/README.md` says the wiki stores non-obvious knowledge that helps future agents: decisions, failure modes, cross-cutting flows, constraints, subsystems, integrations, and product/market conclusions that shape CodeAlmanac.
- The codebase wiki spec says intelligence belongs in prompts rather than pipelines, `.almanac/` is flat, and lifecycle operations own AI-written prose.

Working tree note: the repo was already heavily dirty. `git status --short` showed broad `.almanac/pages/*` edits, many implementation file edits, deleted old `src/process/*` files, new `src/jobs/*` files, and an existing `docs/architecture-audit-2026-06-08/` audit. I am treating those as existing user/session state and not reverting them.

## 2026-06-09 Evidence Pass

Commands and observations:

- `almanac topics` shows 14 topics. The largest topics are `agents`, `product-positioning`, `cli`, `decisions`, `systems`, `flows`, and `competitive-research`.
- `almanac health` reports no graph integrity failures: no orphans, stale pages, dead refs, broken links, broken xwiki links, missing sources, duplicate sources, empty topics, empty pages, or slug collisions.
- The same health run reports 347 unused source IDs, 29 pages with legacy source metadata, and 135 ambiguous legacy source targets.
- A YAML-aware page inventory found 52 pages and one archived page, `sessionend-hook`.
- Largest pages: `github-native-wiki-maintenance` at 831 lines, `capture-automation` at 726, `wiki-organization-primitives` at 397, `almanac-serve` at 387, and `almanac-product-family` at 320.

Initial judgment: the graph is mechanically healthy but editorially undergardened. The storage model is not the problem. Hubs, source hygiene, page splitting, and naming/lineage are the problem.

## 2026-06-09 Prior Art Pass

External references checked:

- Diataxis: useful for reader-purpose categories, not as storage hierarchy.
- Write the Docs Docs as Code: supports repo-owned markdown, Git review, and shared development workflow.
- SEI Views and Beyond / ISO 42010: supports architecture docs organized around stakeholder concerns and views.
- C4 model: useful zoom levels for architecture hubs; not a page taxonomy.
- arc42: useful completeness checklist for architecture documentation; not a folder template to copy.
- MADR: useful decision-page shape; not a reason to turn the wiki into numbered ADRs.

Synthesis: CodeAlmanac should adapt these as page-neighborhood guidance. Major subsystem hubs should answer what parts exist, how they run, where they live, why decisions were made, and what constraints future changes must preserve.

## 2026-06-09 Local Findings Written

Created:

- `README.md`
- `source-map.md`
- `smells.md`
- `feature-questions.md`
- `hand-rolled-inventory.md`
- `research-notes.md`
- `target-architecture.md`
- `refactor-roadmap.md`
- `subagent-briefs.md`

Core local verdict: do a major garden rewrite, but do not replace the wiki model. Keep flat markdown, topics, wikilinks, source provenance, health, and Garden. Add hubs, clean sources, split oversized pages, and gate product strategy.

## 2026-06-09 Sidecar Reports Integrated

Four sidecar reports landed under `reports/` and were folded into the main audit files.

Integrated conclusions:

- Add `getting-started` as the wiki front door. This is a normal page, not schema.
- Keep the hand-rolled graph primitives. The custom model earns its cost because agent retrieval needs page links, file/folder refs, topics, source provenance, health, and Garden judgment.
- Treat topic overload as the main retrieval defect. `agents` should not carry runtime providers, prompts, competitors, external inspiration, product strategy, and wiki theory at once.
- Re-scope the target topic set around current architecture, lifecycle, storage, CLI, provider runtime, prompt system, wiki model, product strategy, prior art, competitive research, automation, and viewer.
- Treat decisions, flows, constraints, failure modes, and reference as page shapes or overlays unless there is a concrete topic-search need.
- Define or delete `status` and `verified`; they currently look like schema without documented semantics.
- Update exported guidance that still teaches legacy `files:` provenance after the garden rewrite settles the `sources:` contract.
- Move, merge, or archive product and external-reference pages unless each one states the implementation, product, trust, pricing, or workflow decision it shapes.

Files updated after integration:

- `README.md`
- `source-map.md`
- `smells.md`
- `feature-questions.md`
- `hand-rolled-inventory.md`
- `target-architecture.md`
- `refactor-roadmap.md`
- `subagent-briefs.md`
