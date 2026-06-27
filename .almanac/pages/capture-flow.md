---
title: Sync Flow
summary: >-
  `almanac sync` discovers quiet Claude and Codex transcripts, maps them to repo wikis, and starts
  background Absorb runs for uncaptured transcript ranges.
topics:
  - agents
  - flows
sources:
  - id: operations
    type: file
    path: src/cli/commands/operations.ts
    note: Migrated from legacy files.
  - id: register-sync-commands
    type: file
    path: src/edges/cli/register-sync-commands.ts
    note: Registers sync command adapters at the CLI edge.
  - id: absorb
    type: file
    path: src/operations/absorb.ts
    note: Migrated from legacy files.
  - id: absorb-2
    type: file
    path: prompts/operations/absorb.md
    note: Migrated from legacy files.
  - id: sync
    type: file
    path: src/cli/commands/sync.ts
    note: Migrated from legacy files.
  - id: discovery
    type: file
    path: src/sync/discovery/
    note: Migrated from legacy files.
  - id: jsonl
    type: file
    path: src/sync/discovery/jsonl.ts
    note: Migrated from legacy files.
  - id: ledger
    type: file
    path: src/sync/ledger.ts
    note: Owns cursor math and pending-run reconciliation semantics.
  - id: lock
    type: file
    path: src/stores/sync/lock.ts
    note: Owns repo-level sync lock files and stale-lock recovery.
  - id: ledger-store
    type: file
    path: src/stores/sync/ledger.ts
    note: Owns repo-local sync ledger JSON files and legacy reads.
  - id: sweep
    type: file
    path: src/sync/sweep.ts
    note: Migrated from legacy files.
  - id: background
    type: file
    path: src/jobs/start.ts
    note: Migrated from legacy files.
  - id: automation
    type: file
    path: src/cli/commands/automation.ts
    note: Migrated from legacy files.
  - id: pricing
    type: web
    url: https://openai.com/api/pricing/
    note: Migrated from legacy sources.
  - id: gpt-5
    type: web
    url: https://developers.openai.com/api/docs/models/gpt-5.5
    note: Migrated from legacy sources.
  - id: capture-discovery-cwd
    type: file
    path: src/sync/discovery/jsonl.ts
    note: Candidate discovery maps each transcript's recorded cwd to the nearest repo root containing .almanac.
  - id: absorb-noop-contract
    type: file
    path: prompts/operations/absorb.md
    note: The Absorb prompt says transcript inputs are raw material and instructs the agent to no-op when the input does not improve durable project memory.
  - id: capture-session-2026-06-09
    type: conversation
    path: /Users/kushagrachitkara/.codex/sessions/2026/06/09/rollout-2026-06-09T10-54-13-019ead85-4907-76b2-b07f-2f843f0d836a.jsonl
    note: Records a Codex maintenance session that left a repo-mapped but project-unrelated transcript note uncommitted, clarifying the boundary between repo ownership and project relevance.
  - >-
    /Users/kushagrachitkara/.codex/sessions/2026/05/11/rollout-2026-05-11T14-32-08-019e18f4-5e73-7790-ba49-73cc02544a58.jsonl
  - >-
    /Users/kushagrachitkara/.codex/sessions/2026/05/11/rollout-2026-05-11T21-33-50-019e1a76-701d-7583-a76c-b3739632ee9b.jsonl
  - >-
    /Users/kushagrachitkara/.codex/sessions/2026/05/12/rollout-2026-05-12T20-25-14-019e1f5d-ff59-7ee1-a73b-836277d8092b.jsonl
  - docs/plans/2026-05-14-provider-automation-boundary-refactor.md
  - >-
    /Users/rohan/.codex/sessions/2026/05/13/rollout-2026-05-13T23-00-06-019e246d-595d-76d3-bd45-6433245065ac.jsonl
  - >-
    /Users/rohan/.codex/sessions/2026/05/14/rollout-2026-05-14T12-03-51-019e273a-e4b1-7510-981d-d1deb31bc8e2.jsonl
  - >-
    /Users/rohan/.codex/sessions/2026/05/14/rollout-2026-05-14T12-11-57-019e2742-4c9c-7241-8ccd-a6d36a889d7d.jsonl
  - >-
    /Users/rohan/.codex/sessions/2026/05/28/rollout-2026-05-28T18-27-05-019e70e9-b7d7-7900-9fc0-da2a6f0b532d.jsonl
