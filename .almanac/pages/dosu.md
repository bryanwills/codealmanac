---
title: Dosu
summary: Dosu is a hosted knowledge and documentation competitor whose public product spans PR-time docs drift, OSS Q&A, MCP context, and agent-instruction maintenance, while 2026-06-09 experiments showed separate gates for setup, source connection, knowledge submission, and curated retrieval.
topics: [product-positioning, competitive-research]
sources:
  - id: dosu-maintain-docs
    type: web
    url: https://dosu.mintlify.app/pages/features-maintain-docs
    retrieved_at: 2026-06-07
    note: Supports Dosu's PR-time documentation review and published-document workflow.
  - id: dosu-pricing
    type: web
    url: https://dosu.dev/pricing
    retrieved_at: 2026-06-07
    note: Supports Dosu's public-repo, private-repo, MCP, integrations, OSS maintainer, SSO, RBAC, and audit-log packaging.
  - id: dosu-response-automation
    type: web
    url: https://app.dosu.dev/9affd04a-e6a9-452c-b927-c639e979994c/documents/685b6df1-da30-4ce1-8904-85d547dace97
    retrieved_at: 2026-06-07
    note: Supports Dosu's issue, discussion, pull-request, GitLab, Slack, citation, deployment, and review-dashboard behavior.
  - id: dosu-home
    type: web
    url: https://dosu.dev/
    retrieved_at: 2026-06-07
    note: Supports Dosu's current positioning around knowledge infrastructure, MCP, agent knowledge capture, and direct maintenance of AGENTS.md, CLAUDE.md, and skill definitions.
  - id: dosu-agents-md-blog
    type: web
    url: https://dosu.dev/blog/a-stale-agents-md-is-worse-than-no-agents-md
    retrieved_at: 2026-06-07
    note: Supports the claim that Dosu watches pull requests for AGENTS.md drift and opens suggested edits in the PR workflow.
  - id: dosu-research-session
    type: conversation
    path: /Users/rohan/.codex/sessions/2026/05/31/rollout-2026-05-31T23-31-46-019e8173-bc02-7503-a102-e9de99d6bb9c.jsonl
    note: Records the CodeAlmanac product discussion comparing Dosu, repo-owned Almanac updates, PR-time documentation maintenance, and OSS maintainer workflows.
  - id: dosu-experiment-session
    type: transcript
    path: /Users/kushagrachitkara/.claude/projects/-Users-kushagrachitkara-Downloads-reverie-codealmanac/767924bf-14a8-48e3-8c5c-a69523619cb9.jsonl
    note: Claude session that tested Dosu MCP retrieval and write tools while asking whether Dosu could draft AGENTS.md and whether sources can be added through CLI or MCP.
  - id: dosu-codex-setup-session
    type: transcript
    path: /Users/kushagrachitkara/.codex/sessions/2026/06/09/rollout-2026-06-09T15-28-27-019eae80-59af-7060-b6de-e0f8d96d48ca.jsonl
    note: Codex session that ran `npx @dosu/cli setup --agent --tool codex`, checked whether setup wrote Codex MCP config, and concluded that the deployment still needed a connected source before retrieval worked.
  - id: dosu-codex-empty-deployment-session
    type: transcript
    path: /Users/kushagrachitkara/.codex/sessions/2026/06/09/rollout-2026-06-09T15-41-37-019eae8c-665b-7842-ac31-481c789a6451.jsonl
    note: Codex session that retried Dosu after authentication, confirmed the deployment had zero connected data sources, checked the public-library fallback for `codealmanac`, and rejected `generate_documentation` as ungrounded for AGENTS.md drafting.
status: active
verified: 2026-06-09
external_version: Public product pages reviewed on 2026-06-07; Dosu MCP and setup surfaces observed on 2026-06-09.
---

# Dosu

Dosu is a close competitive reference for CodeAlmanac's hosted and OSS directions. It is not a one-to-one clone of CodeAlmanac because it sells broader hosted knowledge infrastructure across repositories, docs, issues, pull requests, Slack, GitLab, MCP, and public Q&A surfaces. Its closest overlap is the claim that code changes should keep documentation and agent instructions current without relying on humans to remember a separate docs task. [@dosu-home] [@dosu-maintain-docs]

The product distinction is the canonical artifact. Dosu can maintain docs directly in repositories, but its product center is a hosted Dosu knowledge base, deployments, connected data sources, public spaces, response automation, review queues, and MCP access. CodeAlmanac's differentiator is that durable project memory is the repo-owned Almanac itself: pages, topics, wikilinks, sources, and Git-reviewed updates that local and hosted agents can inspect without treating a hosted knowledge base as canonical. [@dosu-home] [@dosu-response-automation] [@dosu-research-session]

## What Dosu Does

