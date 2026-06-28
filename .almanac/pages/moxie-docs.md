---
title: Moxie Docs
summary: Moxie Docs is a close hosted GitHub-repo documentation competitor that markets source-cited docs generation, drift checks on merge, MCP context for agents, and docs-only review PRs.
topics: [competitive-research, product-positioning]
sources:
  - id: moxie-eval-session
    type: conversation
    path: /Users/kushagrachitkara/.codex/sessions/2026/06/09/rollout-2026-06-09T15-29-43-019eae81-80e8-7b82-95bd-2c491fd3872a.jsonl
    note: Records the public-site and setup-flow evaluation of Moxie Docs, including homepage copy, the GitHub OAuth handoff, the in-app-browser failure, and the Chrome dashboard state after session reuse.
  - id: moxie-home
    type: web
    url: https://moxiedocs.com/
    retrieved_at: 2026-06-05
    note: Supports Moxie's public product promise, pricing, and repo-documentation positioning.
  - id: moxie-workflow
    type: web
    url: https://moxiedocs.com/workflow
    retrieved_at: 2026-06-05
    note: Supports claims about indexing, pull-request checks, and docs-only cleanup PRs.
  - id: moxie-use-cases
    type: web
    url: https://moxiedocs.com/use-cases
    retrieved_at: 2026-06-05
    note: Supports claims about generated architecture, conventions, walkthroughs, gaps, and searchable repo context.
  - id: moxie-security
    type: web
    url: https://moxiedocs.com/security
    retrieved_at: 2026-06-05
    note: Supports claims about the hosted trust boundary and workspace permissions.
  - id: moxie-mcp
    type: web
    url: https://moxiedocs.com/mcp
    retrieved_at: 2026-06-05
    note: Supports claims about MCP context for coding agents.
  - id: comparison-session
    type: conversation
    path: /Users/rohan/.codex/sessions/2026/06/05/rollout-2026-06-05T12-51-25-019e9957-24f5-76a3-9494-603f667f2bbf.jsonl
    note: Records the 2026-06-05 comparison of CodeAlmanac, the `usealmanac` hosted GitHub App direction, and Moxie Docs.
status: active
verified: 2026-06-09
external_version: Public site and dashboard state observed on 2026-06-09; public web pages also reviewed on 2026-06-05.
---

# Moxie Docs

The 2026-06-09 evaluation observed `Moxie Docs` as a hosted product for GitHub-repo documentation and agent context. Its homepage promised four tightly connected behaviors: generate source-cited docs from a repo, re-check those docs after merges, expose scoped repo context to coding agents over MCP, and open docs-only review PRs instead of silently changing code. [@moxie-eval-session]

That makes Moxie one of the closest observed products to CodeAlmanac's remote direction. The overlap is not generic "AI docs." The observed surface was specifically GitHub-native repo indexing, drift-aware documentation maintenance, agent-facing MCP retrieval, and reviewable documentation updates. [@moxie-eval-session]

## Observed Public Product Surface

The public homepage navigation exposed `Workflow`, `Use cases`, `Security`, `MCP`, and `Plans`, plus a `Connect GitHub` path at `/auth/github?next=/dashboard`. The hero copy said: "Docs that write themselves. Agents that already know your repo." The supporting paragraph said Moxie connects a GitHub repo, writes documentation, flags drift when code changes, and serves conventions to AI agents over MCP. [@moxie-eval-session]

The 2026-06-05 public-web comparison recorded the same product shape with more feature detail: Moxie connects to GitHub, indexes selected repositories, generates architecture pages, conventions, walkthroughs, gap reports, and searchable chunks, exposes compact MCP context for Claude Code, Cursor, and Codex, checks pull requests for description alignment and documentation impact, and opens docs-only cleanup PRs for review. [@moxie-home] [@moxie-workflow] [@moxie-use-cases] [@moxie-mcp]

The homepage also exposed the durable marketing claims that matter for comparison work:

- docs are `source-cited`
- docs are `read-only by default`
- context is `scoped per repo`
- docs are re-checked `on every merge`
- stale pages are `regenerated`
- agents use `scoped lookups` over MCP instead of repeated repo crawling
- a weekly `Friday Cleanup` opens a `docs-only` review PR

Those claims make Moxie closer to [[github-native-wiki-maintenance]] than to generic company-brain or personal-memory products. The product is framed around GitHub repos and documentation upkeep, not around broad cross-tool company ingestion. [@moxie-eval-session]

## Observed Setup Boundary

The evaluated setup path started from `/auth/github?next=/dashboard` and redirected to a GitHub OAuth login URL whose `redirect_uri` pointed at a `supabase.co/auth/v1/callback` endpoint. The observed login URL requested `scope=user:email` at that stage. The session did not yet observe repo selection, GitHub App installation, billing entry, or the first completed index. [@moxie-eval-session]