verified: 2026-06-09
---

# Sync Flow

`almanac sync` is the quiet-transcript coordinator for the V1 Absorb operation. It scans Claude and Codex session stores, maps transcript candidates to repos with `.almanac/`, applies the activation and quiet-window rules, reconciles repo-local ledger state, and starts background [[wiki-lifecycle-operations|Absorb]] runs with `targetKind: "session"` for ranges the ledger does not yet own. Those runs then go through [[process-manager-runs]] and [[harness-providers]] like every other AI write path.

The old hardcoded writer/reviewer capture pipeline was removed. There is no `prompts/writer.md`, `prompts/reviewer.md`, `src/cli/commands/capture.ts`, `src/agent/sdk.ts`, or capture-specific `StreamingFormatter` in V1. Old root-level `.capture-*.log` provider logs were replaced by [[process-manager-runs]] JSON/JSONL records.

## Transcript inputs are raw evidence

Capture should treat session transcripts as raw evidence, not as trustworthy summaries or wiki-ready prose. A 2026-05-11 Codex capture discussion included a long accidental tool-output dump from another repo's config and test run, including sensitive-looking values mixed with otherwise irrelevant debugging output. The durable lesson is broader than that one incident: transcript files can contain large raw command output, noisy detours, and accidental data exposure.

For Absorb, that means the unit of value is the conclusion the agent can verify from the transcript, not the transcript text itself. Durable implementation or product understanding may still belong in the wiki, but raw blobs, copied secrets, and incidental debug output do not. This matches the prompt doctrine that inputs are raw material rather than outputs.

Transcript tails can also be incomplete. A 2026-05-14 Codex transcript ended after the user asked for an architecture design plan and after the assistant promised to write it, but before any plan file was created or final answer was recorded. Absorb should treat trailing intentions and in-progress commentary as weaker evidence than completed commands, diffs, or final answers.

The same lesson shapes transcript discovery tooling, not just wiki prose. The scheduled sweep's metadata pass only reads an initial header chunk and first lines to recover fields such as session id and cwd, instead of eagerly loading whole transcript files during candidate discovery. That keeps the cheap path cheap, but it also limits how much noisy or sensitive transcript content routine automation touches before a session is even eligible for capture.

Almanac maintenance jobs request non-persistent provider sessions through `OperationSpec.providerSession.persistence = "ephemeral"` and keep their durable transcript under `.almanac/jobs/`. Sync discovery no longer scans provider transcript contents for CodeAlmanac marker environment variables; the prevention path is to avoid creating provider-history maintenance transcripts in the first place.

Later turns in the same 2026-05-11 session pushed this one step further for actual Absorb work: large JSONL transcripts should be treated as structured event streams, not as text blobs to read linearly into context. The durable recommendation was to extract the useful capture signal structurally:

- user asks and clarifications
- assistant decisions and final answers
- commands run plus short outcomes
- touched files
- explicit errors, fixes, and durable implementation notes

Repeated JSON envelopes, long tool schemas, verbose stdout, and other raw payloads may dominate transcript size without adding wiki value. The rough estimate from the session was that a very large first-run corpus can shrink dramatically once reduced to capture-relevant signal. That is a cost-model conclusion, not a claim that current code already performs this reduction.

The same transcript also exposed a concrete Codex-specific version of that noise pattern: naive text search can get swamped by the opening `session_meta` payload, repeated `turn_context` blocks, and serialized tool catalogs before it reaches the user/problem signal. Future transcript tooling should therefore prefer event-type-aware extraction over generic line-oriented grep whenever it is trying to recover capture-relevant meaning rather than debug the transcript format itself.

