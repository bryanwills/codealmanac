---
title: GitHub-Native Wiki Maintenance
summary: >-
  GitHub-native wiki maintenance is the remote CodeAlmanac product thesis where hosted automation
  surfaces and updates repo-owned Almanac pages through normal GitHub workflows.
topics:
  - product-positioning
  - competitive-research
  - wiki-design
sources:
  - id: github-check-runs-api
    type: web
    url: https://docs.github.com/en/rest/checks/runs?apiVersion=2022-11-28
    retrieved_at: 2026-06-02T00:00:00.000Z
    note: >-
      Documents check-run output actions, their button labels, identifiers, descriptions, and the
      three-action limit for GitHub App check runs.
  - id: github-check-run-webhooks
    type: web
    url: >-
      https://docs.github.com/en/webhooks/webhook-events-and-payloads?actionType=requested_action#check_run
    retrieved_at: 2026-06-02T00:00:00.000Z
    note: >-
      Documents the check_run webhook and the Checks permission requirement for requested_action
      events.
  - id: yc-market-scan
    type: conversation
    path: >-
      /Users/rohan/.codex/sessions/2026/05/31/rollout-2026-05-31T23-31-46-019e8173-bc02-7503-a102-e9de99d6bb9c.jsonl
    note: >-
      Records the YC CLI market scan that refined the GitHub-native roadmap around PR context cards,
      maintainer notes, Almanac update PRs, session capture, repeated-answer detection, and agent
      read surfaces.
  - id: github-app-flow-session
    type: conversation
    path: >-
      /Users/rohan/.codex/sessions/2026/05/31/rollout-2026-05-31T23-31-46-019e8173-bc02-7503-a102-e9de99d6bb9c.jsonl
    note: >-
      Records the discussion that a real GitHub App needs a deployed webhook receiver and that a
      GitHub Action can prototype the loop before a hosted App validates paid team use.
  - id: almanac-update-pr-deploy-risk-session
    type: conversation
    path: >-
      /Users/rohan/.codex/sessions/2026/05/31/rollout-2026-05-31T23-31-46-019e8173-bc02-7503-a102-e9de99d6bb9c.jsonl
    note: >-
      Records the discussion that same-repo Almanac update PRs can trigger CI, preview deployments,
      branch protection, and merge-time deploy workflows unless repositories configure path filters
      or choose a lower-risk Almanac location.
  - id: same-pr-almanac-update-session
    type: conversation
    path: >-
      /Users/rohan/.codex/sessions/2026/05/31/rollout-2026-05-31T23-31-46-019e8173-bc02-7503-a102-e9de99d6bb9c.jsonl
    note: >-
      Records the decision that PR UI should say "Almanac update" rather than "memory update" and
      that Almanac can add wiki changes to the same pull request branch only when the author or
      maintainer approves or repo-visible auto-apply is enabled.
  - id: github-mcp-transport-session
    type: conversation
    path: >-
      /Users/rohan/.codex/sessions/2026/05/31/rollout-2026-05-31T23-31-46-019e8173-bc02-7503-a102-e9de99d6bb9c.jsonl
    note: >-
      Records the settled boundary that the GitHub App owns events, permissions, and publishing
      while GitHub MCP or native API wrappers are possible agent source-tool transports, with
      Daytona-like sandboxing belonging to hosted worker infrastructure.
  - id: github-mcp-deepwiki-answer
    type: conversation
    path: >-
      /Users/rohan/.codex/sessions/2026/05/31/rollout-2026-05-31T23-31-46-019e8173-bc02-7503-a102-e9de99d6bb9c.jsonl
    note: >-
      Records the DeepWiki answer that local or Docker `github/github-mcp-server` should accept
      GitHub App installation tokens through `GITHUB_PERSONAL_ACCESS_TOKEN`, with
      `GITHUB_TOOLSETS=pull_requests,repos,issues,actions` and `GITHUB_READ_ONLY=true`, while remote
      MCP remains less documented for installation-token use.
  - id: daytona-sandbox-session
    type: conversation
    path: >-
      /Users/rohan/.codex/sessions/2026/05/31/rollout-2026-05-31T23-31-46-019e8173-bc02-7503-a102-e9de99d6bb9c.jsonl
    note: >-
      Records the Daytona sandbox sketch for running one hosted Almanac pull-request job in an
      isolated checkout with GitHub App credentials, source tools, diff validation, optional
      same-branch publishing, and sandbox teardown.
  - id: hosted-agent-runner-session
    type: conversation
    path: >-
      /Users/rohan/.codex/sessions/2026/05/31/rollout-2026-05-31T23-31-46-019e8173-bc02-7503-a102-e9de99d6bb9c.jsonl
    note: >-
      Records the hosted-runner split where Python worker orchestration may run a controlled agent
      loop using CodeAlmanac prompts and conventions instead of depending on the local CodeAlmanac
      CLI or desktop coding-agent CLIs.
  - id: daytona-docs
    type: web
    url: https://www.daytona.io/docs/
    retrieved_at: 2026-06-02T00:00:00.000Z
    note: >-
      Documents Daytona sandboxes, SDK creation, process execution, filesystem operations, lifecycle
      management, and agent workflow positioning.
  - id: daytona-codex-sdk-guide
    type: web
    url: https://www.daytona.io/docs/en/guides/codex/codex-sdk-interactive-terminal-sandbox/
    retrieved_at: 2026-06-02T00:00:00.000Z
    note: Documents Daytona's pattern for running a Codex SDK coding agent workflow in a sandbox.
  - id: e2b-docs
    type: web
    url: https://www.e2b.dev/docs
    retrieved_at: 2026-06-02T00:00:00.000Z
    note: >-
      Documents E2B sandboxes, coding-agent use cases, GitHub Actions CI/CD use, commands,
      filesystem access, and agent-in-sandbox examples.
  - id: modal-sandboxes
    type: web
    url: https://modal.com/docs/guide/sandboxes
    retrieved_at: 2026-06-02T00:00:00.000Z
    note: >-
      Documents Modal Sandboxes as a substrate for running arbitrary or untrusted code in isolated
      environments.
  - id: modal-job-processing
    type: web
    url: https://modal.com/docs/guide/job-queue
    retrieved_at: 2026-06-02T00:00:00.000Z
    note: >-
      Documents Modal Functions as a scalable async job queue through deployed functions,
      `.spawn()`, polling, retries, timeouts, and concurrency controls.
  - id: hosted-github-app-runtime-session
    type: conversation
    path: >-
      /Users/rohan/.codex/sessions/2026/05/31/rollout-2026-05-31T23-31-46-019e8173-bc02-7503-a102-e9de99d6bb9c.jsonl
    note: >-
      Records the hosted GitHub App runtime discussion: usealmanac API, Postgres/Supabase, Doppler,
      Modal Function, Modal Sandbox, GitHub MCP or Octokit source tools, proposal storage as an
      approval-first option, diff validation, and same-PR publishing.
  - id: hosted-gh-cli-spike-session
    type: conversation
    path: >-
      /Users/rohan/.codex/sessions/2026/05/31/rollout-2026-05-31T23-31-46-019e8173-bc02-7503-a102-e9de99d6bb9c.jsonl
    note: >-
      Records the 2026-06-04 Modal spike decision to run Absorb with `gh` over a GitHub App
      installation token, use no pre-fetched source bundle beyond minimal run metadata, treat
      `connectors` as an inert legacy field for hosted GitHub, and prove GitHub permissions through
      explicit worker assertions.
  - id: hosted-github-direct-commit-session
    type: conversation
    path: >-
      /Users/rohan/.codex/sessions/2026/05/31/rollout-2026-05-31T23-31-46-019e8173-bc02-7503-a102-e9de99d6bb9c.jsonl
    note: >-
      Records the later critique that storing proposed same-PR diffs creates backend complexity, so
      the MVP should use GitHub as the diff and review surface and reserve proposal storage or
      pending branches for a later approval-first mode.
  - id: pr-evolution-session
    type: conversation
    path: >-
      /Users/rohan/.codex/sessions/2026/05/31/rollout-2026-05-31T23-31-46-019e8173-bc02-7503-a102-e9de99d6bb9c.jsonl
    note: >-
      Records the settled PR lifecycle model: one persistent Almanac thread or check per pull
      request, repeatable runs keyed to head SHAs, PR-level approval as ongoing permission for that
      PR, no draft noise before ready_for_review, and fork PRs handled through post-merge follow-up
      Almanac update PRs.
  - id: hosted-github-first-slice-session
    type: conversation
    path: >-
      /Users/rohan/.codex/sessions/2026/05/31/rollout-2026-05-31T23-31-46-019e8173-bc02-7503-a102-e9de99d6bb9c.jsonl
    note: >-
      Records the implementation sequencing decision that the first hosted slice should prove the
      GitHub App, Modal job, same-PR commit, check-run update, and Almanac-root diff validation loop
      with a fake Almanac change before adding an AI agent.
  - id: hosted-action-transport-session
    type: conversation
    path: >-
      /Users/rohan/.codex/sessions/2026/05/31/rollout-2026-05-31T23-31-46-019e8173-bc02-7503-a102-e9de99d6bb9c.jsonl
    note: >-
      Records the 2026-06-03 correction that v1 should not depend on @-mention comment commands or
      pretend issue comments have native action buttons; GitHub check-run actions are the clean
      action transport.
  - id: pr-surface-followup-session
    type: conversation
    path: >-
      /Users/rohan/.codex/sessions/2026/05/31/rollout-2026-05-31T23-31-46-019e8173-bc02-7503-a102-e9de99d6bb9c.jsonl
    note: >-
      Records the PR #12 follow-up that separated GitHub Actions CI checks from Almanac checks,
      found that the smoke PR did not prove a clean requested_action click path, and revised the
      product surface toward comments as the primary human thread with checks as lightweight status
      and action plumbing.
  - id: pr-ux-flow-session
    type: conversation
    path: >-
      /Users/rohan/.codex/sessions/2026/05/31/rollout-2026-05-31T23-31-46-019e8173-bc02-7503-a102-e9de99d6bb9c.jsonl
    note: >-
      Records the final PR UX flow: trusted same-repo PRs auto-update by default, one sticky Almanac
      comment explains state and changed pages, one Almanac check reports compact status and
      actions, ask mode waits for maintainer action, fork PRs wait for a follow-up path after merge,
      and the agent should write the complete comment markdown instead of the backend composing
      rationale objects.
  - id: hosted-backend-placement-session
    type: conversation
    path: >-
      /Users/rohan/.codex/sessions/2026/05/31/rollout-2026-05-31T23-31-46-019e8173-bc02-7503-a102-e9de99d6bb9c.jsonl
    note: >-
      Records the 2026-06-03 decision that hosted backend implementation belongs in usealmanac,
      should follow openalmanac backend organization patterns, and should treat almanac-backend as
      old-product history rather than the code home.
  - id: hosted-cloud-resource-session
    type: conversation
    path: >-
      /Users/rohan/.codex/sessions/2026/05/31/rollout-2026-05-31T23-31-46-019e8173-bc02-7503-a102-e9de99d6bb9c.jsonl
    note: >-
      Records the hosted deployment setup decisions around the codealmanac resource namespace,
      active Render and Supabase workspaces, region choice, Doppler config policy, and the Render
      service's failed first deploy against a main commit without backend/.
  - id: hosted-github-app-architecture-note
    type: file
    path: docs/plans/2026-06-02-hosted-github-app-architecture.md
    note: >-
      Captures the working hosted GitHub App architecture: usealmanac API, Postgres or Supabase,
      Modal job and sandbox, GitHub MCP or source tools, agent runtime, diff validation, and
      publisher flow.
  - id: hosted-requirements-log
    type: file
    path: docs/requirements_log.md
    note: >-
      Records settled requirements for hosted GitHub App language, PR modes, repo-owned Almanac
      updates, settings, worker model, GitHub access, secrets, platform direction, proposal
      lifecycle, and delivery abstraction.
  - id: pr-update-loop-plan
    type: conversation
    path: >-
      /Users/rohan/.codex/sessions/2026/05/31/rollout-2026-05-31T23-31-46-019e8173-bc02-7503-a102-e9de99d6bb9c.jsonl
    note: >-
      Records the final 2026-06-05 implementation plan for finishing the hosted PR update loop on
      `usealmanac` dev, including GitHub App JWT issuer configuration, durable update state,
      check-run actions, Modal invocation, real CodeAlmanac execution, delivery, fork handling,
      bot-loop prevention, tests, and live smoke gates.
  - id: pr-update-implementation-log
    type: manual
    note: >-
      Records the 2026-06-05 hosted PR update loop implementation decisions and verification results
      on the `usealmanac` dev branch; source path is
      /Users/rohan/Desktop/Projects/usealmanac-dev/docs/plans/2026-06-04-backend-architecture-refactor-log.md.
  - id: pr-update-live-smoke-runbook
    type: manual
    note: >-
      Defines the production-readiness smoke test for the hosted GitHub App PR update loop,
      including deploy preconditions, same-repo PR behavior, database checks, and rollback; source
      path is /Users/rohan/Desktop/Projects/usealmanac-dev/docs/runbooks/pr-update-live-smoke.md.
  - id: pr-update-production-smoke-session
    type: conversation
    path: >-
      /Users/rohan/.codex/sessions/2026/05/31/rollout-2026-05-31T23-31-46-019e8173-bc02-7503-a102-e9de99d6bb9c.jsonl
    note: >-
      Records the 2026-06-05 production smoke that retried the Almanac check after the model quota
      reset, fixed duplicate GitHub webhook delivery processing, redeployed Render at commit
      05ead0e, verified a same-repository Almanac bot commit on PR 12, later found that a terminal
      check attached to the pre-bot head SHA falls out of the current PR check summary, and
      clarified the check-run versus sticky-comment UI contract.
  - id: extensible-update-pipeline-design
    type: manual
    note: >-
      Records the future hosted update-pipeline shape, including Trigger -> Source -> Operation ->
      Policy -> Run -> Bundle -> Select -> Deliver, source-blind delivery strategies, and deferred
      settings/source-ref migrations; source path is
      /Users/rohan/Desktop/Projects/usealmanac-dev/docs/designs/2026-06-05-extensible-update-pipeline.md.
  - id: hosted-async-completion-session
    type: conversation
    path: >-
      /Users/rohan/.codex/sessions/2026/05/31/rollout-2026-05-31T23-31-46-019e8173-bc02-7503-a102-e9de99d6bb9c.jsonl
    note: >-
      Records the 2026-06-05 async-completion decision boundary for long-running Modal agent runs:
      webhook handlers must return quickly, Modal callback is the recommended v1 completion path,
      and backend polling remains a fallback.
  - id: hosted-callback-security-session
    type: conversation
    path: >-
      /Users/rohan/.codex/sessions/2026/05/31/rollout-2026-05-31T23-31-46-019e8173-bc02-7503-a102-e9de99d6bb9c.jsonl
    note: >-
      Records the 2026-06-05 hosted callback security decision to authenticate Modal completion with
      an internal shared-secret header, keep GitHub webhook authentication on GitHub HMAC
      signatures, and use a stale-run sweeper only as recovery.
  - id: hosted-manual-alignment-session
    type: conversation
    path: >-
      /Users/rohan/.codex/sessions/2026/05/31/rollout-2026-05-31T23-31-46-019e8173-bc02-7503-a102-e9de99d6bb9c.jsonl
    note: >-
      Records the 2026-06-05 architecture review after the production smoke: durable run rows must
      commit before Modal spawn, delivery execution must be source-blind after delivery selection,
      and those hosted-loop invariants belong in repo-specific manual doctrine rather than the
      universal manual.
  - id: hosted-terminal-race-hardening-session
    type: conversation
    path: >-
      /Users/rohan/.codex/sessions/2026/05/31/rollout-2026-05-31T23-31-46-019e8173-bc02-7503-a102-e9de99d6bb9c.jsonl
    note: >-
      Records the 2026-06-05 terminal-race hardening after review: Modal spawn recording must not
      regress terminal runs, must still persist the Modal call id, and must suppress stale duplicate
      check publication when completion wins before the original webhook records a check id.
  - id: hosted-settings-session
    type: conversation
    path: >-
      /Users/rohan/.codex/sessions/2026/05/31/rollout-2026-05-31T23-31-46-019e8173-bc02-7503-a102-e9de99d6bb9c.jsonl
    note: >-
      Records the v1 settings decision that hosted dashboard or database settings, not repo
      configuration, own GitHub App behavior; new installs default to ask on future triggers without
      backfilling existing pull requests.
  - id: hosted-authorization-session
    type: conversation
    path: >-
      /Users/rohan/.codex/sessions/2026/05/31/rollout-2026-05-31T23-31-46-019e8173-bc02-7503-a102-e9de99d6bb9c.jsonl
    note: >-
      Records the hosted GitHub App authorization decision: centralize server-side authorization as
      a v1 RBAC/ABAC service backed by GitHub repository permissions and defer OPA, Cedar, or
      OpenFGA until org policy complexity appears.
  - id: hosted-pr-rerun-session
    type: conversation
    path: >-
      /Users/rohan/.codex/sessions/2026/05/31/rollout-2026-05-31T23-31-46-019e8173-bc02-7503-a102-e9de99d6bb9c.jsonl
    note: >-
      Records the v1 decision that approving Almanac on one pull request grants ongoing permission
      for that pull request, with reruns triggered by new commits, submitted reviews, and review
      comments rather than every issue comment.
  - id: github-app-registration-session
    type: conversation
    path: >-
      /Users/rohan/.codex/sessions/2026/05/31/rollout-2026-05-31T23-31-46-019e8173-bc02-7503-a102-e9de99d6bb9c.jsonl
    note: >-
      Records the 2026-06-03 GitHub App registration choices for Almanac Bot: installation auth
      only, `Any account` install location, v1 repository permissions, selected webhook events,
      Doppler secret storage, and the final `github_app:true` production health check.
  - id: hosted-backend-service-boundary-session
    type: conversation
    path: >-
      /Users/rohan/.codex/sessions/2026/05/31/rollout-2026-05-31T23-31-46-019e8173-bc02-7503-a102-e9de99d6bb9c.jsonl
    note: >-
      Records the 2026-06-05 backend structure discussion after the first webhook slice, including
      the decision to copy OpenAlmanac backend principles, use thin routes and an Almanac facade,
      keep schemas/models near owning services, and make updates the product lifecycle service.
  - id: hosted-dashboard-review-session
    type: conversation
    path: >-
      /Users/rohan/.codex/sessions/2026/05/31/rollout-2026-05-31T23-31-46-019e8173-bc02-7503-a102-e9de99d6bb9c.jsonl
    note: >-
      Records the 2026-06-06 hosted dashboard architecture review: GitHub remains the PR-time action
      surface, the dashboard is a BFF for settings, observability, wiki browsing, account/repo
      management, and billing, tenant identity is GitHub App installation, authorization stays
      separate from billing entitlement, current auto mode updates PR branches rather than merge
      events, OAuth sessions should use opaque cookies with server-side encrypted tokens, and Autumn
      billing should be a seam unless charging is imminent.
  - id: hosted-dashboard-auth-session
    type: conversation
    path: >-
      /Users/rohan/.codex/sessions/2026/05/31/rollout-2026-05-31T23-31-46-019e8173-bc02-7503-a102-e9de99d6bb9c.jsonl
    note: >-
      Records the 2026-06-06 dashboard-auth decision: depend on Supabase Auth for frontend and
      backend dashboard identity/session, use GitHub OAuth through Supabase for v1 login, keep
      GitHub App installation tokens for repository automation and wiki reads, and require signed-in
      user permission checks before serving private wiki content.
  - id: hosted-dashboard-wiki-ref-session
    type: conversation
    path: >-
      /Users/rohan/.codex/sessions/2026/05/31/rollout-2026-05-31T23-31-46-019e8173-bc02-7503-a102-e9de99d6bb9c.jsonl
    note: >-
      Records the 2026-06-06 dashboard wiki-reader terminology decision: wiki reads are
      Git-ref-aware, `ref` names default, pull-request, or branch versions of the Almanac, and
      `source` remains reserved for raw material the agent learns from.
  - id: hosted-dashboard-wiki-reader-review-session
    type: conversation
    path: >-
      /Users/rohan/.codex/sessions/2026/05/31/rollout-2026-05-31T23-31-46-019e8173-bc02-7503-a102-e9de99d6bb9c.jsonl
    note: >-
      Records the late 2026-06-06 focused review finding that dashboard wiki listing may treat a
      missing `.almanac/pages` directory as an empty wiki, but must not convert upstream GitHub
      integration failures into successful empty wiki responses.
  - id: hosted-dashboard-identity-access-session
    type: conversation
    path: >-
      /Users/rohan/.codex/sessions/2026/05/31/rollout-2026-05-31T23-31-46-019e8173-bc02-7503-a102-e9de99d6bb9c.jsonl
    note: >-
      Records the 2026-06-06 service-boundary and security discussion that dashboard identity
      authenticates Supabase users, accounts resolves linked provider identities, repository action
      checks remain a separate access service, user-editable metadata must not become authorization
      input, authorization-bearing GitHub identity should be captured from trusted Supabase
      identities or app metadata into product-owned verified link state, and GitHub permission
      checks need a short cache.
  - id: hosted-dashboard-identity-minimal-session
    type: conversation
    path: >-
      /Users/rohan/.codex/sessions/2026/05/31/rollout-2026-05-31T23-31-46-019e8173-bc02-7503-a102-e9de99d6bb9c.jsonl
    note: >-
      Records the 2026-06-06 minimal identity-model decision: Supabase identities and GitHub remain
      the source of truth for external account facts, so v1 should not create GitHubAccountSnapshot,
      ConnectedIdentity, DashboardUser, DashboardUserAuth, DashboardUserRecord, or a local users
      table without a concrete product-owned need.
  - id: hosted-update-outcome-publication-session
    type: conversation
    path: >-
      /Users/rohan/.codex/sessions/2026/05/31/rollout-2026-05-31T23-31-46-019e8173-bc02-7503-a102-e9de99d6bb9c.jsonl
    note: >-
      Records the 2026-06-06 service-boundary correction that publishing update outcomes to GitHub
      checks should be `GitHubAppService.publish_update_check(...)`, with `UpdatesService` wired
      into `GitHubAppService` through the `Almanac` composition root, not a vague top-level Almanac
      facade method or a new orchestration service.
  - id: supabase-github-auth-docs
    type: web
    url: https://supabase.com/docs/guides/auth/social-login/auth-github
    retrieved_at: 2026-06-06T00:00:00.000Z
    note: >-
      Documents Supabase Auth GitHub login through a GitHub OAuth App, GitHub OAuth credentials in
      Supabase, `signInWithOAuth({ provider: "github" })`, and SSR callback code exchange.
  - id: supabase-provider-token-docs
    type: web
    url: https://supabase.com/docs/guides/auth/social-login
    retrieved_at: 2026-06-06T00:00:00.000Z
    note: >-
      Documents provider token behavior: applications can use provider tokens for OAuth-provider API
      calls, Supabase does not refresh those tokens, and provider tokens are intentionally not
      stored in the project database.
  - id: hosted-almanac-updates-design
    type: manual
    note: >-
      Design note at
      /Users/rohan/Desktop/Projects/usealmanac/docs/designs/2026-06-04-almanac-updates-service.md
      records the hosted update-service structure, typed trigger boundary, main webhook and approval
      flows, state model, and boundary rules for the usealmanac backend; the later service-boundary
      session finalized the folder name as services/updates.
  - id: github-mcp-host-integration
    type: web
    url: https://github.com/github/github-mcp-server/blob/main/docs/host-integration.md
    retrieved_at: 2026-06-02T00:00:00.000Z
    note: >-
      Documents local and remote GitHub MCP authentication, including the requirement for a valid
      access token and OAuth as the recommended remote flow.
  - id: github-mcp-policies
    type: web
    url: https://github.com/github/github-mcp-server/blob/main/docs/policies-and-governance.md
    retrieved_at: 2026-06-02T00:00:00.000Z
    note: >-
      Documents GitHub MCP deployment modes, enterprise controls, PATs, OAuth, and GitHub App
      installation-token governance.
  - id: github-app-installation-auth
    type: web
    url: >-
      https://docs.github.com/en/enterprise-cloud@latest/apps/creating-github-apps/authenticating-with-a-github-app/authenticating-as-a-github-app-installation
    retrieved_at: 2026-06-02T00:00:00.000Z
    note: >-
      Documents GitHub App installation access tokens, one-hour expiry, REST/GraphQL use, Git clone
      use through Contents permission, and Octokit.js installation authentication.
  - id: github-com
    type: web
    url: https://docs.coderabbit.ai/platforms/github-com
    note: Migrated from legacy sources.
  - id: knowledge-base
    type: web
    url: https://docs.coderabbit.ai/knowledge-base
    note: Migrated from legacy sources.
  - id: introduction
    type: web
    url: https://www.greptile.com/docs/introduction
    note: Migrated from legacy sources.
  - id: graph-based-codebase-context
    type: web
    url: https://www.greptile.com/docs/how-greptile-works/graph-based-codebase-context
    note: Migrated from legacy sources.
  - id: how-it-works
    type: web
    url: https://supermemory.ai/docs/concepts/how-it-works
    note: Migrated from legacy sources.
  - id: webhook-events-and-payloads
    type: web
    url: https://docs.github.com/en/webhooks/webhook-events-and-payloads
    note: Migrated from legacy sources.
  - id: pulls
    type: web
    url: https://docs.github.com/en/rest/pulls/pulls
    note: Migrated from legacy sources.
  - id: contents
    type: web
    url: https://docs.github.com/en/rest/repos/contents
    note: Migrated from legacy sources.
  - id: settings
    type: web
    url: https://www.mintlify.com/docs/organize/settings
    note: Migrated from legacy sources.
  - id: github
    type: web
    url: https://www.mintlify.com/docs/deploy/github
    note: Migrated from legacy sources.
  - id: preview-deployments
    type: web
    url: https://www.mintlify.com/docs/deploy/preview-deployments
    note: Migrated from legacy sources.
  - id: remote-product-session
    type: conversation
    path: /Users/rohan/.codex/sessions/2026/05/28/rollout-2026-05-28T18-24-15-019e70e7-1dc0-7e30-a996-f47b766b4ee6.jsonl
    note: Records the 2026-05-28 remote CodeAlmanac product research session that examined GitHub-native wiki maintenance, open-source codebase wiki tools, and the hosted product boundary.
  - id: oss-wiki-tools-research
    type: file
    path: docs/research/2026-05-28-open-source-codebase-wiki-and-review-tools.md
    note: Records the 2026-05-28 survey of open-source codebase wiki and review tools that informed the GitHub-native maintenance direction.
  - id: github-context-connectors-research
    type: file
    path: docs/research/2026-05-29-github-context-connectors.md
    note: Records the 2026-05-29 research into GitHub context connector patterns relevant to the remote CodeAlmanac product design.
  - id: remote-product-concept
    type: file
    path: docs/strategy/2026-05-28-remote-codealmanac-product-concept.md
    note: Documents the 2026-05-28 remote CodeAlmanac product concept that defines the hosted product boundary and GitHub-native wiki maintenance loop.
  - id: oss-almanac-concept
    type: file
    path: docs/strategy/2026-05-29-open-source-almanac-concept.md
    note: Documents the 2026-05-29 open-source Almanac concept that shapes the free-public-repo product direction distinct from the hosted GitHub App.
  - id: sdk-integration-session
    type: conversation
    path: /Users/rohan/.codex/sessions/2026/05/28/rollout-2026-05-28T18-27-05-019e70e9-b7d7-7900-9fc0-da2a6f0b532d.jsonl
    note: Records the 2026-05-28 session covering Claude Agent SDK integration and its relationship to the hosted worker architecture for GitHub-native Almanac updates.