The in-app Codex browser reached the GitHub sign-in page but lost usable tab state before the flow completed. The browser automation session later reported only an attached `about:blank` tab and could not reattach to the earlier visible tab. That made the in-app browser a bad environment for continuing the auth-gated evaluation. [@moxie-eval-session]

The follow-up Chrome run behaved differently because it reused the user's existing GitHub session. Opening the same auth URL in Chrome landed directly on `https://moxiedocs.com/dashboard`, where the workspace showed `No repo connected` and navigation entries for `Overview`, `Docs`, `Changelog`, `MCP`, `Admin`, and `Settings`. The durable lesson is that Moxie's hosted dashboard can be inspected without re-entering credentials when Chrome already holds the relevant GitHub session, but repo connection still remains a separate step after login. [@moxie-eval-session]

## Product Boundary Relative To CodeAlmanac

The session positioned Moxie as a hosted GitHub/App layer, while CodeAlmanac's current strongest trust boundary is repo-owned memory in `.almanac/` plus local search and capture flows. Moxie's observed promise is managed indexing, managed MCP serving, and managed docs-maintenance PRs over a hosted dashboard. CodeAlmanac's competing promise is that durable project memory lives in reviewed markdown inside the repository rather than behind a hosted canonical store. [@moxie-eval-session]

The sharp product contrast is the canonical artifact. Moxie is a managed workspace and GitHub App that reads repo data server-side, stores generated docs, notes, bookmarks, settings, and MCP context behind workspace auth, and pushes docs-only PRs when automation is enabled. [@moxie-home] [@moxie-security] CodeAlmanac keeps the durable wiki in the repository as markdown pages, topics, links, source references, and Git-reviewed edits.

This makes Moxie useful as a contrast case for three product questions:

- how much of the value can be delivered through GitHub-native maintenance without making the hosted service the canonical memory artifact
- how much users value docs-regeneration and drift checks versus broader project-memory capture
- whether agent context should be sold as MCP-scoped lookup over maintained docs rather than as a larger company-brain layer

Inside the current wiki graph, Moxie is the clearest observed product that packages pieces of [[open-source-almanac]], [[github-native-wiki-maintenance]], and [[just-in-time-context-surfacing]] into one hosted public-facing surface. [@moxie-eval-session]

## Hosted Almanac Comparison

The `usealmanac` hosted GitHub App direction overlaps Moxie more than the current local-CLI landing page implies. Its implemented foundation is signed GitHub webhook intake, installation and repository persistence, event dedupe, health checks, Supabase-hosted state, Doppler-managed secrets, Render deployment, and Modal worker smoke; its planned loop is PR-triggered Almanac updates that run CodeAlmanac in a worker and commit validated Almanac-root changes back to a PR branch or follow-up PR. [@comparison-session]

Moxie's product lesson for that hosted path is that install should produce an immediate first-index artifact, currentness should have visible states such as current, stale, needs review, and updated, and weekly cleanup PRs may be easier to understand than only per-PR prompts. Moxie's MCP layer is a competitor implementation choice, not a CodeAlmanac requirement, because CodeAlmanac's hosted worker deliberately uses CLI and shell source access so the agent can inspect the repository and PR directly. [@comparison-session]

The strategic risk is that Moxie already packages several CodeAlmanac roadmap ideas in a clean buyer-facing shape: source-cited generated docs, PR drift checks, MCP context, and reviewable update PRs. [@comparison-session] CodeAlmanac should not compete by saying "AI docs for GitHub repos" without narrowing the promise. A stronger sentence is: "`Moxie` keeps generated repo documentation current; `CodeAlmanac` preserves the repo's governed engineering memory."

The product lesson is that currentness must be visible and automatic. CodeAlmanac's wiki quality and Git-native trust boundary are not enough if agents must remember to search manually. [[just-in-time-context-surfacing]] and GitHub-native maintenance workflows become table stakes against Moxie's cleanup-PR story, but the agent source-access interface can remain CLI-first.

## What The Session Did Not Verify

The session did not verify the post-login repo-connection flow, whether GitHub App installation is required for all repos, whether payment details are required before first indexing, what the generated docs actually look like for a real repo, or what MCP configuration Moxie exposes to Codex, Cursor, or Claude Code after setup. The transcript contains informed expectations about those steps, but the durable evidence from this run stops at the unconnected dashboard. [@moxie-eval-session]

## Related Pages

[[competitive-landscape]] is the hub for the full competitive research cluster. [[github-native-wiki-maintenance]] explains the remote CodeAlmanac direction that Moxie most closely resembles. [[company-brain]] places Moxie in the narrower repo-memory and hosted-knowledge landscape rather than the broad company-brain category. [[open-source-almanac]] records the free public-repo product direction whose trust boundary differs from Moxie's hosted dashboard model. [[just-in-time-context-surfacing]] explains the product behavior both systems are trying to improve: agents should receive scoped context before they start rediscovering the repo. [[wiki-organization-primitives]] explains why CodeAlmanac's page, link, topic, source, and file-reference model should remain more structured than flat generated docs.
