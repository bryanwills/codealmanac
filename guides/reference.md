# Almanac CLI Reference

Long-form reference for the `almanac` CLI installed by the `codealmanac` npm
package. The mini guide covers when to use the wiki; this file covers command
shape, data shape, and current storage conventions.

Durable wiki source lives in `docs/almanac/`. Runtime state lives in `.almanac/`.

## Storage Model

```text
docs/almanac/
  README.md              front door
  topics.yaml            topic DAG
  **/*.md                wiki pages

.almanac/
  index.db               derived SQLite index
  jobs/                  job records, logs, sync ledger
  config.toml            project agent config
```

The index is derived. Query commands call `ensureFreshIndex` before reading.

## Frontmatter

Canonical page frontmatter:

```yaml
---
page_id: provider-harness
title: Provider Harness
description: Provider runtime metadata and execution behavior.
topics: [architecture, agents]
sources:
  - id: provider-registry
    type: file
    path: src/agent/providers/index.ts
    note: Registers provider metadata.
  - id: provider-decision
    type: manual
    note: Rohan chose provider-owned runtime truth during the architecture review.
---
```

Normal fields:

| Field | Purpose |
|---|---|
| `page_id` | Stable page identity. Kebab-case. Optional but recommended. |
| `title` | Display title. Falls back to first H1, then filename. |
| `description` | One-sentence preview for search/sidebar listings. |
| `topics` | Topic slugs. Also stored in `docs/almanac/topics.yaml`. |
| `sources` | Evidence. Cite with `[@source-id]` in prose. |

`sources` is the only authored provenance field. `type: file` entries and inline
file/folder wikilinks derive `file_refs`, which power `search --mentions`,
`show --files`, and `health dead-refs`.

Supported source types: `file`, `web`, `commit`, `pr`, `issue`, `conversation`,
`wiki`, and `manual`.

## Wikilinks

One syntax, classified by content:

| Syntax | Kind |
|---|---|
| `[[page-id]]` | Page link in the current wiki. |
| `[[page-id\|Display text]]` | Page link with custom display text. |
| `[[src/file.ts]]` | File reference. |
| `[[src/folder/]]` | Folder reference. |
| `[[other-wiki:page-id]]` | Cross-wiki reference. |

Paths are normalized at index and query time: lowercase, forward slashes, no
leading `./`, collapsed duplicate slashes, trailing slash only for folders.

## Query Commands

### `almanac search [query]`

Find pages by full text and filters.

| Flag | Semantics |
|---|---|
| `--topic <name...>` | AND-intersect topic filter. Walks descendants. |
| `--mentions <path>` | Pages with derived file refs matching a file/folder. |
| `--since <duration>` | Updated within a duration such as `2w` or `30d`. |
| `--stale <duration>` | Not updated within the duration. |
| `--orphan` | Pages with no topics. |
| `--wiki <name>` | Query a registered wiki by name. |
| `--json` | JSON array output. |
| `--descriptions` / `--verbose` | Slug plus one-line description. |
| `--limit <n>` | Cap results. |

Default output is one slug per line. Empty results print nothing to stdout and
`# 0 results` to stderr. JSON output is silent on stderr.

JSON rows: `{slug, title, description, updated_at, topics}`.

### `almanac show [slug]`

Read a page.

| Flag | Semantics |
|---|---|
| `--stdin` | Read slugs from stdin. Emits JSON Lines. |
| `--json` | Full structured page object. |
| `--body` | Body only. |
| `--verbose` | Metadata header plus body. |
| `--meta` | Metadata header only. |
| `--lead` | First paragraph only. |
| `--title`, `--topics`, `--files`, `--links`, `--backlinks`, `--xwiki`, `--updated`, `--path` | Field output. |

`--files` prints derived file references, not an authored frontmatter field.

JSON page shape includes:

```ts
{
  slug: string
  title: string | null
  description: string | null
  file_path: string
  updated_at: number
  topics: string[]
  file_refs: { path: string; is_dir: boolean }[]
  sources: { id: string; type: string; target: string; title: string | null; retrieved_at: string | null; note: string | null }[]
  wikilinks_out: string[]
  wikilinks_in: string[]
  cross_wiki_links: { wiki: string; target: string }[]
  body: string
}
```

### `almanac topics`

Inspect and edit the topic DAG.

```bash
almanac topics
almanac topics list
almanac topics show auth --descendants
almanac topics create auth --parent architecture
almanac topics link jwt auth
almanac topics unlink jwt auth
almanac topics rename old new
almanac topics delete old
almanac topics describe auth "Authentication and identity."
```

Topic structure is stored in `docs/almanac/topics.yaml`. Page assignments are
stored in page frontmatter. Rename/delete rewrite both.

### `almanac health`

Report wiki integrity. It does not mutate files.

| Flag | Semantics |
|---|---|
| `--topic <name>` | Scope page checks to a topic subtree. |
| `--stale <duration>` | Stale threshold. Default `90d`. |
| `--stdin` | Restrict page checks to stdin slugs. |
| `--json` | Structured report. |
| `--wiki <name>` | Target a registered wiki. |

Categories: `orphans`, `stale`, `dead-refs`, `broken-links`, `broken-xwiki`,
`missing-sources`, `unused-sources`, `duplicate-sources`, `empty-topics`,
`empty-pages`, and `slug-collisions`.

### `almanac list`

List registered wikis.