status: active
verified: 2026-06-06T00:00:00.000Z

---

# GitHub-Native Wiki Maintenance

GitHub-native wiki maintenance is the remote CodeAlmanac product direction that keeps the repository as the canonical Almanac artifact while using hosted infrastructure for GitHub event handling, indexing, checks, comments, scheduled maintenance, and Almanac update pull requests. The durable product boundary is that the hosted service can compute, cache, search, and propose, but durable project knowledge lands as reviewed markdown changes in the repository.

The 2026-05-28 remote-product research session clarified the distinction from hosted memory products. A remote CodeAlmanac should not be a hosted replacement for repo-owned Almanac pages, because that would weaken the branch, review, provenance, blame, rollback, and local-agent trust boundary that makes CodeAlmanac different from broad memory layers such as [[codex-supermemory]] and company-brain products discussed in [[company-brain]].

The same session tested and rejected a required `ALMANAC.md` file or top-level `almanac/` directory. Those options add a new repo-root concept, compete with existing docs surfaces, and make adoption feel more invasive for maintainers. The later directory discussion made `docs/almanac/` the preferred public/team knowledge root because it reads as project documentation without adding a branded root directory. `.almanac/` remains the quiet local/private profile. The durable rule is that the Almanac root contains reviewable project memory only; generated indexes, run history, extracts, caches, and hosted job state should live in user cache directories or hosted coordination storage by default.

