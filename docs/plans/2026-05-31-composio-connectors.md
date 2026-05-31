# Composio Connectors Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace the temporary `gh`-based GitHub source access path with a Composio-backed connector substrate, starting with first-class `almanac connect github` UX and GitHub issue/PR ingest.

**Architecture:** Composio is the connector runtime, not a per-app plugin system inside Almanac. Almanac keeps source semantics in `src/ingest/` and connector/account setup in a new connector module; Composio owns external authentication, connected-account routing, and toolkit access. GitHub is the first native connection UX, but the internal shape should be `connector account + toolkit + source brief + runtime instructions`, not a hardcoded GitHub API client.

**Tech Stack:** TypeScript, Commander, local TOML config, Composio TypeScript SDK or Composio CLI fallback if SDK gaps appear, Vitest, existing process/harness shell-tool runtime.

---

## Current Findings

- Composio sessions can be restricted to toolkits such as `github`, expose meta tools for runtime tool discovery, and expose an MCP URL for MCP-compatible clients.
- Composio connected accounts support listing, refreshing, enabling/disabling, deleting, multiple accounts, and explicit `connectedAccountId` tool execution.
- `composio link github` is the fast local auth path for personal CLI usage; the SDK also exposes `toolkits.authorize(userId, "github")` and session-level `authorize("github")`.
- Almanac should not prefetch GitHub issue/PR body JSON in CLI code. The source resolver should produce identity and runtime requirements; the run should inspect source material through Composio tools.
- The current code still has transitional `gh --version` / `gh auth status` checks and prompt guidance. This branch removes that.

## Target Flow

```text
almanac connect github --account work
  -> read Composio API key from config/env
  -> start Composio GitHub connection flow
  -> persist account alias, toolkit slug, connected account id/status

almanac ingest https://github.com/AlmanacCode/codealmanac/issues/11
  -> parse SourceRef as github.issue
  -> resolve GitHub source identity: repo, URL, number
  -> select Composio GitHub account from explicit flag, repo binding, or default
  -> render source brief and connector runtime guidance
  -> run Absorb with source metadata
  -> agent uses Composio-backed GitHub access to inspect the source
```

## Task 1: Connector Config Model

**Files:**
- Modify: `src/config/schema.ts`
- Modify: `src/config/codec.ts`
- Modify: `src/config/index.ts`
- Test: `test/config-command.test.ts` or new `test/connectors-config.test.ts`

**Steps:**
1. Add a `connectors` config object with Composio API key reference, GitHub accounts, and repo bindings.
2. Normalize missing connector config to empty/default values.
3. Serialize TOML tables such as `[connectors.composio]`, `[connectors.github.accounts.work]`, and `[connectors.github.repo_bindings."Owner/repo"]`.
4. Add tests for parse/serialize/normalize round trips.
5. Commit.

## Task 2: Composio Adapter Boundary

**Files:**
- Create: `src/connectors/composio/client.ts`
- Create: `src/connectors/composio/accounts.ts`
- Create: `src/connectors/types.ts`
- Test: `test/composio-connectors.test.ts`

**Steps:**
1. Define Almanac-owned types for connector account aliases, toolkit slugs, account status, and connection requests.
2. Wrap Composio SDK usage behind an injectable adapter so tests do not call the network.
3. Resolve the API key from config first, then `COMPOSIO_API_KEY`.
4. Implement GitHub account listing/status and connection initiation.
5. Commit.

## Task 3: `almanac connect github`

**Files:**
- Create: `src/cli/commands/connect.ts`
- Modify: `src/cli/register-setup-commands.ts`
- Test: `test/connect-command.test.ts`

**Steps:**
1. Add `almanac connect github --account <alias>` with non-interactive output.
2. Print the Composio redirect URL when browser auto-open is not implemented.
3. Persist the connected account id/status after completion when the adapter can wait for connection.
4. Add `almanac connect github --status` and `--list` if they stay small; otherwise defer to a follow-up command.
5. Commit.

## Task 4: GitHub Source Resolution Uses Connector Accounts

**Files:**
- Modify: `src/ingest/github.ts`
- Modify: `src/ingest/source.ts`
- Modify: `src/ingest/input.ts`
- Modify: `src/cli/commands/operations.ts`
- Test: `test/github-source-resolver.test.ts`
- Test: `test/operation-commands.test.ts`

**Steps:**
1. Remove `gh --version` and `gh auth status`.
2. Resolve GitHub source identity only: kind, raw, repo, URL, number.
3. Attach a connector runtime requirement such as `{ toolkit: "github", accountAlias, connectedAccountId }`.
4. Support explicit `almanac ingest ... --account <alias>` if the option is straightforward.
5. Fail with a setup-oriented outcome if no GitHub connector account can be selected.
6. Commit.

## Task 5: Prompt Guidance And Runtime Tool Access

**Files:**
- Modify: `src/ingest/context.ts`
- Modify: `src/operations/run.ts`
- Modify: `src/harness/tools.ts` or provider adapters if a first-class tool is needed
- Test: `test/ingest-input.test.ts`
- Test: `test/absorb-operation.test.ts`

**Steps:**
1. Replace `gh` prompt guidance with Composio connector guidance.
2. Prefer Composio session/toolkit meta-tools over hardcoded GitHub tool names.
3. If the provider cannot consume Composio-native tools directly yet, expose a small shell-compatible bridge command or prompt the agent to use Composio CLI as the runtime access path.
4. Keep the operation prompt source-specific enough for GitHub issue/PR provenance and citation rules.
5. Commit.

## Task 6: Viewer Connection Surface

**Files:**
- Modify: `src/viewer/api.ts`
- Modify: `src/viewer/server.ts`
- Modify: `viewer/*`
- Test: existing viewer API/UI tests

**Steps:**
1. Add a read-only connections API that reports supported native connections and current GitHub account status.
2. Add a simple connections screen with GitHub icon/name, Connect, and Manage affordances.
3. Do not store secrets in browser-visible responses.
4. Commit.

## Task 7: Review, Squash, Merge

**Steps:**
1. Run targeted tests after every task.
2. Ask subagents for architecture review after Tasks 2, 4, and 5.
3. Run `npm run lint`, `npm test`, `npm run build`, and `git diff --check`.
4. Squash merge this branch into `dev`.
5. Do not push `dev`.
