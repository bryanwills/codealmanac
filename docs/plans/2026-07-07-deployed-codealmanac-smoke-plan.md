# Deployed CodeAlmanac Acceptance Plan

Goal: test the installed `codealmanac` as a real user would, with real machine
state, real launchd automation, real temp repositories, real provider choices,
and explicit notes for expectation gaps.

This is not a unit-test checklist. It is a product acceptance pass. The order is
deliberate: highest-risk, highest-trust flows first.

## Ground Rules

- Use `/Users/rohan/.local/bin/codealmanac`, not `uv run`, unless a test says it
  is comparing deployed behavior to source behavior.
- Record every bug and quirk in an operation note.
- Use throwaway repositories for writer tests.
- Do not run Garden or Ingest on an important repo until the same path has
  passed in a throwaway repo.
- Stop after any serious bug, write the actual/expected gap, and decide whether
  the bug blocks further testing.

## Current Deployed Surface

Observed deployed version: `codealmanac 0.3.1`.

Observed public commands:

- `init [path]`
- `ingest inputs...`
- `garden`
- `sync status`
- `list`
- `search`, `show`, `topics`, `health`, `validate`, `reindex`, `serve`
- `tag`, `untag`
- `config list|get|set`
- `setup`
- `uninstall`
- `doctor`
- `update --check`
- `jobs show|logs|attach|cancel`
- `automation install|uninstall|status`

Important expectation gap to watch: earlier manual output showed bare
`codealmanac jobs` listing jobs, but deployed help says a jobs subcommand is
required. Treat this as a product surface test.

## What We Record For Every Test

- command
- current directory
- relevant config before and after
- relevant files created or changed
- job ID if any
- `codealmanac jobs` or `jobs show` evidence
- database evidence when needed
- launchd evidence when needed
- expected behavior
- actual behavior
- severity: blocker, important, polish, or environment quirk

## Priority 0: Do Not Corrupt The Machine

These come before real operation runs.

### P0.1 Installed Binary Identity

Question: are we testing the deployed product?

Procedure:

1. `which codealmanac`
2. `codealmanac --version`
3. `codealmanac doctor`
4. Confirm no command is accidentally invoking the repo checkout.

Expected:

- Binary is `/Users/rohan/.local/bin/codealmanac`.
- Version is deployed version.
- Doctor reads `~/.codealmanac/codealmanac.db`.

### P0.2 Baseline State Snapshot

Question: what global state already exists before testing?

Procedure:

1. `codealmanac list --json`
2. `codealmanac config list`
3. `codealmanac automation status`
4. `codealmanac jobs` and `codealmanac jobs --json`
5. `sqlite3 ~/.codealmanac/codealmanac.db` inspect repositories, runs, locks.
6. `launchctl list | rg codealmanac`

Expected:

- We know registered repositories, stale entries, config, active jobs, and
  launchd state before changing anything.

### P0.3 Backup Global State

Question: can we restore if setup/uninstall/config tests mutate user state?

Procedure:

1. Copy `~/.codealmanac/codealmanac.db`.
2. Copy `~/.codealmanac/config.toml`.
3. Copy the three codealmanac launchd plists.
4. Record instruction files that setup owns.

Expected:

- We can restore the pre-test machine state manually.

## Priority 1: Trust And Installation

These decide whether a user can trust setup.

### P1.1 Doctor On Real Machine

Question: does doctor tell the truth?

Procedure:

1. Run `codealmanac doctor` inside this repo root.
2. Run it from an unrelated folder.
3. Run it with `--json`.

Expected:

- In repo: shows install and wiki health.
- Outside repo: install is still visible, wiki selection is explicit.
- JSON contains the same facts as human output.

### P1.2 Setup Default

Question: does first setup create the right global state?

Procedure:

1. Run `codealmanac setup --yes` on the real installed CLI.
2. Inspect config.
3. Inspect instruction files for Codex and Claude.
4. Inspect automation status.
5. Inspect launchd plists and logs directory.

Expected:

- Config is valid.
- Instructions are installed.
- Sync, Garden, and update automation are installed unless explicitly disabled.
- Output tells the user what changed.

### P1.3 Setup Variants

Question: do setup flags map cleanly to product choices?

Cases:

- `setup --yes --target codex`
- `setup --yes --target claude`
- `setup --yes --target all`
- `setup --yes --skip-instructions`
- `setup --yes --no-auto-commit`
- `setup --yes --sync-off`
- `setup --yes --garden-off`
- `setup --yes --no-auto-update`
- `setup --yes --sync-every 1h --garden-every 2h`

Expected:

- Each flag changes only its promised surface.
- Re-running setup is idempotent.
- Disabled automation is actually absent from launchd.
- Config remains valid after every variant.

### P1.4 Uninstall

Question: does uninstall remove only setup-owned local artifacts?

Procedure:

1. Run `codealmanac uninstall`.
2. Inspect automation status.
3. Inspect launchd list.
4. Inspect instruction files.
5. Confirm repositories and wiki files are not destroyed.
6. Re-run setup after uninstall.

Expected:

- Automation is unloaded and plists removed.
- Setup-owned instructions are removed.
- User wiki content and database are not recklessly destroyed.

## Priority 2: Config And Provider Choice

These affect every agent run.

### P2.1 Config Read/Write Round Trip

Procedure:

1. `config list`
2. `config get auto_commit`
3. `config set auto_commit false`
4. `config set auto_commit true`
5. `config get harness.default`
6. `config get harness.model`

Expected:

- Values persist in `~/.codealmanac/config.toml`.
- Human output and JSON output agree.

### P2.2 Provider Switching

Procedure:

1. `config set harness.default codex`
2. Confirm model becomes Codex default.
3. Set a valid Codex model.
4. `config set harness.default claude`
5. Confirm model becomes Claude default.
6. Set a valid Claude model.
7. Switch back to Codex.

Expected:

- Provider and model never become inconsistent.
- Errors mention allowed values.

### P2.3 Invalid Config

Cases:

- `config set auto_commit maybe`
- invalid provider
- invalid model name
- Claude model while provider is Codex
- Codex model while provider is Claude
- malformed TOML manually written to config file

Expected:

- Command fails cleanly.
- Existing valid config is not silently corrupted.
- Doctor surfaces invalid config if relevant.

## Priority 3: Repository Registration And Root Semantics

This is central to the no-root-hopping product stance.

### P3.1 Fresh Repo Init

Procedure:

1. Create a throwaway git repo.
2. Add a small source file and commit.
3. Run `codealmanac init /path/to/repo`.
4. Inspect `almanac/README.md`, `almanac/topics.yaml`, and git status.
5. Run `codealmanac list`.
6. Run `doctor` from the repo root.

Expected:

- `almanac/` exists.
- Repository is registered.
- Doctor recognizes the repo.

### P3.2 Duplicate Init

Procedure:

1. Run `codealmanac init /path/to/repo` again.

Expected:

- It stops.
- It does not overwrite existing `almanac/`.
- Error is simple and clear.

### P3.3 Exact Directory Behavior

Procedure:

1. From exact repo root: run `search`, `health`, `topics`, `garden`.
2. From a nested subfolder: run the same commands.
3. From unrelated folder: run the same commands.
4. Repeat with `--wiki <name>` where supported.

Expected:

- Exact root works.
- `--wiki` works from anywhere.
- Nested folder behavior must match the current product decision. If it still
  root-hops, record it as a decision gap.

### P3.4 Stale Repository

Procedure:

1. Create/register a throwaway repo.
2. Delete the repo folder.
3. Run `list`, `doctor`, `sync`, and scheduled Garden.

Expected:

- Missing repo is visible as unavailable.
- Scheduled Garden should not queue writing jobs for missing repos.

## Priority 4: Jobs And Queue Behavior

This is the user’s mental model for operations.

### P4.1 Jobs List Surface

Procedure:

1. Run bare `codealmanac jobs`.
2. Run `codealmanac jobs --json`.
3. Compare with help text.

Expected:

- If bare jobs lists jobs, help should say so.
- If bare jobs is invalid, product UX may need reconsideration.

### P4.2 Job Detail Surfaces

Procedure:

1. Pick a failed job.
2. `jobs show <id>`
3. `jobs logs <id>`
4. `jobs attach <id>` on a completed job.
5. `jobs cancel <id>` on completed, failed, queued, and running jobs.

Expected:

- Show gives enough context.
- Logs are useful.
- Attach exits cleanly for terminal jobs.
- Cancel handles each state clearly.