## Competitive Lesson

CodeRabbit and Greptile validate GitHub as the workflow surface for AI coding teams. CodeRabbit's GitHub installation requests selected repository access and repository permissions for review-oriented work, and its knowledge base combines team learnings, code guidelines, multi-repo context, MCP servers, web search, linked issues, and past pull requests. Greptile describes itself as an AI code review agent that installs as a GitHub or GitLab app, builds a repository graph, reviews pull requests automatically, posts PR comments, and learns from team reactions and replies over time.

The CodeAlmanac lane is different. CodeRabbit and Greptile use memory to review code; CodeAlmanac should maintain the memory that future agents and reviewers use before changing code. Competing as another general PR reviewer would put CodeAlmanac against products whose core surface is bug-finding, summaries, inline comments, and fix suggestions. Competing as repo-governed project memory keeps the product centered on decisions, invariants, flows, gotchas, architecture views, and source-backed synthesis.

Supermemory illustrates the hosted-memory alternative. Its public docs describe raw documents becoming dynamically connected memories through extraction, chunking, embedding, indexing, update relationships, extension relationships, and derived memories. That model is useful for cross-tool recall, but it is not branch-scoped Git memory. CodeAlmanac should treat hosted memory systems as adjacent infrastructure and possible source adapters, not as the canonical store for codebase knowledge.

The 2026-05-31 YC CLI market scan added a sharper incumbent lesson: the everyday competitor is not only venture-backed codebase-context software, but also `CLAUDE.md`, `AGENTS.md`, `.cursorrules`, README files, and copied prompt context. Those files are cheap, visible, and already part of agent workflows. Almanac for GitHub must therefore prove that reviewed pages, file-aware retrieval, and Almanac update PRs reduce repeated explanation enough to justify more structure than a single prompt file. [@yc-market-scan]

## GitHub Shape

A remote CodeAlmanac should be a GitHub App before it is a GitHub Action. GitHub App webhooks give event-driven access to `pull_request`, `pull_request_review`, `pull_request_review_comment`, `issue_comment`, `push`, and related events, and GitHub's docs require at least read-level pull request permission for pull request webhook subscriptions.

The permission model should have tiers:

- **Read mode** reads `.almanac/`, repository contents, pull request diffs, issues, and metadata so it can surface relevant pages and detect missing context.
- **Comment/check mode** adds pull request or check permissions so it can post one compact PR comment or status when wiki context matters.
- **Maintenance mode** adds contents write and pull request write so it can push a branch that edits the repo-owned Almanac directory and open a normal Almanac update PR.

GitHub's REST docs make this boundary concrete. Reading repository contents requires `Contents: read`, creating or updating file contents requires `Contents: write`, listing pull request files requires `Pull requests: read`, and creating a pull request requires `Pull requests: write`. Those permissions map directly to CodeAlmanac's trust tiers.

The GitHub App is the control plane, not just another source connector. It receives webhooks, identifies the installation, mints installation tokens, enforces repository permissions, owns checks and comments, and publishes commits or Almanac update PRs. GitHub source tools are a separate agent read surface for pull requests, diffs, commits, comments, reviews, linked issues, and repository search. The official `github/github-mcp-server` can fit as that read surface, but it should be treated as one possible transport behind a source connector contract rather than the core hosted path until permission scoping, write-tool suppression, audit logging, and hosted-agent MCP reliability are proven. [@github-mcp-transport-session]

The registered v1 app is Almanac Bot. The setup intentionally left user OAuth off: no callback URL, no expiring user authorization tokens, no "request user authorization during installation", and no device flow. Installation authentication is enough for the first GitHub App slice because the App acts on repositories through installation tokens rather than user OAuth tokens. The app was configured for `Any account` installation so it can be installed on `AlmanacCode` organization repositories instead of only `@rohans0509` repositories. [@github-app-registration-session]

The v1 repository permissions are `Checks: Read and write`, `Commit statuses: Read and write`, `Contents: Read and write`, `Issues: Read and write`, `Metadata: Read-only`, and `Pull requests: Read and write`, with `Discussions: Read-only` and `Actions: Read-only` accepted as useful optional permissions. The v1 subscribed events are `Check run`, `Issue comment`, `Issues`, `Pull request`, `Pull request review`, `Pull request review comment`, `Pull request review thread`, `Installation target`, and `Repository`. The setup explicitly skipped push and broad repository activity events for v1 because `pull_request.synchronize` already fires when PR branch commits change and push events would add noise before the PR-centered loop is proven. [@github-app-registration-session]

The hosted GitHub client should keep both the numeric GitHub App ID and the Client ID in configuration. The app ID remains useful for display, storage, and installation context, but the JWT issuer should prefer the GitHub App Client ID when it is available and fall back to the numeric App ID only when no Client ID is configured. The 2026-06-05 implementation plan records that numeric App ID issuer was rejected during the current app flow while Client ID `Iv23lip5I92lhXZPzAs2` worked, so production token minting should make the issuer rule explicit and tested. [@pr-update-loop-plan]

The GitHub MCP token question should be split by deployment mode. Official remote GitHub MCP is risky for v1 because the docs mostly frame remote auth around OAuth or PATs and a reported installation-token attempt worked against GitHub REST while failing against the remote MCP endpoint. Local or Docker GitHub MCP is still viable as a source-tool transport: the DeepWiki answer for `github/github-mcp-server` said an installation token can be supplied as `GITHUB_PERSONAL_ACCESS_TOKEN`, with `GITHUB_TOOLSETS=pull_requests,repos,issues,actions` and `GITHUB_READ_ONLY=true`; GitHub API permissions remain enforced by the App installation because installation tokens do not expose ordinary OAuth scope headers. The operational risk is the one-hour installation-token lifetime, so a worker should mint a fresh token before starting MCP and be prepared to restart the server after a 401. Octokit-backed native tools remain the fallback if local MCP rejects installation tokens, cannot expose the required pull-request material, or makes audit and write-tool suppression harder than native API wrappers. [@github-mcp-host-integration] [@github-mcp-policies] [@github-mcp-transport-session] [@github-mcp-deepwiki-answer]

## Product Loop

The remote product should make local wiki knowledge available at the moments when teams already review change:

1. On PR open or update, register source handles for the pull request, diff or commit range, review thread, linked issues, changed files, and target-branch Almanac root.
2. Run a small review-note agent with source and wiki tools when the repository has enabled PR-time notes.
3. Post a short "Almanac context for this PR" comment only when the agent can cite existing Almanac pages or explicit source material that changes review behavior.
4. After merge, run Absorb or Garden with source handles for the merged diff, PR discussion, issues, reviews, and branch wiki.
5. Open a separate Almanac update PR when durable knowledge changed.
6. Keep quiet when no useful wiki action exists.

The highest-value checks are not generic code review comments. They are docs-drift checks, invariant conflicts, missing decision or flow updates, stale pages, broken file references, and "this change deserves an Almanac update" signals. That keeps the product aligned with [[just-in-time-context-surfacing]]: a few cited constraints at action time, not broad context injection.

The concrete product name for this loop is Almanac for GitHub. Its durable units are Context Cards, Almanac update PRs, Decision Capture, and Almanac Queue. Context Cards are compact issue or pull-request comments that cite existing Almanac pages when the page would reduce maintainer repetition or contributor confusion. Almanac update PRs are ordinary GitHub pull requests that change the repo-owned Almanac after a merge, review discussion, or maintainer decision creates reusable project memory. Decision Capture is the event detector that turns a maintainer statement such as "do not support this flag because it conflicts with workspace-local config" into a proposed page update instead of letting the rationale remain buried in review comments. Almanac Queue is the hosted workflow surface that shows pending capture candidates, Almanac update PRs that need review, and pages or areas that need an owner.

The YC market scan condensed the first product sequence to six units: PR Context Cards, `/almanac note`, Almanac update PRs, AI session capture, repeated-answer detection for maintainers, and an MCP or agent read surface. That sequence keeps the first wedge near GitHub and coding agents while deferring enterprise connectors, dashboards, permissions, and broad company-search features until the Almanac loop proves value. [@yc-market-scan]

