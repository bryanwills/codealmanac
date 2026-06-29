# Python Port Product Debt

Updated: 2026-06-29

This file lists old assumptions that future agents must not accidentally keep
alive while rebuilding in Python.

## Quarantined Assumptions

| Assumption | Status | Reason |
|---|---|---|
| Hosted CLI verbs such as `login`, `connect`, `upload` | out of scope | Python v1 is local-only. Hosted control plane work belongs to a later agreement. |
| Public `almanac`, `alm`, or `absorb` aliases | out of scope | Public naming is `codealmanac`; compatibility aliases were explicitly rejected. |
| `capture` as a public command | out of scope | Conversation collection belongs under `sync` or a future explicit local source workflow. |
| CLI shell-out as an internal API | forbidden | Automation and future server wrappers must call Python services/workflows directly. |
| Hosted-shipping work merged from `origin/dev` | archive/reference only | The branch may contain hosted assumptions that are not v1 product direction. |
| TypeScript module boundaries | archive/reference only | The old code is behavior evidence, not a shape to preserve. |
| Semantic/vector search | out of scope | FTS5 and explicit refs come first. |
| `.almanac/wiki/` nesting | forbidden | `.almanac/` remains flat; future files are peers. |

## Open Debts To Resolve During Slices

| Debt | Pressure test |
|---|---|
| `jobs` vs `runs` public noun | Decide before implementing the run ledger CLI surface. |
| Local `add` command | Decide only when source-pool behavior is concrete. |
| `serve` slice timing | Restore after core read model works unless a viewer need becomes the highest-risk boundary. |
| Agent harness contract | Re-evaluate old Codex app-server and Claude SDK adapters before implementing lifecycle workflows. |
| Codex app-server parity | The Python v1 Codex adapter uses `codex exec`; port app-server only if the harness contract needs streaming, usage, structured tool display, structured output, or subagents. |
| Sync execution internal-session exclusion | Before full `codealmanac sync` runs ingest, harness runs must record provider session ids or transcript paths so sync can skip CodeAlmanac's own Ingest/Garden transcripts. |
| Update/self-update behavior | Keep command surface, but avoid npm-era assumptions when packaging Python. |
| Index refresh cost | `ensure_fresh` skips unchanged projection writes using source signatures, but still parses page markdown to compute them. Optimize only after real large-repo dogfood shows this is too slow. |