A short 2026-05-12 Codex transcript made that asymmetry concrete. The user asked one short question and the assistant answered `hello`, but the saved JSONL still reached `192` lines and `650,091` bytes because the opening `session_meta` record embedded the full global and project instruction text, and later records repeated desktop app context and tool metadata. That means transcript volume can be dominated by harness scaffolding even when the human-visible conversation is trivial.

A 2026-05-20 Codex Desktop transcript sharpened that point with a session that was completely unrelated to CodeAlmanac implementation. The human-visible conversation was about rewriting recommendation-letter anecdotes, but the saved JSONL still carried large developer app-context blocks advertising desktop-only capabilities such as `automation_update`, `load_workspace_dependencies`, inline `::code-comment` / `::archive` directives, and git UI directives. Capture should treat those repeated capability manifests as harness metadata, not as project evidence or new repo instructions, unless the session itself is explicitly about those app features.

A later Codex subagent experiment sharpened that cost-model warning with real usage data. A helper agent was asked to read and summarize a `716,942`-byte / `414`-line session transcript whose naive `chars / 4` estimate was about `179k` tokens. The helper's own Codex transcript finished at `315,173` cumulative `total_tokens`, with `260,992` of those counted as cached input. The durable lesson is that transcript size is not a reliable proxy for actual capture cost once the agent takes multiple turns, carries tool output forward, and benefits from cache reuse. Future optimization work should benchmark candidate capture strategies against real transcript `token_count` logs rather than assuming file-size heuristics are good enough.

The same experiment also showed why any future "estimate capture cost" feature needs a model-aware pricing rule, not just token totals. Using OpenAI's published 2026-05-12 GPT-5.5 standard rates, the run's `311,995` input tokens and `3,178` output tokens translate to a simple base-rate estimate of about `$0.48` when cached-input discounts are applied, or about `$1.66` if none of the input had been cached. But GPT-5.5's own model page also states that prompts above `272K` input tokens are billed at higher full-session rates. The durable conclusion is not the exact dollar figure from this one transcript; it is that transcript benchmarks must preserve raw token counts, cached-vs-uncached breakdown, and the pricing rule version used for the estimate.

The same experiment also exposed one archival parsing wrinkle worth preserving: raw Codex session transcripts may contain `token_count` events whose `info` payload is `null` before later events settle into the expected `last_token_usage` / `total_token_usage` shape. Any offline transcript-analysis or benchmarking helper should therefore treat `token_count` as a best-effort structured stream and skip unusable entries defensively instead of assuming every event can be parsed into usage numbers.

The same transcript family also carries another durable signal inside `token_count`: Codex logs `rate_limits` metadata alongside usage totals. The observed shape includes `primary` and `secondary` windows with `used_percent`, `window_minutes`, and `resets_at`, plus plan metadata such as `plan_type`. In the 2026-05-11/2026-05-12 capture-cost investigation, the same transcript stream showed `primary.window_minutes = 300` and `secondary.window_minutes = 10080`, which strongly suggests a short-window and long-window usage view rather than a second token counter. Importantly, `rate_limits` can still be present on early `token_count` events even when `info` is `null`, so offline parsers should treat token totals and limit telemetry as related but independently optional substructures.

The same investigation later added a more useful backlog-planning calibration by measuring a batch of ten helper-agent transcript reads instead of a single case. Across `36.95 MB` of source JSONL (`12,734` lines), the helper transcripts accumulated `2,790,928` total tokens, with `2,238,976` counted as cached input and `522,314` as uncached input. The visible Codex subscription telemetry moved from roughly `8% / 2%` (`primary` / `secondary`) before the sample to about `10% / 3%` during the second batch, with a later `11% / 3%` reading that also included some main-thread work. The durable conclusion is not the exact percentage from one day on one plan; it is that real capture-cost benchmarks should preserve three distinct signals together:

- source transcript size and line count
- token totals, including cached-vs-uncached input
- rate-limit telemetry snapshots before and after a batch

The same measurement also showed one subtle interpretation trap: first and last `used_percent` values inside an individual helper transcript can stay flat at `0` delta even when the overall account usage clearly rose across the full batch. That means any future estimator or benchmarking script should not rely only on per-transcript start/end percentages; it should also compare batch-boundary or account-level readings when interpreting subscription impact.