GitHub ingestion should not copy the local transcript-capture scheduler model. Local capture uses periodic quiet-window sweeps because Claude, Codex, and Cursor do not share one reliable session-end event. GitHub already has explicit lifecycle events, so pull requests, issues, labels, reviews, maintainer comments, releases, and pushes should enqueue source-event records directly. Periodic jobs should be reconciliation and cleanup for missed webhooks, stale pages, and slow Garden work, not the primary way fresh GitHub activity enters the system.

The clean architecture is event-driven enqueue plus per-wiki single-writer execution plus periodic reconciliation. A GitHub event becomes a cheap classified source-event record, then an [[evidence-bundles|evidence bundle]] that names available source handles, then a queued Absorb or Garden job with source tools, then an Almanac update PR when durable wiki source changes. Issues and pull requests remain evidence; they should not directly become wiki pages. The page should preserve the distilled invariant, decision, flow, or maintenance rule, while the GitHub object becomes a source.

The hosted app should expose product navigation around the work it performs: Overview, Pages, Topics, Files, Issues and PRs, Decisions, Maintainers, Queue, and Settings. Queue is the paid-product surface because it turns Almanac maintenance from a hidden background job into governed work: "needs capture" items from PRs or issues, "needs review" Almanac update PRs, and "needs owner" pages whose stewardship is unclear.

## Trigger Policy

The v1 trigger policy should group GitHub events by product intent, not by whether a webhook exists. Pull request activity before merge is a read-heavy context path: `pull_request.opened`, `pull_request.synchronize`, `pull_request.reopened`, and `pull_request.ready_for_review` should read the target branch Almanac, inspect the proposed diff, and optionally post one Context Card or status check. They should not normally open an Almanac update PR because the code is still provisional.

Pull request review events are decision evidence. `pull_request_review.submitted`, `pull_request_review_comment.created`, and `issue_comment.created` on a pull request can record maintainer rationale, repeated explanations, or missing-memory candidates. They should usually create queue evidence rather than immediately edit the wiki, because review threads often change before merge.

The main write trigger is `pull_request.closed` with `merged == true`. That event has a stable base branch, merged diff, discussion, review history, linked issues, and changed files. Almanac should run Absorb for the branch that received the merge and open an Almanac update PR back to that same branch only when durable project memory changed.

Pushes to maintained branches are reconciliation triggers. They catch direct commits, missed PR webhooks, and branch merges that do not provide enough pull-request context, but they should be conservative and dedupe against existing source identities such as PR number, merge commit SHA, changed file fingerprints, and wiki source entries.

Issue events are candidate triggers. `issues.opened`, `issues.edited`, and `issues.labeled` can surface existing context or create evidence candidates; `issues.closed` can become durable memory when the close reason contains a maintainer decision or when a linked pull request fixed a recurring project pattern. Most issues should not create wiki pages directly because issues are noisy source material rather than maintained synthesis.

Release events are version-memory triggers. `release.published` can update support, upgrade, compatibility, or release-behavior pages when the release changes durable project facts. It should target the release branch or default branch according to the repository's maintained-branch configuration.

Periodic jobs are cleanup and reconciliation, not primary ingestion. Weekly or scheduled work should handle missed webhooks, stale pages, broken references, slow Garden cleanup, queue health, and backlog compaction. GitHub activity already has explicit lifecycle events, so a hosted GitHub product should not depend on time-based polling for fresh pull requests and issues.

## End-to-End GitHub Flow

The exact hosted flow starts with installation, not with a hidden memory database. A maintainer installs the Almanac GitHub App on selected repositories, chooses an Almanac root such as `docs/almanac/` or `.almanac/`, and grants only the permissions needed for the selected mode. The repository remains the canonical store for pages, topics, config, and issue policy; hosted storage keeps webhook deliveries, queue items, source fingerprints, rendered indexes, run logs, billing settings, and other coordination state.

The 2026-05-31 GitHub App discussion made deployment a hard boundary: a real GitHub App needs a public HTTPS webhook receiver. GitHub sends events to Almanac, a hosted API verifies signatures and installation state, a queue records the job, a worker checks out the repository or pull request context, Almanac decides whether wiki context or an update is useful, and the App posts comments, checks, or Almanac update PRs back to GitHub. The CodeRabbit flow research in that discussion supports a narrower Almanac MVP: subscribe to pull request and comment events, run on `pull_request.closed` with `merged: true`, and open a separate Almanac update PR only when durable project memory changed. A GitHub Action-only prototype can avoid an always-on service, but it pushes setup friction, secrets, timing, and failure handling onto the repository. [@github-app-flow-session]

Hosted Absorb needs five runtime inputs after a GitHub trigger: a GitHub App installation token, a repository checkout or sandbox for the target branch, Almanac-controlled agent-provider credentials, an operation brief that names the source event, and queue/run state for dedupe, logs, status, and output publishing. The installation token is the GitHub access path. Composio is not part of the core GitHub path unless the operation also needs a secondary system referenced by the GitHub source.

Human and bot edits converge through Git. A maintainer can edit an Almanac page directly, a contributor can include an Almanac update in a feature pull request, and the Almanac App can open an Almanac update PR after it detects durable knowledge. All three paths produce ordinary branches and pull requests against the repository's Almanac root. GitHub review, CODEOWNERS, merge rules, blame, rollback, and branch history remain the trust boundary.

Same-PR wiki updates are a separate write mode from follow-up Almanac update PRs. The earlier approval-first design had the App compute a proposed Almanac diff, store it in hosted job state, show `Update this PR`, `Ignore`, and `Always update automatically`, and commit the stored Almanac-root changes only after a user action or explicit auto-apply rule. That interaction is clean for trust, but it requires proposal artifacts, diff rendering, staleness checks, apply logic, and hosted state that GitHub already handles for ordinary branch changes. [@same-pr-almanac-update-session] [@hosted-github-direct-commit-session]

The MVP should avoid a custom proposal and diff storage system. The simpler Git-native mode is that Almanac asks for permission through the pull request surface, then analyzes the pull request, commits Almanac-root changes directly to the same pull-request branch, posts a comment explaining what changed, and lets reviewers inspect, edit, keep, or remove the bot commit through the normal GitHub pull-request diff. Same-repository pull requests have exactly three v1 repository modes: `ask`, `auto`, and `disabled`. [@hosted-github-direct-commit-session] [@hosted-settings-session]

Direct same-branch commits work best for internal branches, small teams, trusted bot permissions, and teams already accustomed to bots such as CodeRabbit, Copilot, Renovate, or Dependabot mutating pull-request branches. They are risky for forked OSS pull requests, first-time contributors, security-sensitive repositories, strict branch-ownership cultures, large pull requests where wiki diffs distract from code review, and repositories where bot commits trigger expensive CI or deployment workflows. That risk keeps auto-commit an opt-in workflow rule rather than the default for public or untrusted contribution paths. [@same-pr-almanac-update-session] [@hosted-github-direct-commit-session]

The PR-time UI should be one persistent Almanac surface per pull request, not a new comment on every push. The v1 action surface should be a GitHub check run, because issue comments do not have native action buttons and the project does not want an `@usealmanac update` command flow for the first product slice. A PR comment can still mirror status or summarize a completed update, but the action identifiers, clicked actor, and authorization handoff should come from check-run actions. The stored state should include the pull request number, current head SHA, last prompted head SHA, last run head SHA, last Almanac commit SHA, check-run identifier, optional comment identifier, and status, so the same GitHub surface can be updated in place as the pull request evolves. `Update this PR` should mean ongoing approval for that pull request: run now, keep watching new commits, comments, and reviews, and rerun until the pull request is merged, closed, or explicitly stopped. A separate `Auto-update this PR` action is confusing because the user's intent is "use Almanac on this PR," not "run once and stop." `Always update in this repo` is the broader convenience action; it sets the default for future pull requests in the repository. [@pr-evolution-session] [@hosted-action-transport-session]

Draft pull requests should stay silent until GitHub sends `pull_request.ready_for_review`, because a draft usually means the author is still exploring. Fork pull requests are common in public OSS and should not be mutated by default. The preferred future safe OSS path is to show after-merge actions, wait for merge, and open a follow-up Almanac update PR against the upstream repository's maintained branch when the maintainer opted in for that pull request or repository. V1 must not expose those controls until follow-up delivery exists, because a visible fork prompt or waiting-for-merge state would promise an unimplemented publisher path. [@pr-evolution-session] [@pr-update-implementation-log]

GitHub check runs are the preferred v1 UI for this because check-run output actions render as user-triggered buttons with labels, identifiers, descriptions, and a maximum of three actions. A clicked action arrives through the `check_run` webhook with the `requested_action` action type, and receiving that action requires write-level Checks permission for the GitHub App. That maps cleanly to `Update this PR`, `Skip this PR`, and `Always update in this repo` without inventing signed comment links, OAuth-backed comment buttons, or slash-command parsing. [@github-check-runs-api] [@github-check-run-webhooks] [@pr-evolution-session] [@hosted-action-transport-session]

An approval-first same-PR mode still has a coherent future shape. It should use two hosted jobs rather than holding one sandbox open while the user decides. The analysis job would receive the pull-request event, clone or check out the branch, read repository and GitHub source context, ask the agent for proposed Almanac-root changes, store the proposal with the pull request head SHA, and render the check or comment from that stored proposal. The apply job would start only after `Update this PR` or an explicit auto-apply rule: it reloads the proposal, verifies that the current pull request head SHA still matches, checks out a fresh copy of the branch, applies the stored changes, validates that only the configured Almanac root changed, commits, and pushes to the pull-request branch. That design is later-product complexity, not the lowest-complexity MVP. [@hosted-github-app-runtime-session] [@hosted-github-direct-commit-session]

For a pull request, the App receives `pull_request` and review events, records a source-event row, registers source handles, and may run a review-note agent with repo and source tools. That PR-time path is read-heavy and should stay quiet unless the agent can cite memory or explicit source material that would change review behavior or reduce maintainer repetition.

After a pull request merges, the App receives the merge or push event, registers source handles for the merged diff, commits, PR body, reviews, comments, linked issues, changed files, and target-branch Almanac root, then enqueues one Absorb run for that repository. The per-wiki single-writer queue is still the execution boundary: hosted workers can process many repositories at once, but only one write-capable Almanac run should edit a given repository's Almanac root at a time.

The worker clones or checks out the repository, runs the Almanac engine against the evidence bundle, and leaves the working tree unchanged when no durable project memory changed. When pages, topics, or policy files change, the worker pushes a branch such as `almanac/update-gateway-auth-almanac` and opens an Almanac update PR. The Almanac update PR body should cite the GitHub sources that caused the update and summarize the page changes, but the durable output is still markdown in the repo-owned Almanac root.

Once maintainers merge the Almanac update PR, the target branch contains the updated canonical wiki for that branch. The hosted viewer and connector then reindex from the merged repository state. If maintainers reject or edit the Almanac update PR, that Git outcome is the source of truth; hosted state should follow the repository instead of preserving a conflicting private memory record.

Periodic jobs are secondary in this flow. They reconcile missed webhooks, find stale pages, check dead references, batch slow Garden work, and surface queue health. They should not be the primary discovery mechanism for GitHub activity because GitHub already emits explicit events for pull requests, issues, comments, labels, releases, and pushes.

The same operation model should also work without the hosted App. In local mode, a maintainer can run an explicit command against a pull request, issue, or git range using the current checkout plus a user GitHub token; in GitHub Action mode, the workflow checkout and action token provide the runtime; in hosted mode, Almanac Cloud uses a sandbox or worktree and GitHub App credentials. The product boundary is not "local engine versus cloud engine." The stable boundary is a source connector plus evidence bundle plus operation runtime plus publisher, with each runtime supplying the repo checkout and credentials differently.

The first hosted implementation should separate a small onboarding and settings app from the worker path. The minimum hosted architecture is a web or API surface for GitHub App installation, webhook receipt, signature verification, and repository settings; a queue for event and run state; a worker that checks out repositories and runs Almanac operations; a database for installations, jobs, settings, and billing state; and a GitHub App private key in managed secrets. That is hosting as coordination and execution infrastructure, not a second canonical memory store. [@github-app-flow-session]

Hosted orchestration should live outside the open-source `codealmanac` package. `codealmanac` should own the local engine, operation prompts, config parsing, Almanac-root editing, source connector contracts, publisher interfaces, and any reusable native GitHub source connector library. A hosted `usealmanac`-style app should own GitHub App onboarding, webhook handling, queues, databases, billing, and worker orchestration. Daytona or a similar sandbox provider belongs inside that hosted worker runtime: create an isolated environment, check out the repository or pull request branch, mount GitHub source tools or MCP tools, run CodeAlmanac, restrict writes to the Almanac root, return a validated diff or changed-file result to the delivery layer, and destroy the sandbox. [@github-mcp-transport-session] [@hosted-requirements-log]