| Flag | Semantics |
|---|---|
| `--json` | Structured output. |
| `--drop <name>` | Remove a registry entry. This is the only removal path. |
| `--verbose` | Include descriptions and paths. |

### `almanac serve`

Start the local read-only viewer.

```bash
almanac serve --port 3927
```

The viewer exposes pages, search, topics, file mentions, registered wiki
switching, and job transcripts. It does not invoke AI or mutate wiki source.

## Edit Commands

```bash
almanac tag checkout-flow payments flows
almanac tag --stdin needs-review
almanac untag checkout-flow needs-review
```

`tag` auto-creates missing topics and rewrites only frontmatter. Body bytes are
preserved.

```bash
almanac migrate automation
```

Migrates old scheduled capture automation to the current scheduled sync job.

## Lifecycle Commands

### `almanac init`

Create the initial wiki for a repo. It creates `docs/almanac/README.md`,
`docs/almanac/topics.yaml`, `_manual/`, `_meta/`, and runtime `.almanac/`
state, then runs the Build operation.

Common flags: `--using <provider[/model]>`, `--background`, `--json`, `--force`,
`-y`.

### `almanac absorb <inputs...>` / `almanac ingest <inputs...>`

Update the wiki from explicit files, folders, PRs, issues, or URLs. `ingest`
routes to the same implementation as `absorb`.

Common flags: `--using <provider[/model]>`, `--foreground`, `--json`, `-y`.

### `almanac sync`

Scan supported Claude/Codex transcript stores, wait for quiet sessions, map each
session to the nearest repo with `docs/almanac/`, reconcile
`.almanac/jobs/sync-ledger.json`, and enqueue background Absorb jobs for new
material.

Common flags: `--from <apps>`, `--quiet <duration>`, `--using <provider[/model]>`,
`--json`. `almanac sync status` reports eligible work without enqueuing jobs.

### `almanac garden`

Maintain an existing wiki graph: page boundaries, links, topics, stale claims,
hubs, source quality, and readability.

Common flags: `--using <provider[/model]>`, `--foreground`, `--json`, `-y`.

### `almanac jobs`

Inspect lifecycle jobs under `.almanac/jobs/`.

```bash
almanac jobs
almanac jobs show <job-id>
almanac jobs logs <job-id>
almanac jobs attach <job-id>
almanac jobs cancel <job-id>
```

Each subcommand accepts `--json`.

### `almanac automation`

Manage scheduled sync.

```bash
almanac automation install
almanac automation install --every 2h --quiet 30m
almanac automation status
almanac automation uninstall
```

## Setup Commands

### `almanac setup`

Install scheduled sync, guide files, and agent instruction imports.

Common flags: `-y`, `--agent`, `--model`, `--skip-automation`,
`--sync-every`, `--sync-quiet`, `--skip-guides`, `--auto-commit`.

### `almanac uninstall`

Remove scheduled sync and installed guides. Flags: `-y`, `--keep-automation`,
`--keep-guides`.

### `almanac doctor`

Read-only install and wiki report. It checks binary, SQLite binding, provider
readiness, automation, guides, registry, page/topic counts, index freshness,
last absorb, and health status. JSON output has stable `install`, `agents`,
`wiki`, and `updates` arrays.

### `almanac agents`

Inspect and configure provider defaults.

```bash
almanac agents list
almanac agents doctor
almanac agents use codex
almanac agents model claude claude-opus-4-6
almanac agents model claude --default
```

Provider resolution order:

```text
--using flag > project config > user config > provider default
```

### `almanac config`

Scriptable config surface.

```bash
almanac config list
almanac config list --show-origin
almanac config get agent.default
almanac config set auto_commit true
almanac config set --project agent.default codex
almanac config unset agent.models.claude
```

User config lives at `~/.almanac/config.toml`. Project config lives at
`.almanac/config.toml`.

### `almanac update`

Manual foreground update plus update-banner controls.

```bash
almanac update
almanac update --check
almanac update --dismiss
```

Almanac does not auto-install updates.

## Registry And Cross-Wiki Links

The registry is `~/.almanac/registry.json`. Query/edit commands auto-register a
repo when `docs/almanac/` exists. `almanac list --drop <name>` is the only
automatic removal path.

Cross-wiki links use `[[wiki-name:page-id]]`. `health --broken-xwiki` checks
that the named wiki is registered and reachable.

## Troubleshooting

`search` returns nothing:

- Empty stdout plus `# 0 results` means a clean no-match.
- An `almanac:` line means a real invocation/runtime error.

`--mentions` misses a page:

- Add a structured file source with `type: file`, or use an inline
  `[[src/path.ts]]` / `[[src/folder/]]` link.
- Run `almanac reindex` if manual file timestamps are suspect.

Dead refs look wrong:

- Check path casing. Almanac stores normalized lookup paths and original paths
  for filesystem checks.

Sync did not run:

```bash
almanac doctor
almanac automation status
almanac sync status --json
almanac jobs
ls -lah .almanac/jobs/
```

Useful files:

- `docs/almanac/README.md` — wiki front door
- `docs/almanac/topics.yaml` — topic DAG
- `.almanac/index.db` — derived index
- `.almanac/jobs/<job-id>.json` — job record
- `.almanac/jobs/<job-id>.jsonl` — provider event log
- `.almanac/jobs/sync-ledger.json` — scheduled sync cursor