### P4.3 Queue Mechanics

Procedure:

1. Queue multiple operations.
2. Inspect DB run order.
3. Start worker path naturally through a command.
4. Observe whether one job runs at a time.
5. Cancel running job.
6. Confirm locks/processes clear.

Expected:

- Queue order is understandable.
- Failed jobs do not block later jobs.
- Cancellation is visible and cleans up.

## Priority 5: Writer Operations

These are the heart of the product and should run on throwaway repos first.

### P5.1 Init As Build

Question: does init scaffold and then run the first agent write correctly?

Procedure:

1. Create throwaway repo with meaningful code.
2. Run `init --using codex`.
3. Inspect queued/running job.
4. Inspect terminal output.
5. Inspect resulting wiki.
6. Repeat with `--using claude`.

Expected:

- Scaffold exists before writing.
- Agent job is visible.
- Resulting wiki is useful.
- Git diff stays under `almanac/`.

### P5.2 Ingest One File

Procedure:

1. Create `note.md`.
2. Run `ingest note.md --using codex`.
3. Observe jobs, logs, output, changed files.
4. Repeat with Claude.

Expected:

- One ingest job.
- Agent can read the file.
- Wiki diff is local and useful.
- Provider failures are surfaced clearly.

### P5.3 Ingest Multiple Inputs

Cases:

- two files
- folder input
- missing file
- file outside repo
- empty file
- very large file
- binary file

Expected:

- Valid inputs are summarized.
- Invalid inputs fail without half-queued nonsense.
- Large/binary behavior is explicit.

### P5.4 Garden

Procedure:

1. Run Garden in throwaway repo after ingest.
2. Run Garden with `--wiki` from outside repo.
3. Run Garden from unrelated folder without `--wiki`.
4. Run Garden when no changes are needed.

Expected:

- Garden targets the intended wiki.
- It does not need root hopping.
- No-change output is not scary.
- Changes stay under `almanac/`.

### P5.5 Auto Commit

Procedure:

1. Set `auto_commit true`.
2. Run writer operation.
3. Inspect git log and git status.
4. Set `auto_commit false`.
5. Run writer operation.
6. Inspect git log and git status.

Expected:

- True creates commit when there are wiki changes.
- False leaves working tree diff.
- Terminal output says what happened.

## Priority 6: Sync And Transcript Eligibility

Sync is subtle because it depends on real agent transcripts.

### P6.1 Sync Status

Procedure:

1. Run `codealmanac sync status`.
2. Run JSON status.
3. Check Codex and Claude transcript directories if surfaced.

Expected:

- Status says what sources are available.
- Missing source app is not a scary failure.

### P6.2 Sync Scan

Procedure:

1. Create a recent Codex transcript by running a tiny Codex session in a
   throwaway repo.
2. Create a recent Claude transcript if Claude is available.
3. Run `codealmanac sync`.
4. Inspect queued ingest jobs.

Expected:

- Recent active transcripts map to exact registered repositories.
- Nonmatching CWDs are ignored.
- Sync itself is not a job.

### P6.3 Sync Filters

Cases:

- `--wiki <name>`
- `--from codex`
- `--from claude`
- no recent transcripts
- stale transcript older than last sync
- transcript with missing CWD
- transcript from deleted repo

Expected:

- Filters do exactly what they say.
- No transcript creates a quiet no-op.
- Bad transcript metadata is skipped with useful diagnostics if surfaced.

## Priority 7: Automation And Auto Update

This is where “installed product” matters most.

### P7.1 Automation Status Truth

Procedure:

1. Run `automation status`.
2. Inspect plists.
3. Inspect `launchctl print`.
4. Compare intervals and commands.

Expected:

- CLI status agrees with launchd.
- Plists point at deployed Python, not repo Python.

### P7.2 Automation Install/Uninstall

Procedure:

1. `automation uninstall`
2. Confirm plists removed and launchd unloaded.
3. `automation install`
4. Confirm plists restored and loaded.

Expected:

- No ghost launchd jobs.
- No stale plist left behind.

### P7.3 Kick Update

Procedure:

1. Snapshot update logs.
2. `launchctl kickstart -k gui/$(id -u)/com.codealmanac.update`
3. Inspect new logs.
4. Inspect exit code through `launchctl print`.