The 2026-06-03 backend placement decision made that boundary concrete. Hosted backend work belongs in `usealmanac`, not `almanac-backend`, because `almanac-backend` is old-product history. The implementation should borrow organization patterns from `openalmanac/backend` such as `src/api`, `src/services`, `src/database`, `src/schemas`, `src/clients`, `src/utils`, and `modal_app`, but the product code, GitHub App webhook receiver, repository settings, run records, and Modal worker entrypoints should live in the `usealmanac` repository. The same planning thread treated external application setup as part of the backend work: Supabase or Postgres for hosted state, Vercel for the `usealmanac` frontend, Doppler for runtime secrets, Modal for v1 worker execution, and Render or a similar service only if the FastAPI backend deployment shape needs it. [@hosted-backend-placement-session] [@hosted-github-app-architecture-note] [@hosted-requirements-log]

The 2026-06-05 service-boundary discussion kept the OpenAlmanac backend principles but narrowed their application for the smaller hosted CodeAlmanac backend. Routes should stay thin, external clients should live under `src/clients/`, database/session concerns under `src/database/`, schemas and models beside the service that owns them, and an `Almanac` facade should wire dependencies so routes do not manually construct service graphs. The project should copy those principles rather than pre-create every OpenAlmanac-scale folder before the hosted product has code that needs it. [@hosted-backend-service-boundary-session] [@hosted-almanac-updates-design]

The service split should be product-capability first. `clients/github.py` owns raw GitHub transport: app JWT creation, installation-token minting, REST or GraphQL calls, pagination, retries, rate limits, and primitive operations such as reading pull requests or creating check runs. `services/github_app` owns GitHub App semantics: webhook signature verification, webhook event parsing, event-to-trigger mapping, permission interpretation, and publishing the GitHub check surface through the raw client. `services/installations` owns installation identity, account login, repository selection, and suspension or uninstall state. `services/repositories` owns repo-level product state such as default branch, linked installation, enabled mode, configured Almanac root, fork behavior, and dashboard-owned settings. `services/updates` owns the product lifecycle: typed trigger intake, prompt/run/ignore decisions, user intent, worker run creation, delivery strategy, product state mutation, and status updates on the persistent GitHub check surface. Pull requests are the first trigger source, not the service boundary. [@hosted-backend-service-boundary-session] [@hosted-almanac-updates-design]

The `updates` boundary should receive product-shaped triggers such as `PullRequestChanged`, `PullRequestDiscussionChanged`, `PullRequestMerged`, `CheckActionRequested`, `ManualUpdateRequested`, and `ScheduledDigestDue`. GitHub-specific payload parsing stays in `github_app`, which converts webhooks into normalized trigger facts such as repository ID, pull request number, head SHA, base branch, fork status, actor, event kind, and source delivery ID. `almanac.updates.handle_trigger(trigger)` should return outcomes such as ignore, prompt, run, or wait-for-merge, and `almanac.updates.handle_approval(action, actor)` should preserve authorized user intent before creating worker runs. Routes should publish the returned surface through `github_app.checks` instead of knowing whether the product skipped, prompted, ran, or deferred the work. [@hosted-almanac-updates-design]

Check publication plus check-run-id persistence should be extracted out of routers, but it should not become a vague top-level `almanac.publish_update_outcome(...)` facade method or a new orchestration service. Publishing an `UpdateTriggerOutcome` is GitHub App surface work: transform the outcome into a check payload, create or update the GitHub check run, and record a newly created `check_run_id` through the updates service. The lightweight hosted-backend shape is to wire `GitHubAppService` with `UpdatesService` through the `Almanac` service registry and expose a concrete `publish_update_check(outcome)` method. That follows the old `almanac-backend` composition-root pattern without turning the top-level `Almanac` object into a business-verb facade. [@hosted-update-outcome-publication-session]

The design's negative boundary rules are part of the architecture. Routers should not call Modal or create check-run markdown directly, `updates` should not verify webhook signatures or read raw GitHub payloads, `github_app` should not mint installation tokens or decide product policy, and worker code should report run outcomes rather than owning product truth. An `events` service should be deferred until more than one real subscriber needs an internal event bus. Dashboard-owned repository settings remain under `repositories` for v1 rather than moving into repo config before the hosted loop proves itself. [@hosted-backend-service-boundary-session] [@hosted-almanac-updates-design]

The hosted deployment resource namespace is `codealmanac`, while the frontend project and backend code home remain `usealmanac`. Existing provider state should guide placement instead of names alone: Render's active `openalmanac` backend lived in the `Almanac` workspace and the `virginia` region, while Supabase active projects were visible under the `Reverie` organization with `OpenAlmanac` in `us-east-1` and `Almanac` in `us-east-2`. The setup session therefore treated `us-east-1` as the preferred new Supabase region for overlap with Render Virginia and treated Supabase `micro` as the minimum paid-plan size after `nano` was rejected. Doppler should mirror the existing projects' pattern: deployment uses `codealmanac/prd`, local personal work uses `codealmanac/dev_personal`, and values can match early on while still living in the environment-specific config. Render service creation succeeded after private-repository access was available, but the first deploy failed because Render checked out a `main` commit that did not contain `backend/`; pushing the backend scaffold to Render's deployed branch is the next deployment gate. [@hosted-cloud-resource-session]

Hosted mode can treat CodeAlmanac as doctrine rather than as the only executable runner. The local product can keep using the CodeAlmanac CLI and its provider harnesses, while hosted `usealmanac` can be Python-owned and still load CodeAlmanac base prompts, operation prompts, notability rules, syntax rules, and source connector contracts. The web/API service should receive GitHub events, verify signatures, enqueue jobs, and return quickly; a separately deployed worker should orchestrate sandbox creation, agent execution, diff collection, and write-scope validation. The delivery layer should own GitHub writes such as committing to the pull-request branch, opening follow-up PRs, updating checks or comments, and recording publisher actions. This boundary keeps long-running agent jobs out of the request-response backend and keeps Modal from becoming the product owner for commits. [@hosted-agent-runner-session] [@hosted-requirements-log]

The preferred hosted mental model is an agent process running inside an isolated repo sandbox. The worker still exists, but it starts the sandbox, monitors it, collects its diff, validates write scope, returns the result, and tears down the environment; the sandbox runs the expensive SDK or coding-agent process, shell commands, GitHub source tooling, repository reads, and Almanac edits. Running the agent loop outside the sandbox with sandbox-backed shell and file tools remains a fallback when SDK plumbing makes that easier, but the product language should be "drop an agent into a sandboxed repo" because that matches the user-facing job and parallelizes the heavy work away from the web backend. [@hosted-agent-runner-session] [@hosted-requirements-log]

The 2026-05-31 Modal check changed the v1 substrate preference. Modal can plausibly own both the fire-and-forget job runner and the isolated repo workspace: the API can call a deployed Modal Function with `.spawn()`, Modal handles asynchronous execution, retries, timeouts, concurrency, and result polling, and that function can create a Modal Sandbox for one repository job. The v1 architecture is therefore `usealmanac` API -> Postgres/Supabase job record -> Modal Function `run_almanac_pr_job` -> Modal Sandbox -> GitHub MCP or source tools -> agent/runtime with CodeAlmanac prompts -> diff validator -> GitHub publisher. Daytona should remain a fallback or comparison substrate unless the Modal sandbox spike fails. [@hosted-agent-runner-session] [@modal-job-processing] [@modal-sandboxes] [@hosted-github-app-runtime-session]

The Modal source-access spike should run the Absorb operation with the pull request as starting context, not introduce a separate source operation. The worker should install `gh`, mint a GitHub App installation token per run, export it as `GH_TOKEN`, pass `--repo OWNER/REPO` on every `gh` command, and let Absorb decide which PR facts to inspect. The spike's pass/fail checks are GitHub-token minting, `gh pr view` with PR metadata and comment fields, `gh pr diff` or REST diff fetch, REST reads for review comments and issue comments, HTTPS clone at the pull-request head, completion inside the one-hour token window, and visibility limited to installed repositories. GraphQL-backed `gh pr --json` fields and HTTPS clone are the two permission risks to test rather than assume. [@hosted-gh-cli-spike-session]

The proven worker path refined that plan. `run_update` in the `usealmanac` Modal worker uses `codealmanac@dev` and runs `almanac ingest github:pr:N --foreground --using codex -y` rather than a custom freeform-context Absorb entrypoint. The source-access idea remains the same: the agent gets `gh` under a GitHub App installation token and CodeAlmanac decides what pull-request material matters. The operational entrypoint changed because `ingest github:pr:N` is now the GitHub PR-shaped CodeAlmanac surface, so the old "freeform absorb context" blocker should not be carried forward as a hosted-product dependency. [@pr-update-loop-plan]

The `connectors` slot in the current CodeAlmanac run spec should not be revived for the hosted GitHub path. That slot was Composio-shaped and inert for this worker need, while Composio is no longer part of the core GitHub App source-access path. The long-term replacement is a transport-agnostic source-tool boundary for pull requests, diffs, files, commits, comments, reviews, and linked issues, with implementations such as `gh` CLI, local GitHub MCP, or native GitHub API hidden behind the same operation contract. [@hosted-gh-cli-spike-session] [@pr-update-loop-plan]

The worker should gate temporary Codex subscription auth on credential presence rather than on `almanac doctor` reporting an active authenticated state. Codex OAuth access tokens can expire and refresh during actual use, so a doctor-based gate can falsely block a run that would succeed after refresh. The v1 worker may use the Codex subscription credential exception, but that exception is a runtime bridge rather than the production model-auth architecture. [@pr-update-loop-plan]

The sandbox spike should prove the operational boundary before it becomes architecture: private-repo clone with a GitHub App installation token, Node/npm/codealmanac execution, agent or Codex SDK execution, official GitHub MCP startup with the installation token, pull-request comments and reviews readable through the source tools, diff collection, write blocking outside the Almanac root, and a validated update output that the delivery layer can push to the PR branch when the user clicked `Update this PR` or repo-visible auto-apply allows it. If any of those fail, the fallback is not a different product loop; it is a different worker substrate, source-tool transport, or publisher implementation behind the same event-to-[[evidence-bundles|evidence bundle]]-to-operation boundary. Daytona's current docs still support SDK-created sandboxes, process execution, filesystem operations, and Codex SDK agent workflows, so it remains the main fallback if Modal cannot satisfy the repo-agent workspace needs. [@daytona-sandbox-session] [@daytona-docs] [@daytona-codex-sdk-guide] [@e2b-docs]

The next backend design surface is now concrete enough to name. `usealmanac` needs GitHub App installation and repository onboarding, webhook signature verification, event dedupe and job creation, hosted repository settings for the Almanac root and pull-request behavior, check-run creation and `requested_action` handling, Modal job invocation, run status and logs, hosted wiki browsing, bot-authored Almanac-root commit publishing, and publisher status updates back to GitHub. Proposal records with changed page names, diff access, `Ignore`, and `Always update automatically` belong to the later approval-first mode unless the MVP deliberately accepts proposal storage or pending bot branches. This API surface belongs to the hosted product, while `codealmanac` remains the local engine and prompt/page doctrine. [@hosted-github-app-runtime-session] [@hosted-github-direct-commit-session] [@hosted-settings-session] [@hosted-action-transport-session]

V1 GitHub App settings live in the hosted dashboard or database, not in repo configuration. Repo-based settings would make behavior reviewable in Git, but they add configuration PRs and source-of-truth questions before the core GitHub App loop is proven. The first same-repository settings surface should stay simple: `ask`, `auto`, or `disabled`, with the hosted service owning the current repository mode. Changing a repository from `ask` to `auto` is forward-looking only: it affects future pull-request triggers and does not retroactively run Almanac on existing pull requests that were already prompted or skipped unless a user explicitly runs Almanac on those pull requests. [@hosted-settings-session]

Newly installed repositories should default to `ask` and begin on future trigger events only. Installation should not comment on every existing open pull request. The default same-repository path is new non-draft PRs and `ready_for_review` transitions receiving the "Update the Almanac?" surface; existing PRs are left alone unless a later supported event intentionally brings them into scope. [@hosted-settings-session]