## Command surface

The public automatic-session command is `almanac sync`. It defaults to scanning Claude and Codex transcript stores, uses a `45m` quiet window, and starts background Absorb runs for eligible transcript continuations. `almanac sync status` runs the same discovery and cursor evaluation without enqueueing Absorb jobs or writing `sync-ledger.json`.

The currently wired flags are:

- `--from <apps>` for `claude`, `codex`, or both
- `--quiet <duration>` with a default of `45m`
- `--using <provider[/model]>`
- `--json`

The durable behavioral split is more important than the spelling of each flag:

- `sync status` is read-only and reports ready ranges
- `sync` writes sync ledger state and starts background Absorb jobs
- discovery is provider-store-specific, but the Absorb run is provider-neutral after a transcript path is selected
- `--json` emits the structured summary for agent and automation consumers

## Transcript resolution

Resolution lives under `src/sync/discovery/` and `src/sync/sweep.ts` before Absorb starts:

- `discoverClaude()` scans Claude project transcripts.
- `discoverCodex()` scans Codex session transcripts.
- Codex transcripts marked with `payload.thread_source === "subagent"` are ignored.
- Candidate records carry `app`, `sessionId`, `transcriptPath`, `repoRoot`, and `mtimeMs`.
- `executeSyncSweep()` applies the quiet window, activation baseline, internal-maintenance-session exclusion, repo lock, ledger reconciliation, and cursor decision.

The important current implementation boundary is that `runSyncCommand()` resolves concrete transcript candidates first, then starts `operations.absorb(...)` with the original absolute transcript path as the session target. There is no sync-time notion of "read only bytes N-M from this transcript" in the operation target list.

That boundary also matters at prompt-construction time. `syncAbsorbContext()` in [[src/cli/commands/sync.ts]] does not inline transcript contents into the Absorb prompt or try to pre-truncate the session into the context window. It appends a command-context block with the app, session id, transcript path, and cursor note, then relies on the Absorb agent's normal filesystem/search tools to inspect the transcript lazily in chunks as needed. For large or noisy transcripts, "sync input" means "here is the file and cursor range to examine," not "here is the whole transcript stuffed into the model context."

The scheduler path extends this resolver boundary rather than replacing it. Scheduled automation invokes `almanac sync --quiet <duration>`, and sync still starts normal background Absorb jobs with ordinary transcript paths and additional cursor context.

The first scheduled discovery implementation scans Claude transcripts under `~/.claude/projects/**/*.jsonl` and Codex transcripts under `~/.codex/sessions/**/*.jsonl`. Provider-specific transcript scanning lives under `[[src/sync/discovery/]]` because it scans historical transcript stores; it is not part of the runtime adapter boundary in `[[harness-providers]]`.

The 2026-05-13 review discussion clarified the ownership boundary for this discovery code. Claude and Codex transcript scanning is provider-specific source discovery, not [[harness-providers]] execution behavior. The transcripts being scanned are external agent-app session histories that may come from ordinary user work outside CodeAlmanac's own Build, Absorb, or Garden runs. They therefore should not be treated as harness run history, even though the scanners are app-specific.

Continuation sync keeps passing the original transcript path into Absorb, and adds cursor context telling Absorb what transcript prefix was already absorbed. That preserves the "agent inspects files lazily" contract while avoiding temp delta transcript files or byte-range semantics.

The sweep's state helpers are split by ownership. `[[src/stores/sync/ledger.ts]]` owns repo-local ledger loading, atomic writes, and legacy `capture-ledger.json` reads. `[[src/stores/sync/lock.ts]]` owns repo-level sync locking and stale-lock recovery. `[[src/sync/ledger.ts]]` owns pending-run reconciliation, prefix hashes, and initial cursor calculation. `[[src/sync/sweep.ts]]` owns the coordinator: eligibility checks, internal session filtering, lock acquisition, ledger reconciliation, cursor validation, Absorb enqueueing, cursor context, start-result handling, and summary construction. Its top-level loop should stay a coordinator over named helpers such as candidate eligibility, transcript snapshot reading, cursor decision, enqueue, and summary recording. `[[src/cli/commands/sync.ts]]` parses CLI options, loads config and discovery inputs, adapts `operations.absorb(...)` to a typed sync-start result, and renders command output.