Expected:

- Update runs noninteractively.
- It exits zero when already current.
- It reports what it would upgrade.

### P7.4 Kick Sync

Procedure:

1. Snapshot sync logs and jobs.
2. Kick launchd sync.
3. Inspect logs, jobs, DB.

Expected:

- Sync runs.
- It either queues ingest jobs or cleanly no-ops.
- It does not require terminal CWD.

### P7.5 Kick Garden

Procedure:

1. Ensure only safe throwaway repos are registered or stale behavior is known.
2. Snapshot garden logs and jobs.
3. Kick launchd garden.
4. Inspect which repositories get jobs.

Expected:

- Garden queues only available repositories.
- Duplicate queued/running Garden behavior is sensible.
- Failures are isolated per repository.

## Priority 8: Query And Organization Commands

These prove the wiki remains usable after writes.

### P8.1 Search/Show/Topics

Procedure:

1. Search for content created by init/ingest.
2. Show the page.
3. Inspect topics.
4. Run JSON variants.

Expected:

- Search finds new content.
- Show output is readable.
- JSON is scriptable.

### P8.2 Health/Validate/Reindex

Procedure:

1. Run `health`.
2. Run `validate`.
3. Run `reindex`.
4. Break a link/source in a throwaway repo and rerun.

Expected:

- Healthy repo is quiet and clear.
- Broken repo gets actionable diagnostics.
- Reindex does not corrupt state.

### P8.3 Tag/Untag

Procedure:

1. Add topic to a page.
2. Remove topic.
3. Try missing page.
4. Try missing topic.

Expected:

- Deterministic metadata edit only.
- Body content is preserved.
- Errors are clear.

## Priority 9: Terminal UX

This is not polish-only. Terminal output is behavior.

Review every command for:

- Does it say what happened?
- Does it say where files changed?
- Does it show job ID when a job is created?
- Does it tell me what to run next?
- Are errors short, concrete, and non-jargony?
- Does JSON mode stay clean?
- Are colors okay when piped or `NO_COLOR` is set?

High-risk commands:

- `setup`
- `init`
- `ingest`
- `garden`
- `sync`
- `jobs`
- `automation status`
- `doctor`
- `update`

## Priority 10: UrbanBKH Real-Life Cases

These are messy-world cases. They matter after the core flow works.

### U1 Repo Shape Cases

- brand-new empty git repo
- repo with no commit
- repo with dirty working tree
- repo with existing `almanac/`
- repo with nested package folders
- repo with spaces in path
- repo in `/tmp`
- repo deleted after registration
- repo moved after registration
- repo with huge files
- repo with binary files
- repo with symlinks

### U2 Machine State Cases

- no Codex auth
- no Claude auth
- both providers available
- only Codex available
- only Claude available
- PATH missing provider binary under launchd
- launchd job loaded but plist deleted
- plist exists but job not loaded
- DB exists but config missing
- config exists but malformed
- old stale launchd job from previous version

### U3 Command Usage Cases

- command from exact root
- command from subfolder
- command from unrelated folder
- command with `--wiki`
- command with invalid `--wiki`
- command with `--json`
- command with piped output
- `NO_COLOR=1`
- invalid arguments
- interrupted command

### U4 Operation Failure Cases

- provider refuses auth
- provider times out
- provider edits outside `almanac/`
- provider writes nothing
- provider writes invalid markdown/frontmatter
- git commit fails
- worker process dies
- user cancels running job
- duplicate scheduled jobs
- stale queued jobs

## Suggested Execution Order

1. P0 baseline and backup.
2. P1 doctor/setup default.
3. P2 config round trip.
4. P7 update automation kick.
5. P3 fresh temp repo init.
6. P4 jobs list/show/logs using existing failed jobs.
7. P5 ingest one file with Codex in throwaway repo.
8. P5 Garden in throwaway repo.
9. P7 sync kick.
10. P7 garden kick only after stale repo behavior is understood.
11. P5 repeat provider run with Claude.
12. P6 sync transcript eligibility.
13. P8 query/org commands after writes.
14. P1 setup variants and uninstall/reinstall.
15. P10 UrbanBKH messy cases.
16. P9 terminal UX pass across all observed outputs.

This order gives us product confidence early and pushes destructive or confusing
cases later.