Authorization should be a server-side product service, not checks scattered through webhook handlers or UI button visibility. The v1 shape is `authorize(user, action, resource, context) -> allow | deny`, backed by GitHub repository permissions and PR state. `Update this PR` and `Skip this PR` require write, maintain, or admin permission on the repository; `Always update in this repo` and repository settings changes require maintain or admin permission; dashboard read paths can use read permission. The backend must identify the GitHub sender and re-run authorization before starting a Modal job, changing repository settings, committing to a branch, or publishing an Almanac update PR. Unauthorized clicks should create an audit event and redraw the prior GitHub comment or check state with a denial note; they must not set the pull request to active, change repository settings, or enqueue a run. RBAC and ABAC are enough for v1 because GitHub role and resource attributes carry the important decisions; OPA/Rego, Cedar, OpenFGA, or Zanzibar-style relationship authorization should remain later options for complex organization and team policy. [@hosted-authorization-session]

The hosted dashboard should be a BFF and user-auth layer over existing hosted services, not a second product engine. GitHub remains the PR-time action surface for `Update this PR`, check status, and same-branch Almanac commits; the dashboard covers the work GitHub cannot do well: repository and installation selection, settings, run history and observability, hosted wiki browsing, account management, and billing. The dashboard should be repo-centric because users ask what Almanac is doing in a specific repository before they ask for an organization-wide memory product. [@hosted-dashboard-review-session]

Dashboard tenancy should be the GitHub App installation, not the individual user who installed the app. GitHub-derived authorization and billing entitlement must stay separate: authorization answers whether a user may read or change a repository or installation resource, while billing answers whether the installation has capacity to run hosted work. GitHub OAuth should use an opaque signed session cookie with encrypted OAuth tokens stored server-side, rather than putting encrypted GitHub tokens directly in cookies, because the dashboard will call GitHub repeatedly and needs revocation, rotation, and audit control. [@hosted-dashboard-review-session]

Supabase Auth is the v1 dashboard identity and session layer on both frontend and backend. The frontend should use the Supabase client for GitHub OAuth login, session state, and logout. The backend should verify the Supabase session or JWT, read the Supabase user and linked GitHub identity, and then apply Almanac authorization policy over GitHub repository permissions. Almanac should not build custom `users` and `user_identities` tables for v1 because Supabase already owns stable users, provider identities, identity linking, sessions, and future enterprise identity paths. [@hosted-dashboard-auth-session] [@supabase-github-auth-docs]

The v1 identity model should stay smaller than the earlier service sketches. Supabase `auth.users` and `auth.identities` own app users and linked login methods, while GitHub owns repository permissions and current provider account facts. Almanac should not create `GitHubAccountSnapshot`, `ConnectedIdentity`, `DashboardUser`, `DashboardUserAuth`, `DashboardUserRecord`, or a broad local `users` table unless a product-owned fact needs storage. Valid local tables are product state, durable audit, billing, repository settings, pull-request state, run state, webhook delivery dedupe, a measured cache, or a verified linked-account row for an authorization-bearing external identity. [@hosted-dashboard-identity-minimal-session] [@hosted-dashboard-identity-access-session]

The dashboard service boundary should separate identity, accounts, and access. `services/identity` owns Supabase token verification and returns an authenticated app user. `services/accounts` owns linked external identities and may wrap Supabase `auth.identities` for GitHub, Google, or WorkOS without leaking Supabase's storage shape to the rest of the backend. Its core API should be provider-parameterized, such as `accounts.require_linked_account(user, provider=AccountProvider.GITHUB)`, rather than a GitHub-only `github_account_for(...)` helper. `services/access` owns repository-specific action checks using GitHub App installation facts, GitHub collaborator permissions, and Almanac product policy. The stable browser flow is `identity.authenticate(token) -> accounts.require_linked_account(user, provider=GITHUB) -> repositories.get_repository(repo_id) -> access.require_repository_action(github_login, action, repository)`, while GitHub webhooks build the GitHub login directly from the signed payload and reuse the same access policy. `accounts` can start as a small identity-adjacent helper if v1 only has GitHub, but the named boundary is useful because later Google, GitHub, and WorkOS account facts should not be folded into repository authorization. A broad actor framework should wait until more than the browser and webhook paths need it. [@hosted-dashboard-identity-access-session]

Per-request dashboard authentication should split "who is signed in" from "which external account may authorize repository actions." `identity.authenticate(token)` should verify the Supabase JWT locally through claims or JWKS behavior and return an `AuthenticatedUser` for the signed-in Supabase user. That local JWT path is trusted for the Supabase user identity, but it should not be assumed to contain the trusted GitHub account link because Supabase access tokens commonly expose user metadata and app metadata but not the full provider `identities[]` record. [@hosted-dashboard-identity-access-session]

Authorization-bearing GitHub identity must never come from Supabase `user_metadata` or `raw_user_meta_data`. Those fields are user-editable, so trusting `user_metadata.user_name` would let an attacker set their GitHub login string to a repository admin's login and pass a downstream GitHub permission check as the wrong person. Trusted link material can come from Supabase provider identity data captured during OAuth, Supabase app metadata written by service-role code, or a product-owned verified linked-account row derived from those trusted sources. [@hosted-dashboard-identity-access-session]

The corrected v1 shape is to capture the verified GitHub link once from trusted Supabase identities, anchor it on stable `github_user_id`, store current `github_login` plus refresh metadata in product-owned linked-account state, and let `accounts.require_linked_account(user, provider=GITHUB)` read that verified row on ordinary requests. Occasional refresh can use Supabase `get_user` or another trusted identity lookup, but ordinary dashboard requests should not hide a Supabase API round trip inside account resolution. The small verified-link table earns its place because the GitHub identity link is both authorization-bearing and needed often. [@hosted-dashboard-identity-access-session]

`require_repository_action` means "can this GitHub login perform this Almanac product action on this repository," not generic repo access. Its implementation should map actions such as `VIEW_WIKI`, `EDIT_REPO_SETTINGS`, and `UPDATE_THIS_PR` to required GitHub permissions, ask the GitHub integration for the login's current repository permission, and raise access denied before settings changes, wiki reads, run enqueue, branch commits, or check publication. GitHub check-run button identifiers should be translated inside a small `github_app.check_actions` boundary into product actions instead of becoming flat route logic or a broad `github_app` catchall. [@hosted-dashboard-identity-access-session]

GitHub repository permission remains the source of truth for repository actions, but dashboard pages should not fan out one GitHub permission API call for every backend request. V1 should cache permission facts for a short window keyed by GitHub login, repository, and action or required permission, roughly 30 to 60 seconds. That cache is only a latency and rate-limit guard; losing repository access may remain visible for less than a minute, and every mutating backend action still calls the same `access.require_repository_action(...)` boundary rather than trusting frontend state. [@hosted-dashboard-identity-access-session]

The GitHub App installation token remains the repository credential for automation, `.almanac/` reads, GitHub checks, and bot commits. Supabase documents GitHub login as a GitHub OAuth App configured in Supabase with `signInWithOAuth({ provider: "github" })` and SSR callback code exchange, so custom dashboard session auth should wait for a concrete Supabase blocker. Supabase provider tokens should not become Almanac's core GitHub access path because Supabase does not refresh them and does not store them in the project database; they are only a possible fallback for user-specific permission checks if installation-token permission endpoints cannot answer a repository-access question. [@hosted-dashboard-auth-session] [@supabase-github-auth-docs] [@supabase-provider-token-docs]

Hosted wiki-reader endpoints such as `GET /api/dashboard/repos/{repo_id}/wiki` and `GET /api/dashboard/repos/{repo_id}/wiki/pages/{slug}` may read `.almanac/` through the GitHub App installation token only after the backend verifies the Supabase user, maps that user to a GitHub login, confirms the repository is installed, and checks that the user has GitHub read access to the repository. The installation token is the app's repo-scoped file credential, not a bypass around user authorization. The required invariant is `Supabase user -> GitHub login -> GitHub repo permission -> product action policy` for every dashboard repo, wiki, run, and settings endpoint. [@hosted-dashboard-auth-session] [@github-app-installation-auth]

Dashboard wiki reads should be Git-ref-aware because the Almanac root is repository state. The default branch is the canonical dashboard view, a pull-request branch is a preview of proposed or in-flight Almanac state, and arbitrary branch refs are possible later without becoming the primary UI. The API term should be `ref`, as in `GET /api/dashboard/repos/{repo_id}/wiki?ref=default`, `?ref=pr:418`, or `?ref=branch:release/1.4`; `source` remains reserved for raw material the agent learns from, such as pull requests, issues, transcripts, and documents. [@hosted-dashboard-wiki-ref-session]

Dashboard wiki listing may expose a missing `.almanac/pages` directory as an empty wiki state, but upstream GitHub errors are not empty wiki states. A GitHub 403, 500, malformed content response, or transport failure should propagate as an error response rather than `200` with an empty page list, because a false empty wiki hides authorization, installation, ref, and transport problems from users and operators. [@hosted-dashboard-wiki-reader-review-session]

Dashboard copy must describe the current same-PR product loop accurately. `ask` means Almanac proposes on a pull request and waits for approval; `auto` means Almanac updates the pull-request branch automatically when relevant pull-request activity happens. "Update automatically on PR merge" describes a later after-merge delivery mode, not the current same-PR branch model, and would make users expect follow-up PR behavior that v1 does not provide. [@hosted-dashboard-review-session]

Billing should exist as a service boundary before it becomes full payment machinery. `billing.has_run_capacity(...)` and `billing.record_run(...)` are the right call shape, but Autumn customer creation, webhook mirroring, metering, entitlement gates, local billing mirrors, and usage UI are v1 machinery only if charging is imminent. If dashboard and settings are the immediate MVP, a no-op or free billing provider behind the same seam preserves the architecture without making Autumn the blocking path. [@hosted-dashboard-review-session]

`Update this PR` is ongoing approval for that pull request, not a one-shot run request. After authorization passes, the hosted database owns the persistent PR state and the GitHub comment or check is only a projection of that state. V1 reruns should trigger on `pull_request.synchronize`, `pull_request_review.submitted`, and `pull_request_review_comment.created` because commits change code and review comments often carry rationale. V1 should not rerun on every `issue_comment.created`; ordinary PR comments can contain thanks, CI noise, bumps, or other conversation that does not justify another Almanac run. [@hosted-pr-rerun-session]

Useful discussion that does not change code should mark the pull request as dirty without immediately running Almanac. The next code-triggered run or explicit `Update now` action can include that discussion; merge should run one final check for active pull requests whose discussion changed since the last run. If the same-PR Almanac update was already captured before merge, the final check can report that Almanac is current. If uncaptured discussion landed after the last update, the hosted app should open a follow-up Almanac update PR against the maintained base branch. [@pr-evolution-session] [@hosted-pr-rerun-session]

Doppler is the preferred hosted secret manager for v1 when it fits the deployment shape. Durable secrets include the GitHub App private key, webhook secret, model provider keys, Modal tokens, database credentials, and source-tool credentials. GitHub App installation tokens are not durable secrets; the worker should mint them per job and inject them into the Modal Function or Sandbox runtime. [@hosted-github-app-runtime-session]

The first hosted implementation slice should prove the platform loop without an AI agent. The target demo is a GitHub App installed on a test repository, a same-repository pull request, one check run with `Update this PR` and `Skip this PR`, a clicked `requested_action` event that starts a Modal job, a checkout of the pull-request branch, a fake Almanac file change, validation that only the configured Almanac root changed, a returned change result from Modal, a delivery-owned bot commit to the pull-request branch, and an update to the same check run. This slice tests the riskiest non-agent surfaces: GitHub App auth, check-run action handling, Modal async execution, branch checkout, push permissions, check mutation, delivery ownership, and write-path validation. The next slice can replace the fake file change with a real agent run that starts GitHub MCP or Octokit source tools, uses CodeAlmanac or Codex structured-output paths when useful, edits the Almanac root, returns a summary and validated diff, and lets delivery push the resulting commit. [@hosted-github-first-slice-session] [@hosted-action-transport-session] [@hosted-requirements-log]