Dosu's maintain-docs workflow reviews pull-request code changes against published documentation and comments on the PR with relevant docs or update guidance. Its current docs say users publish documents from the dashboard, then Dosu checks whether a new PR is related to those published documents. The same page frames further automatic updates as an upcoming direction, while other Dosu product material describes self-documenting PRs and in-place doc sync as packaged features. [@dosu-maintain-docs] [@dosu-pricing]

Dosu's response automation answers questions in GitHub issues, GitHub discussions, pull-request comments, code-level PR review comments, GitLab merge requests, and Slack. It searches indexed code, documentation, past issues, discussions, pull requests, reviews, and internal knowledge bases, then writes cited answers through mention, auto-draft, or auto-reply modes. That makes Dosu an OSS support and engineering-support product, not only a documentation updater. [@dosu-response-automation]

Dosu's pricing page makes the OSS threat explicit. The free Explore tier includes self-documenting PRs, existing-doc sync, doc generation, MCP, public repositories, and limited usage. Its OSS maintainer plan adds issue labeling, deduplication, and public-space Q&A, while paid team and enterprise tiers add private repositories, SaaS integrations, analytics, SSO, custom RBAC, audit logs, and self-hosting only at enterprise scale. [@dosu-pricing]

Dosu also competes directly with agent-instruction maintenance. Its homepage says it can maintain `AGENTS.md`, `CLAUDE.md`, and skill definitions. Its May 2026 AGENTS.md post says Dosu watches pull requests, flags drift when code touches something described in agent documentation, and opens a suggested edit in the PR workflow. That overlaps CodeAlmanac's view that stale agent context damages future coding-agent work. [@dosu-home] [@dosu-agents-md-blog]

The confusing product detail is where updated documentation lives. Dosu's docs can mean Dosu-published documents, repository-backed documentation, or third-party documentation surfaces. The durable model from the research session is that Dosu indexes code and knowledge sources, decides which published docs a change affects, then delivers updates to the configured destination: a GitHub or GitLab pull request for repo-hosted docs, a direct update for Notion or Confluence-style docs, or a Dosu-hosted published document when the docs live inside Dosu. CodeAlmanac should preserve the opposite default: the Almanac root in Git is canonical, and hosted services index, render, and coordinate work around that root. [@dosu-maintain-docs] [@dosu-research-session]

## 2026-06-09 Empty-Deployment Experiments

The 2026-06-09 experiments tested Dosu as a possible way to draft project instructions and evaluate company-brain tooling. The durable lesson was not that Dosu failed; it was that the observed Dosu surface separates Codex MCP setup, deployment source connection, knowledge submission, curated retrieval, and public-library coverage for repositories that are not part of a connected deployment. [@dosu-experiment-session] [@dosu-codex-setup-session] [@dosu-codex-empty-deployment-session]

The first session asked Dosu to draft an `AGENTS.md` file for this repository, then narrowed into tool-surface exploration. The observed MCP calls were `search_documentation`, `init_knowledge`, and `save_topic`, all against an empty deployment. [@dosu-experiment-session]

`search_documentation` returned `No data sources found for this deployment`, and `init_knowledge` returned `No knowledge found`. In the tested state, Dosu could not retrieve or ground an `AGENTS.md` draft from project sources because there were no connected sources and no curated knowledge to search. [@dosu-experiment-session]

The later Codex session tested the local installation path instead of the hosted MCP calls. It ran `npx @dosu/cli setup --agent --tool codex`, hit a browser-auth requirement before setup completed, and then checked `~/.codex/config.toml`, which still had no `mcp_servers.dosu` block at that point. The only new local artifacts the session observed were Dosu CLI files under `~/.config/dosu-cli`. [@dosu-codex-setup-session]

A third Codex session retried the hosted MCP path after authentication. `init_knowledge` still returned `No knowledge found`, `list_available_data_sources` returned zero connected sources, and `find_public_library` returned no public result for `codealmanac`. The session therefore concluded that Dosu still could not ground an `AGENTS.md` draft from its own corpus. [@dosu-codex-empty-deployment-session]

## Observed Setup And Knowledge Boundaries

The Codex setup session showed that "connect Dosu to Codex" and "give Dosu project content" are different steps. The setup command prepared an authenticated MCP deployment path, but the follow-up conclusion was still that the deployment needed at least one connected source, such as the `codealmanac` GitHub repo, before `npx @dosu/cli ask "What does this project do?"` could return project knowledge. [@dosu-codex-setup-session]

The sessions did not observe any MCP tool for creating or connecting a data source. They only observed tools for reading existing sources or knowledge, for submitting knowledge-like content such as `save_topic`, and for preparing a Codex MCP connection that still depended on a separately populated deployment. The practical conclusion is that source connection was not available through the tested MCP surface. [@dosu-experiment-session] [@dosu-codex-setup-session]

The three sessions together established a hosted workflow with at least four distinct gates: authenticate or install the MCP connection, attach sources to the deployment, wait for retrievable knowledge to exist behind the search tools, and fall back to Dosu's public-library index only if the repository is actually covered there. The exact product surface for source attachment was only observed indirectly through empty-deployment failures and dashboard-oriented guidance, so future evaluation should still treat "dashboard-only source connection" as a working hypothesis until a post-auth CLI run or product doc confirms it. [@dosu-experiment-session] [@dosu-codex-setup-session] [@dosu-codex-empty-deployment-session]

