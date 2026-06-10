# Architecture Cleanup Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Remove stale Composio, deprecated CLI aliases, legacy connector runtime fields, and `health --fix`, while keeping recurring Garden installed by default and preserving local `gh` source ingest.

**Architecture:** This refactor deletes unsupported or stale public surfaces instead of moving them around. GitHub source ingest remains the small local `gh`-based path under `src/ingest/`; external integrations do not get a generic connector framework until there is a concrete first-party integration to build. Health reports problems, while explicit migration commands mutate wiki metadata.

**Tech Stack:** TypeScript, Commander, Vitest, local `.almanac/` wiki files, `better-sqlite3`, `js-yaml`.

---

## Baseline Notes

- Worktree: `/Users/rohan/.config/superpowers/worktrees/codealmanac/architecture-cleanup`
- Branch: `codex/architecture-cleanup`
- `npm run lint` passed before changes.
- `npm test` had one baseline failure in `test/setup.test.ts`: the setup automation plist points at the Vitest worker entrypoint instead of `dist/codealmanac.js` when run in this worktree. Do not mix that unrelated setup bug into this cleanup unless a touched slice requires it.
- The original workspace still contains unrelated `.almanac` changes and untracked `docs/architecture-audit-2026-06-08/`; this branch must not delete or stage those original-workspace files.

## Task 1: Remove Composio And Connector Public Surface

**Files:**
- Modify: `package.json`
- Modify: `package-lock.json`
- Modify: `src/cli/register-setup-commands.ts`
- Modify: `src/cli/commands/config-keys.ts`
- Modify: `src/cli/commands/config.ts`
- Modify: `src/config/schema.ts`
- Modify: `src/config/codec.ts`
- Modify: `src/config/store.ts`
- Modify: `src/viewer/api.ts`
- Modify: `src/viewer/server.ts`
- Delete: `src/cli/commands/connect.ts`
- Delete: `src/cli/commands/source.ts`
- Delete: `src/connectors/`
- Delete tests for Composio-only surfaces.
- Modify tests that expected connector config, connect/source commands, or viewer connections.

**Behavior:**
- Remove `almanac connect`.
- Remove `almanac source`.
- Remove `connectors.*` config keys and TOML config sections.
- Remove `@composio/core`.
- Keep `almanac ingest github:pr:N` and `github:issue:N` local `gh` behavior.
- Keep the source-ref and source-provenance model.

**Focused tests:**

```bash
npm test -- --run test/config-command.test.ts test/github-source-resolver.test.ts test/ingest-input.test.ts test/operation-commands.test.ts test/viewer-api.test.ts test/cli.test.ts
```

## Task 2: Remove Deprecated CLI Aliases

**Files:**
- Modify: `src/cli/register-query-commands.ts`
- Modify: `src/cli/register-setup-commands.ts`
- Modify: `src/cli/register-wiki-lifecycle-commands.ts`
- Modify: `src/cli/commands/show.ts`
- Modify: `src/cli/commands/update.ts`
- Modify: `src/cli/commands/agents.ts`
- Delete or rewrite: `test/deprecations.test.ts`
- Modify command/help tests.

**Behavior to delete:**
- `almanac set ...`
- `almanac ps`
- `almanac capture status`
- `almanac show --raw`
- `almanac update --enable-notifier`
- `almanac update --disable-notifier`

**Behavior to keep:**
- `almanac capture` alias `c`.

**Focused tests:**

```bash
npm test -- --run test/cli.test.ts test/show.test.ts test/update.test.ts test/agents-command.test.ts test/jobs-command.test.ts
```

## Task 3: Replace `health --fix` With Explicit Migration

**Files:**
- Modify: `src/cli/register-query-commands.ts`
- Modify: `src/cli/register-edit-commands.ts` or a new registration family if cleaner.
- Modify: `src/cli/commands/health/index.ts`
- Create: `src/cli/commands/migrate.ts`
- Modify: `src/wiki/health/index.ts`
- Move or reuse: `src/wiki/health/legacy-frontmatter-fix.ts`
- Modify: `test/health.test.ts`
- Create: `test/migrate-command.test.ts`

**Behavior:**
- `almanac health` warns when legacy frontmatter migration is available.
- `almanac health --fix` no longer exists.
- `almanac migrate legacy-sources` applies the deterministic legacy source migration.
- The migration remains explicit and safe; health remains diagnostic.

**Focused tests:**

```bash
npm test -- --run test/health.test.ts test/migrate-command.test.ts test/cli.test.ts
```

## Task 4: Remove Connector Runtime Fields From Harness Specs

**Files:**
- Modify: `src/harness/types.ts`
- Modify: `src/operations/run.ts`
- Modify: `src/operations/absorb.ts`
- Modify: `src/harness/providers/codex/app-server.ts`
- Modify: `src/harness/providers/codex/request.ts`
- Modify: `test/codex-harness-provider.test.ts`
- Modify: `test/harness-types.test.ts`
- Modify: `test/absorb-operation.test.ts`

**Behavior:**
- Delete `ConnectorRuntimeRequirement`.
- Delete `AgentRunSpec.connectors`.
- Use only `networkAccess` for source-ingest sandbox network access.
- Do not add a new connector abstraction.

**Focused tests:**

```bash
npm test -- --run test/harness-types.test.ts test/codex-harness-provider.test.ts test/absorb-operation.test.ts test/operation-commands.test.ts
```

## Task 5: Remove Legacy Codex Exec Runtime Compatibility

**Files:**
- Modify: `src/harness/providers/codex.ts`
- Modify: `src/harness/providers/codex/request.ts`
- Delete or quarantine: `src/harness/providers/codex/exec.ts`
- Delete or quarantine: `src/harness/providers/codex/jsonl-events.ts`
- Modify: `test/codex-harness-provider.test.ts`

**Behavior:**
- Production Codex runtime stays app-server for this branch.
- Remove exported `runCodexCli`, `CodexExecRequest`, and `buildCodexExecRequest`.
- Do not migrate to `@openai/codex-sdk` in this branch.

**Focused tests:**

```bash
npm test -- --run test/codex-harness-provider.test.ts test/harness-provider-registry.test.ts test/operation-commands.test.ts
```

## Task 6: Documentation And Wiki Alignment

**Files:**
- Modify: `CLAUDE.md`
- Modify active `.almanac/pages/*` pages only when they currently assert removed behavior.
- Keep audit docs in the original workspace intact; this branch does not need to import the untracked audit folder.

**Updates:**
- Remove Composio claims.
- State that GitHub local source ingest uses `gh`.
- State that health warns and `migrate legacy-sources` mutates.
- State that recurring Garden remains part of setup automation.
- Remove stale deprecated alias guidance.

**Focused checks:**

```bash
almanac search "Composio" --limit 20
almanac search "health --fix" --limit 20
almanac search "capture status" --limit 20
```

## Task 7: Final Verification

Run:

```bash
npm run lint
npm test -- --run test/config-command.test.ts test/github-source-resolver.test.ts test/ingest-input.test.ts test/operation-commands.test.ts test/viewer-api.test.ts test/cli.test.ts test/show.test.ts test/update.test.ts test/agents-command.test.ts test/jobs-command.test.ts test/health.test.ts test/migrate-command.test.ts test/harness-types.test.ts test/codex-harness-provider.test.ts test/absorb-operation.test.ts test/harness-provider-registry.test.ts
npm run build
git diff --check
```

Run full `npm test` before merge and record whether the baseline setup plist failure is still the only failure.