By the end of 2026-06-05, the `usealmanac` dev branch had the hosted same-repository PR update loop implemented locally: durable update state, typed GitHub trigger normalization, mutable check-run surfaces, collaborator-permission authorization, Modal invocation, Modal callback completion, same-PR delivery through GitHub Git Data API, bot-loop suppression through delivered commit SHA tracking, and an internal-secret-protected repository settings API. Review-blocker hardening made Modal completion idempotent for terminal runs, finished `changed` bundles with no files without delivery, rejected empty Git Data commits, prevented stale or manual fork follow-up actions from queueing undeliverable runs, dispatched delivery through `run.delivery_kind`, failed unimplemented delivery kinds at the delivery boundary, removed active fork prompt and waiting-for-merge surfaces, and switched internal-secret comparison to `hmac.compare_digest`. Final local verification after the duplicate-delivery fix passed with 85 backend tests, route tests, compile, and lint. [@pr-update-implementation-log] [@pr-update-production-smoke-session]

The production gate passed on 2026-06-05 after the branch was pushed, merged to `main`, deployed to Render, paired with the production Supabase migration, redeployed to Modal, and smoke-tested on a same-repository pull request. The successful smoke used `AlmanacCode/codealmanac#12`; Render was live on commit `05ead0e`, the Almanac check reached success with the title "Almanac updated", the App committed `.almanac/pages/github-native-wiki-maintenance.md` as bot commit `09e4b706491207e3433cc264d7911839682b2196`, and the production run row reached `succeeded`, `delivered`, `same_pr_branch` with that delivered commit SHA. [@pr-update-live-smoke-runbook] [@pr-update-loop-plan] [@pr-update-production-smoke-session]

PR 12 should not be treated as clean evidence that the GitHub UI approval path works end to end. Production state showed `same_repo_behavior=ask`, `approved_by=rohans0509`, `approved_at=2026-06-05 19:59:08 UTC`, and a successful run created at the same time, but the recorded GitHub deliveries did not include a `check_run.requested_action` event for that PR. The smoke proves that the backend can create a check, spawn Modal, receive a bundle, and commit `.almanac/` changes to the same PR branch; a separate clean smoke should prove `check_run.requested_action -> actor authorization -> run enqueue` with no manual or synthetic backend trigger. [@pr-update-production-smoke-session]

The PR 12 smoke also exposed a GitHub visibility invariant for same-PR delivery. GitHub check runs are attached to a specific commit SHA, so the Almanac check that succeeded on pre-delivery head `fd38bd2` stopped appearing in the current pull-request check summary after the bot commit advanced the head to `09e4b70`. Same-PR delivery should therefore publish or update a terminal Almanac check on the post-delivery head SHA as well as recording the delivered commit SHA, so the current PR view still shows `Almanac updated` after the bot commit lands. [@pr-update-production-smoke-session]

Checks remain the right v1 action and status surface because GitHub check-run actions provide native `Update this PR`, `Skip this PR`, and `Always update in this repo` buttons and appear in the merge box. A sticky PR comment is still useful as the human-readable thread because comments are visible in conversation history, can explain why Almanac is waiting or what it changed, and can be edited in place after delivery. The product invariant is that the hosted database owns the pull-request state, the check run projects actionable status for the current head SHA, and the sticky comment projects human-readable context without becoming the authorization mechanism. [@hosted-action-transport-session] [@pr-update-production-smoke-session] [@pr-surface-followup-session]

The follow-up product critique changed the default feel even though it did not remove checks. The merge box is culturally a CI and gate surface, so Almanac should not make the check run the only visible product experience or make routine Almanac maintenance feel like an extra approval chore. For trusted same-repository pull requests, `auto` should probably become the normal mode after installation: Almanac updates the PR branch when the Almanac should change, posts or updates a sticky comment with the changed pages and rationale, and leaves the check as the compact current-head status. `ask` remains useful for first-run trust, public repositories, forks, and teams that do not want a bot mutating PR branches by default. [@pr-surface-followup-session]

The product UX contract is one sticky Almanac comment plus one Almanac check per pull request. The comment is the human-readable thread: it says when no Almanac update was needed, when Almanac is checking the pull request, which pages changed after a bot commit, supported rationale when the run produced it, and what happened on later PR revisions. The check is the compact status and control projection: `No Almanac update needed`, `Checking the Almanac`, `Almanac updated`, `Waiting for maintainer`, or `Waiting for merge`, with actions only when the repository is in `ask` mode or the user can change the repository mode. User-facing copy should say "Almanac", "Update the Almanac", "Almanac pages", or "project knowledge"; it should not say "repo memory", "memory update", or "repo-memory update". Almanac should edit these surfaces in place rather than adding a new comment on every push. [@pr-ux-flow-session] [@same-pr-almanac-update-session]

For the normal same-repository path, auto-update means Almanac analyzes the PR source material and existing Almanac, commits `.almanac/` changes to the same PR branch when durable project knowledge changed, and updates the sticky comment with changed pages. Reviewers then inspect, edit, or revert the Almanac commit through the ordinary pull-request diff. `ask` mode changes only the start condition: the check presents `Update this PR`, `Skip`, and possibly `Always update in this repo`, and the run begins after authorization. Fork PRs remain a separate delivery mode; the intended user-facing state is waiting until merge and then opening a follow-up Almanac update PR, but v1 must not advertise that state until follow-up delivery exists. [@pr-ux-flow-session] [@pr-update-implementation-log]

The current hosted worker contract should let the agent write the full sticky-comment markdown rather than forcing the backend to compose meaning from small reason fields. The useful bundle shape is `comment_markdown: str | None` alongside status and changed files. The backend validates that comment markdown is present for `changed` or `no_change`, enforces safety limits such as length and unsafe links, and posts or edits the sticky PR comment. It should not invent per-page rationale after the fact or split the agent's explanation into backend-composed reason objects. [@pr-ux-flow-session]

The same live smoke found a webhook idempotency invariant before it passed. Duplicate GitHub deliveries must stop after delivery-record dedupe and must not continue into trigger handling, run creation, check publishing, or Modal invocation. The production blocker was that duplicate deliveries were recorded idempotently but still processed; the fix made duplicates return before product handling and added a regression test before the successful Render deploy. [@pr-update-production-smoke-session]

Fork follow-up delivery is intentionally disabled in v1 even though the product model still has a future after-merge path. The settings API can only set `fork_behavior` to `disabled`, so deployed repository settings cannot promise an unimplemented follow-up PR delivery flow. [@pr-update-implementation-log]

The extensibility rule for the hosted update pipeline is that configuration stays mechanical. Settings may decide whether a run starts, which operation or provider runs, and where the completed bundle is delivered, but they must not decide what project knowledge belongs in the Almanac. The pipeline shape is `Trigger -> Source -> Operation -> Policy -> Run -> Bundle -> Select -> Deliver`: source facts and settings select a `delivery_kind`, and the delivery executor receives that kind plus a bundle without reading fork or source-specific facts. V1 should build only the `same_pr_branch` strategy, the `choose_delivery` policy seam, and honest unavailable surfaces; JSONB nested settings, non-PR source refs, comment delivery, Almanac-branch delivery, external-repo delivery, and follow-up PR delivery are deferred until a second real source or delivery method justifies the migration. [@extensible-update-pipeline-design] [@pr-update-implementation-log]

Long-running Modal agent runs need an explicit async completion path because GitHub webhook handlers cannot wait one to five minutes for CodeAlmanac. The recommended v1 architecture is Modal callback to backend: the webhook handler records a run, spawns Modal, returns quickly, and later receives an authenticated internal callback containing the validated bundle or failure result; the backend then runs delivery and updates the check surface. The old `almanac-backend` job pattern supports the durable-state discipline rather than a pure callback-only design: a job row is the source of truth, the worker records progress and heartbeats, and a scheduled sweeper marks stale running jobs failed. The hosted CodeAlmanac version should use callback as the normal completion path and a stale-run sweeper only for missed callbacks, killed workers, or stuck GitHub checks, not as a poller that routinely asks Modal whether work is done. [@hosted-async-completion-session] [@hosted-callback-security-session]

The Modal completion route uses the old backend's internal-secret pattern as a route-level dependency, not as global middleware for v1. GitHub webhooks are public external callbacks and authenticate with `X-Hub-Signature-256` HMAC verification; GitHub cannot send Almanac's internal proxy secret. Modal completion is an internal callback and requires `X-Internal-Secret` before the backend accepts a run result, validates bundle paths, commits Almanac-root changes, or updates the GitHub check. A later global internal-proxy middleware can exist after route exemptions are stable, but copying it before the webhook surface settles would add avoidable failure modes. [@hosted-callback-security-session] [@pr-update-implementation-log]

Two hosted-loop invariants should be treated as repo-specific manual doctrine. First, durable run state must commit before any external worker spawn: the backend creates and commits a queued run, spawns Modal outside that transaction, then records the invocation in a second transaction or marks the run failed if spawn fails. Second, delivery mechanisms must be source-blind after policy selection: fork, writability, branch, and settings facts choose a `delivery_kind` before delivery starts, and the same-PR branch executor should only write to the resolved target instead of rechecking source facts such as `is_fork`. These rules belong in the hosted product's manual section because they are local invariants of the GitHub App and Modal loop, not universal CodeAlmanac doctrine. [@hosted-manual-alignment-session]

The Modal spawn and completion paths have a specific race contract. Completion may win after the worker starts but before the webhook path records the Modal invocation or publishes its projected GitHub check. Spawn recording must therefore always persist `modal_call_id` while only promoting still-queued rows to `running` and `modal_spawned`; terminal rows keep their terminal status and step. After spawn recording or spawn failure handling, the webhook path must re-read the run. If completion already won and no `check_run_id` is recorded, the webhook path should return no surface so GitHub publishing no-ops, because the internal completion route is responsible for publishing and recording the first terminal check id. [@hosted-terminal-race-hardening-session]

## Branch Scope

There is no branch-independent hosted Almanac for a repository when the wiki is stored in Git. Each maintained branch can carry a different Almanac root because each branch can carry different code, docs, config, and reviewed project memory. Almanac Cloud therefore maintains the wiki on the branch that owns the code state being discussed.

For a merged pull request, the maintenance target is the base branch that received the merge. A pull request merged into `dev` should produce an Almanac update PR targeting `dev`, not `main`. A hotfix merged into `release/2026.5` should update the `release/2026.5` Almanac root when that branch is configured for maintenance. A later merge from `dev` to `main` can carry the wiki edits through normal Git history or trigger a separate main-branch maintenance run if the resulting main state needs different synthesis.

Hosted configuration should distinguish maintained branches from preview branches. Maintained branches are branch patterns whose Almanac roots the App is allowed to update through Almanac update PRs. Preview branches can be rendered, searched, or inspected for a pull request without becoming a durable maintenance target. Feature branches may include contributor-authored Almanac changes, but the App should treat those as proposed changes until they merge into a maintained branch.

Mintlify is useful precedent for this branch model, not a content-model template. Its GitHub docs describe a connected repository, branch, and optional subdirectory as the documentation source; its troubleshooting asks users to verify that they are pushing to the configured deployment branch; and its preview-deployment docs say automatic previews are created for pull requests targeting the deployment branch while manual previews can be created for arbitrary branches. Almanac should copy the source-branch and preview distinction: maintained branches get automatic memory maintenance, while other branches can get preview rendering and context.

## Connector Boundary

An Almanac connector is the agent-facing read path for remote CodeAlmanac. It should expose repo wiki knowledge through tools such as `search_almanac(repo, query)`, `show_page(repo, slug)`, `context_for_files(repo, files)`, `context_for_pr(repo, pr_number)`, and `list_topics(repo)`. It should also expose enabled source systems through source-access tools or connector-specific tools, so an agent can inspect a GitHub pull request, issue, comment thread, or commit range on demand instead of receiving a preselected context blob. Those tools let Codex, Claude, Cursor, OpenHands, and custom agents ask what the repo already knows before they edit files.

The source connector contract should hide transport choice from the agent operation. A v1 GitHub connector can use official local/Docker GitHub MCP if a short spike proves that its pull-request, repository, issue, and actions toolsets expose PR details, diffs, files, comments, reviews, review comments, linked issue context, and check-run or workflow data under a GitHub App installation token. If that spike fails, the same conceptual tools can be backed by native GitHub API or Octokit-style calls such as `github.get_pr`, `github.list_comments`, `github.list_reviews`, `github.read_diff`, and `github.search_issues`. GitHub's App installation docs make Octokit.js the standard SDK path for installation-token API calls, and the same installation token can also authenticate REST, GraphQL, and HTTP Git access when the App has the required permissions. The operation should receive source tools, not know whether the implementation came from MCP, native REST calls, or a third-party connector service. [@github-app-installation-auth] [@github-mcp-transport-session] [@github-mcp-deepwiki-answer]

