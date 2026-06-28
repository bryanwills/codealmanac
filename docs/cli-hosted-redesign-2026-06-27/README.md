# codealmanac hosted redesign — 2026-06-27

Working synthesis from a product/architecture session on how `codealmanac`
(open-source CLI + engine) and `usealmanac` (hosted, paid) should relate, what
the CLI should become, and how delivery should work.

This is design thinking, not a committed plan. Code is truth; revise when the
codebase disagrees.

## Files

- [`cli-current-vs-final.html`](./cli-current-vs-final.html) — every CLI command,
  current behaviour → final behaviour, grouped by zone. Open in a browser.
- [`delivery-model.md`](./delivery-model.md) — how the wiki should be delivered
  back into a repo (beyond PR-only).

---

## The mental model

There are three repos but five distinct things. Naming collisions are the main
source of confusion, not the architecture.

| Layer | What it is | Where it lives |
|---|---|---|
| **Artifact** | the `.almanac/` wiki format (markdown pages + topics + index) | in the repo, committed |
| **Engine** | the brain that reads sources and writes pages | shared (today: TS engine; Python re-port exists) |
| **Local CLI** | `codealmanac` — read locally; optionally build locally | npm package, OSS |
| **Hosted control plane** | `usealmanac` — teams, auth, billing, GitHub App, runs | hosted, paid |
| **Worker** | Modal sandbox that runs the engine with zero policy | hosted infra |

`/almanac` (the Python general-knowledge wiki) is a **separate product** and is
out of scope here. The "Almanac" brand is reserved for it; **the code product is
branded `codealmanac` end to end** (binary, package, hosted).

## Open-core principle

`codealmanac` ↔ `usealmanac` are **one product, two tiers** (open-core, like
GitLab CE/EE or Sentry self-hosted/Cloud) — *not* framework-vs-platform like
Next.js/Vercel. So they share one brand, distinguished by a qualifier, with
**one CLI**. Do not split into two confusingly-similar names.

The free/paid line is **not which commands exist** — it is *who runs the engine,
where, and for whom*:

> **Free** = your machine, your keys, your effort. **Paid** = our machine, our
> compute, automatic, your whole team. Same engine, same brain. Paid is never
> *smarter*, only *less work*.

Avoid the open-core trap: never cripple the OSS engine to force payment. The free
CLI is the distribution funnel. Teams pay for automation + collaboration +
hosted compute they cannot replicate alone, not for an unlocked "real version".

## One binary, capabilities unlock by setup/login

Think of `codealmanac` as one tool with layers (like `git` porcelain/plumbing,
or `gh`/`supabase` where hosted unlocks via `login`):

```text
Layer 0 — READ        no setup       search / show / serve        (the agent path; everyone)
Layer 1 — HOSTED      login          build / runs / repos         (the assumed center, paid)
Layer 2 — LOCAL LAB   opt-in install init --local / sync / garden (the experimenter path)
```

## The reading correction (load-bearing)

**Reading is always local file access.** `search` / `show` / `serve` read the
`.almanac/` already in the repo checkout. They must **never** proxy to the hosted
API. By the time there's anything to read, hosted has written it into the repo
and the developer has pulled it.

```text
hosted   = the WRITER     builds the wiki, commits it into the repo (GitHub App)
git/repo = the MEDIUM     the .almanac/ files live here; the two sides meet here
local    = the READER     show / search read those files off disk
```

They are not separate systems talking over an API (not git-vs-GitHub). They are
one wiki — the repo's files — written by hosted and read locally. The handoff is
git, not an API. (The hosted `wiki/pages` read endpoints exist only for the
dashboard, which has no local checkout.)

## Wiki format: keep it branch-native

Do **not** collapse the code wiki into a single hosted-only wiki (that's the
`/almanac` model, which fits because its sources aren't a git repo). The code
product's source *is* a branched, PR-reviewed repo, so the wiki is repo-native:

- **Source of truth** = `.almanac/pages/*.md` on the default branch (git history,
  in-PR review, point-in-time correctness, atomic with code).
- **Query layer** = a single derived index over the default branch (the
  `index.db` pattern locally; hosted DB on the server). This is the
  docs-as-code / Sourcegraph pattern: truth in the repo, one queryable index on
  top. Decoupled single wikis (GitHub Wiki, Confluence) are the staleness
  cautionary tale.

Rule that removes the ambiguity: **default branch = canonical, published wiki;
PR/feature branch = proposed next state, reviewed in the PR.**

## Posture-aware config + setup (the local-first flip)

`codealmanac` was built local-first; that assumption is now wrong. What changes:

1. **Default install posture = Reader.** A bare install runs nothing and writes
   ~nothing to config.
2. **`setup` becomes a posture chooser** (reading / connect to Cloud / enable
   local lab), and it must state *why the lab exists*.
3. **Config becomes posture-aware** (reader = empty; hosted = auth + selected
   account/repo; lab = provider + automation).
4. **`doctor` reports posture** (logged in? connected repo? lab enabled?).
5. **Automation moves fully under the lab**; hosted "automation" is the GitHub
   App running on PRs — no CLI command.

## v1 to ship first (the small section)

Hosted read + identity, with reading untouched and local:

```text
codealmanac login / logout / whoami / use <account> / repos / runs
```

Everything else is added one command at a time. `build` / `ingest` are gated on
settling **delivery** (see `delivery-model.md`) — today triggering is UI-only.
The one hard prerequisite for the read CLI is a **CLI-token endpoint** behind
`login` (usealmanac currently only has the browser-dashboard GitHub-OAuth flow).

## Open questions

- **Engine of record: TS or Python?** Modal runs the TS engine today; the Python
  core re-ports it. Two engines = drift. Pick one; demote the other.
- **`init --local` flag vs a separate lab namespace** for local execution.
- **First delivery defaults** per context (see `delivery-model.md`).
