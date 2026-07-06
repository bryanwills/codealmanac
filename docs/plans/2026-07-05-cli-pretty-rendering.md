# Plan: CLI pretty rendering, background-by-default, gorgeous jobs

Date: 2026-07-05. Decided in conversation after the archive-vs-Python CLI
rendering audit.

## Decisions (from the user)

- **Human shape is the priority.** Every command renders the pretty,
  colored, aligned human shape by default. There is no separate plain
  "machine shape" — `--json` is the piping format. Color still degrades
  to plain text automatically when stdout is not a TTY or `NO_COLOR` is
  set (the ansi.ts trick), so pipes remain clean without a second
  renderer.
- **Search shows summaries by default.** Slug + indented one-line
  summary, like the old `--summaries`. `--slugs` forces bare slugs.
- **Show renders the old metadata header + `---` + body by default.**
  Composable narrowing flags; conflicting view flags **fail loudly**
  (ValidationFailed), never silently drop.
- **Background by default for ingest/garden.** Output names the started
  run and how to attach. `--foreground` is the marked flag. The
  foreground result block (wiki_changes, health_before, summary) is
  preserved on the foreground path and in `jobs show` via run records.
- **Jobs get the old gorgeousness on the new run-record store**: aligned
  table with humanized elapsed, colored status, rich `show` view with
  page-change breakdown and log path, attach terminal failure summary.
- **Deferred explicitly:** search `--since/--stale/--orphan/--archived`,
  health `--topic/--stale` and the stale category, archive-aware flags
  (index/service work, separate slice); PID/staleness probing on run
  records; `automation status` next-run estimate.
- Removals stay removed: `agents`, `review`, `migrate`. `init` stays
  deterministic + synchronous. Update mechanism stays. Setup stays.
- **Config gains keys**: `harness.default`, `sync.quiet` join
  `auto_commit` in `config set`, typed per key.
- **Durations humanize** everywhere they render (`900s` → `15m`).

## Design

One new module carries the whole look:

```python
# cli/render/style.py — port of archive ansi.ts + table.ts
USE_COLOR   # stdout.isatty() and NO_COLOR unset
RST BOLD DIM BLUE GREEN RED YELLOW          # "" when not USE_COLOR
table(headers, rows) -> list[str]           # ANSI-aware width math
humanize_duration(td) -> "45m"              # humanfriendly, coarse
humanize_elapsed(start, end|now) -> "12m"
```

Render modules import these constants; when piped, every constant is an
empty string so output degrades to exactly the plain text agents parse
today. Rich stays confined to setup/uninstall.

`jobs show` composes the old view from data already on `RunRecord`
(`page_changes`, `log_path`, `started_at`/`finished_at`, `error`,
`harness_transcript`). No store changes needed for this slice.

## File changes

- `src/codealmanac/cli/render/style.py` — new.
- `render/search.py` — summaries default, `--slugs`, >50 stderr nudge.
- `render/pages.py` — header + `---` + body default; single-field flags
  stay bare; view-flag conflicts raise ValidationFailed.
- `render/topics.py` — TOPIC/PAGES table, empty-state hint, aligned
  `topics show` with em-dash placeholders and "(incl. descendants)".
- `render/health.py` — bold section names, green ok / red counts, prose
  findings; validate verdict colored, issues as sentences.
- `render/diagnostics.py` — ✓/✗/◇ icons, dim fix lines.
- `render/workspaces.py` — two-line pretty entries with description,
  empty-state hint; keep `--drop`/`--drop-missing` wording.
- `render/jobs.py` — table, colored status, humanized elapsed, rich
  show, styled logs/attach, terminal failure summary.
- `render/automation.py` — humanized intervals.
- `render/lifecycle.py` + `dispatch/operations.py` +
  `parser/lifecycle.py` — background default, `--foreground`, started
  output with attach hint.
- `services/config/` — ConfigKey additions + typed set.
- `parser/wiki.py` — `--slugs` on search.

## Tests

Update `tests/test_cli.py` output assertions (capsys is not a TTY, so
existing plain-text assertions mostly keep passing; new assertions for
summaries lines, show header, flag-conflict errors, jobs table words,
background default). Config service tests for new keys. Gates:
`uv run pytest`, `uv run ruff check .`.

## Read before coding

- `archive/code/src/ansi.ts`, `table.ts`, `commands/show.ts`,
  `commands/jobs.ts`, `commands/health/index.ts` (target look).
- `src/codealmanac/cli/render/*` (current shapes), `services/runs/models.py`.