The connector should not own the self-updating loop. It is read and retrieval infrastructure: agent-queryable wiki pages, file-aware context, branch or repository selection, and links back to the reviewed source pages. The write path still needs GitHub events through an Action, App, cron job, or webhook worker that runs Absorb and opens a normal Almanac update PR.

The compact architecture is one repo-owned wiki with two product edges: a connector for agent queries and a GitHub Action or App for PR-maintained updates. The product sentence is: Almanac is a connector-readable wiki and source-access layer for repositories, kept current by GitHub pull requests.

## MVP Validation

The 2026-05-29 MVP discussion narrowed the first product test to a GitHub-backed, agent-queryable wiki that updates itself through pull requests. The smallest useful loop is not Scout, queue triage, maintainer routing, billing, comments, or a hosted dashboard. It is a repo with an Almanac root, agents that can query it, and a post-merge job that opens a reviewed Almanac update PR when durable project memory changed.

The implementation should start inside this repository because CodeAlmanac already has search, show, topics, capture, [[ingest-operation]], Absorb, and page-writing concepts. A narrow source-aware `ingest` path can read a merged diff, pull request, or issue through connector-provided tools, ask whether durable memory changed, edit pages when needed, and print the files changed. A GitHub Action can run that path on pushes to the default branch and use `peter-evans/create-pull-request` or an equivalent step to open the Almanac update PR.

OpenClaw or another active public repository can still be a testbed, but only through a fork or read-only experiment. The success criterion is simple: a code PR merges, the Action runs, Almanac updates or creates a page, a PR opens, and a human says the Almanac update is useful. If that loop works, Scout, queue views, context comments, maintainer routing, and a hosted App become workflow layers rather than the core product proof.

OpenClaw is useful as a scale example because a high-activity public repository already has issue and pull-request automation for readiness, proof quality, merge risk, and maintainer status. Almanac's missing value there would not be another blanket triage bot. The useful loop is maintainer repetition reduction, decision capture, PR-time context from existing pages, post-merge Almanac update PRs, and strict silence unless cited Almanac context or a high-confidence missing-context signal exists.

## Canonical State Boundary

The default canonical state should stay in the same repository. The current implementation uses `.almanac/` for reviewed wiki source and local machinery, but the product boundary should be a configurable `almanac root` rather than a hard-coded hidden path. Same-repo ownership gives project memory the same branch, review, merge history, CODEOWNERS, blame, rollback, and access boundary as the code it describes.

The root choice is an adoption profile. `docs/almanac/` is the preferred public/team default when a repository can carry project memory under `docs/`; it is visible, conventional, and low-clutter. `.almanac/` is the quiet profile for local/private use or for projects whose `docs/` tree is a curated product-docs surface. A top-level `almanac/` has the strongest brand visibility and the highest repo-root clutter cost, so it should remain opt-in.

Generated state should not live inside the public/team Almanac root by default. Local commands can hash the repository identity and store `index.db`, run history, extracts, and caches in platform user-cache locations such as `~/Library/Caches/almanac/<repo-id>/`, `~/.cache/almanac/<repo-id>/`, or `%LOCALAPPDATA%/Almanac/<repo-id>/`. Hosted state should be cache and coordination state: indexed Almanac pages, source provenance, embeddings if later needed, webhook deliveries, run history, stale-page findings, source extracts, and pending maintenance jobs. Hosted state can make the experience fast and team-friendly, but correctness should not depend on an opaque memory record that cannot be reviewed with the code.

Separate storage is an escape hatch, not the default. It fits multi-repo architecture memory, company-wide policy pages, regulated deployments that need a separate repository, private source caches, or an org-wide Almanac that intentionally spans repositories. Even then, the durable page artifact should still be Git-backed markdown somewhere.

Same-repo Almanac update PRs have a real automation cost. A pull request that only changes the Almanac root can still trigger CI checks, preview deployments, branch protection, review assignment, Slack notifications, or production deployment workflows after merge when a repository runs automation on every pull request or every push to a maintained branch. GitHub Actions path filters such as `paths-ignore: [".almanac/**"]` reduce that risk, but relying on every customer to configure deploy automation correctly is fragile. [@almanac-update-pr-deploy-risk-session]

The product should therefore treat canonical Almanac location as a risk profile rather than only a taste choice. Same-repo Almanac update PRs give the strongest local-agent and Git-review story, but carry medium deploy-noise risk unless path filters exist. A same-repo dedicated branch such as `almanac/wiki` lowers deploy risk while weakening the tie to the branch that owns current code. A separate Almanac repository has the lowest deploy risk and can serve multi-repo company memory, but it makes agent checkout, access control, and source-of-truth discovery less direct. The default remains same-repo for MVP because it best preserves the trust story, but onboarding should recommend or propose CI and deploy ignores for the configured Almanac root when it can do so safely. [@almanac-update-pr-deploy-risk-session]

## Hosted Browsing Boundary

The 2026-05-28 follow-up clarified that the canonical wiki root does not have to be the primary human reading surface. The repo path and the reading surface should be separate: pages under the configured Almanac root are the reviewed source of truth, the CLI, connector, GitHub App, and raw markdown are agent and automation surfaces, and a hosted site such as `almanac.dev/{owner}/{repo}` should be the human wiki surface for public repos and teams.

The hosted viewer is not a replacement store. Its job is to render the repo-owned graph with search, topics, backlinks, related files, PR and issue provenance, stale-page status, maintainer ownership, changed-since views, and agent-ready context packs. GitHub can render a markdown file, but it cannot make an Almanac page behave like a navigable project-memory object with file references, source provenance, graph context, and drift state.

This boundary also separates Almanac from public product docs. README files, tutorials, API references, changelogs, and user documentation explain how to use a project. Almanac pages explain how the project thinks, changes, and gets maintained: architecture decisions, rejected approaches, subsystem owners, issue triage rules, compatibility constraints, review expectations, and known maintenance traps. The product promise is "reviewed in Git, browsed on Almanac, used by agents everywhere," not "replace the docs folder."

Mintlify is the closest product-pattern precedent for this storage and rendering split. Its docs describe `docs.json` as the central site configuration for a documentation project, use a GitHub App to sync documentation from a connected repository, automatically deploy when changes land on the connected branch, and create pull-request preview URLs so reviewers can inspect rendered docs before merge. Mintlify's source root is intentionally visible because it is a docs source tree: `docs.json` and MDX pages can live at the repository root, under a `docs/` directory, or in a dedicated docs repository. Almanac should copy the Git-backed source plus hosted rendering pattern, not Mintlify's public-docs content model: pages and topics under the configured Almanac root stay the source for code repositories, while the hosted viewer renders project memory with graph navigation, provenance, drift status, and agent context.

## Team Need

The first-principles team need is not remote memory storage. Teams need trusted current project context that answers what was decided, whether it is true on this branch, what evidence supports it, whether an agent will see it before editing, and whether humans can review changes to that memory like code.

That makes the hosted product a governed maintenance layer over project memory:

- PR-time relevant page surfacing for changed files.
- Drift detection when code changes invalidate pages.
- Wiki-maintenance PRs after merges.
- CODEOWNERS-aware or configured maintainer routing for Almanac update PRs and subsystem-specific context.
- Scheduled Garden runs for stale pages, dead file references, unresolved questions, and broken source links.
- Hosted viewer and search for humans who will not browse markdown pages directly.
- MCP or API retrieval that returns cited Almanac context packets to agents.
- Multi-repo indexes without hiding canonical pages in a hosted database.

## Buyer And Payment Thesis

Teams will pay for this only when the product saves expensive engineering time or reduces change risk. The pain is strongest when senior engineers repeat the same architectural context in reviews, agents violate hidden invariants, stale docs cause bad implementation choices, onboarding into complex repos is slow, or compliance and process knowledge drifts away from the code.

The strongest buyer is a team using multiple AI coding agents, many junior contributors, external contractors, or a complex long-lived codebase where project-specific context changes review outcomes. In that setting, "project memory maintenance" is a workflow cost and risk product. "AI wiki" or "memory database" is weaker positioning because it sounds like optional storage.

The paid boundary should therefore be private-team governance rather than memory volume. The product name for that tier should be Almanac Teams. The local CLI and public-repo convention can remain free, while paid features cover private repo GitHub App automation, org-wide almanacs, cross-repo context, hosted viewer and search, drift dashboards, SSO, audit logs, retention controls, private model routing, self-hosted or VPC workers, and CODEOWNERS-aware wiki PR routing.

Free open-source use is strategic because it can make `.almanac/` a normal repository convention for agents and contributors. Private teams then pay for the governance, automation, security, and cross-repo scale needed to make the same convention reliable inside a company.

Almanac Teams should be explained through the concrete problem, not a feature list: engineering teams are losing project memory while AI increases the rate of code change. Engineering managers want new engineers and agents to stop interrupting senior people for context. Tech leads want invariants and decisions to be hard to miss before code changes. Platform and DevEx teams want every repo to have current, searchable, reviewable project knowledge. Security and compliance teams want architecture, release, and process knowledge to stay auditable. AI tooling buyers want agents to inherit real project memory rather than grep the repo and guess.

## Open-Source Research Lesson

The 2026-05-28 open-source research pass found direct overlap on both sides of the product. `aictx/memory`, Cline Memory Bank, and similar local memory projects validate repo-owned agent memory but make the local storage pattern easier to commoditize. CodeWiki, DeepWiki-Open, RepoAgent, and docAider validate repo-scale decomposition, generated architecture documentation, diagrams, AST-aware updates, and pull-request-triggered documentation maintenance. PR-Agent, Claude Code Action, OpenReview, and OpenHands validate GitHub comments, checks, webhook jobs, sandboxed workers, agent-triggered reviews, and PR-creating agents as normal engineering surfaces.

That comparison strengthens the GitHub-native thesis rather than weakening it. A remote CodeAlmanac should not be "local wiki plus sync," because local agent memory and generated repo documentation are already becoming legible categories. The unresolved surface is team governance: PR-time context from reviewed memory, drift detection when code invalidates pages, post-merge Almanac update PRs, and a hosted queue that keeps project memory current without making hidden hosted state canonical.

OpenReview is the most relevant implementation pattern from the open-source set. Its GitHub App webhook starts a durable workflow, creates a sandbox, clones the pull request branch, runs an agent, and posts comments or commits back to the branch. A remote CodeAlmanac worker can use the same event-to-job shape, but its output should be wiki context and Almanac maintenance PRs rather than general code-review findings.

The product sentence after the research is: CodeAlmanac keeps the repo's agent wiki true as code changes, with every durable Almanac update reviewed in GitHub.

## Open-Source Route

[[open-source-almanac]] is the public-repository adoption path for the same GitHub-native maintenance loop. The 2026-05-29 open-source research pass found that maintainers struggle most with attention scarcity, support burden, stale process surfaces, contributor onboarding, and low-quality AI-generated reports or pull requests. That makes free OSS Almanac a maintainer-attention product rather than a hosted wiki giveaway.

The free OSS version should make an Almanac root a public convention for contributors and coding agents without requiring a visible top-level brand directory. It should index public repo docs, issues, pull requests, release notes, and existing Almanac pages; post quiet cited context only when it can reduce maintainer repetition; suggest likely maintainers when ownership is known; and open reviewed maintenance PRs after decisions change project memory. It should not auto-close issues, generate a giant wiki on day one, or make hidden hosted memory canonical for public projects.

The strongest OSS social protocol is: if a contribution was AI-assisted, cite the Almanac pages it used. That turns AI disclosure into a testable context habit and connects public-agent behavior to reviewed project memory.

## Open Questions

The remaining product questions are operational, not category-level. PR-time comments need a noise budget before developers mute them. Post-merge Almanac update PRs need a batching rule so the system does not create doc churn. Remote Absorb jobs need a minimum evidence bundle before they can edit the repo-owned Almanac. Blocking checks should start as opt-in because false-positive wiki drift can damage trust. Org-level almanacs need a clear boundary between same-repo Almanac pages and cross-repo architecture Almanac pages.

## Related Pages

[[customer-segmentation]] explains why the GitHub-native product should start with OSS maintainers and AI-heavy startup teams before enterprise governance. [[open-source-almanac]] explains the free public-repo product path for maintainers, contributors, and AI-assisted open-source work. [[company-brain]] places this product direction inside the broader market for agent-readable organizational memory. [[almanac-product-family]] explains why scoped Almanacs should preserve source material separately from maintained wiki synthesis. [[just-in-time-context-surfacing]] explains the local runtime version of the same surfacing principle. [[codex-supermemory]] explains why automatic hosted recall is compelling but should not become CodeAlmanac's canonical project memory.