The same third session clarified one tool-selection boundary. `generate_documentation` was not used because it publishes a background documentation page from connected data sources, and the deployment had no connected sources to ground a repo-specific `AGENTS.md` draft. The safe fallback in that state is direct repo inspection rather than asking Dosu to synthesize from an empty deployment. [@dosu-codex-empty-deployment-session]

`save_topic` returned `Topic saved.` for a CodeAlmanac architectural note, then an immediate `init_knowledge` call on the same subject still returned `No knowledge found`. The observed write-to-read path is therefore not synchronous. A saved topic did not become searchable curated knowledge immediately in the same session. [@dosu-experiment-session]

The strongest safe interpretation is that Dosu distinguishes submitted knowledge from retrievable curated knowledge. The session inferred a review or async indexing step, but only the delayed or gated read behavior was directly observed. [@dosu-experiment-session]

## Product Lesson

Dosu proves that "docs drift because code changes faster than documentation" is now a live product category. It also proves that "AI-maintained docs from PRs" is too broad for CodeAlmanac as a standalone pitch. Dosu already packages PR-time docs review, MCP context, public-repo OSS support, docs generation, hosted review, broad source ingestion, and agent-instruction maintenance in a polished buyer-facing lane. [@dosu-pricing] [@dosu-response-automation] [@dosu-agents-md-blog]

The useful lesson is not to copy Dosu's broad automation surface. CodeAlmanac should keep the narrower job: preserve governed engineering memory about why the code is shaped a certain way, then surface the relevant memory at issue, pull-request, and agent-task time. [[github-native-wiki-maintenance]] should therefore emphasize Almanac update PRs, check-run actions, and repo-owned memory diffs over hidden hosted docs, while [[open-source-almanac]] should emphasize maintainer attention and cited project context over generic auto-replies.

The 2026-06-09 experiments reinforced one CodeAlmanac product rule: when project instructions must be accurate to the current repository, direct inspection of the repository is more reliable than asking an empty or uncovered external knowledge base to synthesize them. Dosu's setup path can be smooth for installing a hosted MCP endpoint into an agent tool, but that convenience still leaves source attachment and knowledge population outside the repository. [@dosu-experiment-session] [@dosu-codex-setup-session] [@dosu-codex-empty-deployment-session]

Dosu also validates that OSS maintainers are a real go-to-market wedge. The risk is noise. Dosu's response modes, issue labeling, deduplication, and public-space Q&A show that public repositories can accept automation when it saves support time, but a CodeAlmanac bot must stay quieter than a general Q&A bot because its value is high-signal project memory, not omnipresent issue response. [@dosu-pricing] [@dosu-response-automation]

## Differentiation

The strongest CodeAlmanac contrast is not "Dosu does not write repo docs." Dosu does support repo-backed documentation workflows. The stronger contrast is that CodeAlmanac treats the repo-owned Almanac as the source of truth and treats hosted infrastructure as coordination around Git-reviewed wiki changes.

CodeAlmanac should describe the difference this way: Dosu keeps documentation and knowledge infrastructure fresh across work surfaces; CodeAlmanac preserves the repository's governed project memory and makes coding agents read it before changing the project. That distinction keeps CodeAlmanac out of broad support automation and preserves the [[company-brain]] boundary around codebase-specific memory.

The practical product consequence is that CodeAlmanac should learn from Dosu's activation loops while avoiding a hosted-knowledge-base center of gravity. First-index artifacts, freshness states, PR-time drift signals, suggested edits, and MCP or agent read surfaces are useful patterns. The canonical write path should remain ordinary Git diffs against an Almanac root, because inspectability and review are the trust boundary.

## Follow-Up Questions

The next meaningful Dosu checks are whether the CLI can connect sources directly after browser auth, whether a saved topic appears in a visible review queue, whether a direct document-write path becomes searchable faster than `save_topic`, and whether public-library coverage for a repo can be discovered anywhere other than `find_public_library`. Those questions were identified in the sessions but not yet verified. [@dosu-experiment-session] [@dosu-codex-setup-session] [@dosu-codex-empty-deployment-session]

## Related Pages

[[moxie-docs]] is the other close hosted codebase-documentation competitor. [[github-native-wiki-maintenance]] explains the hosted GitHub App loop that overlaps Dosu's PR-time docs checks and why CodeAlmanac keeps the canonical memory artifact in the repository even when remote automation is added later. [[open-source-almanac]] explains the OSS maintainer wedge where Dosu is already active. [[just-in-time-context-surfacing]] explains why CodeAlmanac must move from manual wiki search toward automatic cited context at work time. [[company-brain]] places Dosu in the broader hosted knowledge-infrastructure market.