The current sync implementation makes that continuation context explicit in the saved run spec. `cursorContext()` in [[src/sync/sweep.ts]] appends a cursor note with the transcript identity and cursor boundary:

```text
Sync cursor:
- App: codex|claude
- Session id: <session-id>
- Transcript: <absolute transcript path>
- Previously absorbed through line: <N>
- Previously absorbed through byte: <B>
- Focus on line <N+1> onward.
- You may inspect earlier lines only for context.
- Do not re-document decisions already captured unless newer lines amend, invalidate, or add important nuance to them.
```

This matters operationally because the prompt does not inline the uncaptured chat tail. When an operator wants to verify why a job became eligible or what slice of an active conversation Absorb was asked to analyze, the authoritative artifact is `.almanac/jobs/<job-id>.spec.json`, not the viewer transcript alone.

One open operational consequence from the same session is that "pass the original transcript path" is still compatible with a smarter first step inside Absorb. Future prompt or tooling work can keep the current command surface while instructing the agent to parse JSONL structurally before reading deeply, and can optionally add a cheap preflight size estimator or cap for unusually large first-run backlogs. Neither behavior is part of the current implementation.

Discovery first tries to match transcripts by directory name hash, which is the fast path with no transcript-content IO. If no matches are found, it falls back to content scanning: each transcript is opened, and `readHead(path, 4096)` checks whether the first 4 KB contains `"cwd":"<repoRoot>"`. One known performance issue remains in that fallback: `readHead` currently calls `readFile()` to load the entire file into memory before slicing. On a Claude projects directory with many large session files this causes hundreds of MB of unnecessary IO at `almanac sync` startup. The fix is to use `fs.open().read()` or a bounded stream limited to 4,096 bytes.

## Sync status semantics

`almanac sync status` is the verification path. It discovers the same candidates and computes the same cursor ranges as a live sync, but it does not enqueue Absorb jobs or create/update [[capture-ledger|sync ledger]] state. This keeps the current CLI aligned with the repo's "no dry-run flags" doctrine while preserving the operator need to see which transcript ranges are ready.

## Absorb execution

Sync appends session-file context to `prompts/operations/absorb.md` through [[operation-prompts]]. `src/operations/absorb.ts` requests read, write, edit, search, and shell tools, sets `metadata.operation = "absorb"`, and `src/cli/commands/sync.ts` always starts background Absorb jobs for eligible transcripts.

Provider-specific behavior is adapter-owned. Claude may support helper agents through [[harness-providers]], but Capture no longer hardcodes a reviewer subagent or a capture-only SDK wrapper.

## No-op sync runs

Sync-started Absorb jobs can produce no page changes if the transcript does not meet the notability bar. In V1 the observable record is a completed job with zero created, updated, and archived pages in `.almanac/jobs/`.

Repo mapping is only an ownership decision, not a relevance decision. Discovery maps a transcript to a wiki by recovering its recorded `cwd` and walking upward to the nearest `.almanac/`, but Absorb still has to decide whether the conversation improves durable project memory. A 2026-06-09 Codex maintenance session preserved that boundary explicitly: a local wiki edit that referenced a personal, repo-unrelated transcript was deliberately left uncommitted because repo attribution alone did not make the session relevant to CodeAlmanac. [@capture-discovery-cwd] [@absorb-noop-contract] [@capture-session-2026-06-09]

## Log files

Raw provider events are normalized and written to `.almanac/jobs/<job-id>.jsonl`. Job status, target paths, provider/model, PID, summary counts, and errors live in `.almanac/jobs/<job-id>.json`.

## Scheduled automation

Automatic session sync is scheduler-driven. `almanac automation install` writes a macOS launchd plist that runs `almanac sync --quiet 45m` every 5h by default, alongside the separate scheduled Garden plist described in [[capture-automation]]. Sync applies quiet-window and ledger rules in-process, so launchd is only the wakeup mechanism; it does not own transcript state.
