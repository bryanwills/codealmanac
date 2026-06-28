# Delivery model — how the wiki lands back in a repo

Date: 2026-06-27

## The problem

Today delivery is **PR-only**: a PR opens → run → wiki changes commit into the
PR. That's one strategy, not the model. It can't serve direct pushes,
trunk-based repos, or local work. "PR-only" must become one row in a policy
table, not the hardcoded path.

This is the blocker on exposing `build` / `ingest` in the CLI. The command is
trivial; *where the result goes* is the open question.

## Delivery is three independent dials

`choose_delivery(facts, settings)` is the only place that resolves them (the seam
MANUAL §6 already names; mechanisms stay source-blind).

```text
WHERE   the PR branch · the current branch · a dedicated almanac/ branch · the working tree (no commit)
HOW     commit & push · open/refresh a PR · write to working tree (human commits) · preview only
WHEN    on a PR event · on push · per conversation/turn · debounced (session end) · scheduled · on demand
```

## The menu of strategies (and the trade you buy)

```text
A. Commit into the PR        (today)  reviewed with code, atomic   — but needs a PR to exist
B. Commit to current branch           always fresh, no PR          — noisy history, races your WIP
C. Dedicated almanac/ branch + PR     batched, one review surface  — a second PR, can drift
D. Working-tree write, human commits  zero noise, dev owns it      — dev must actually commit
E. Scheduled batch → PR to main       predictable, low noise       — not real-time
F. Preview only (check/dashboard)     full control                 — manual, friction
```

## On "auto-commit every conversation to our branch"

It works, but the **cadence** is the problem, not the destination. Per-turn /
per-conversation commits interleave `almanac` commits with WIP — ugly on
rebase/squash, and they race the developer's own edits. Two fixes make it good:

- **Debounce, don't stream.** Deliver at a natural boundary (session end, before
  the next push, or a timer). One clean wiki commit, not twelve.
- **Quarantine the commits.** Always a dedicated `docs(almanac): …` commit
  (optionally `[skip ci]`), never mixed into a code commit — trivial to see,
  squash, or drop.

## Recommended defaults per context

The point of the seam: don't pick one — let context pick.

| Context | Delivery |
|---|---|
| Fork PR (can't push to fork) | open a PR |
| Own PR | commit into the PR (A — today's default) |
| Push to main / trunk-based, no PR | refresh a single `almanac/update` PR (C); or direct commit if repo opts in (B, debounced) |
| **Local lab** | write to working tree, surface in `git status`, dev commits (D, default); opt-in auto-commit to current branch, debounced + quarantined (B) |
| Scheduled | PR to main (E) |

## For the local user specifically

**Default to D (working-tree write); offer B (auto-commit) as a setting.** This
is exactly the `--auto-commit` / `--no-auto-commit` switch codealmanac already
has — so it's half-built. Why D as default:

- The change lands in the working tree → it rides along in the developer's *next*
  commit and gets reviewed when the branch is PR'd. Same "wiki reviewed with
  code" benefit as the hosted PR model, generated locally, with **zero extra
  commits and zero history pollution.**
- Hands-off users flip on B (debounced + quarantined).

So the local model is **"the wiki sits in your working tree, ready to commit"**,
not per-conversation auto-commit. Avoids the noise and the WIP races while still
being always-fresh.

## Next

Turn this into the concrete `choose_delivery(facts, settings)` decision table:

```text
inputs:   is_fork · has_open_pr · is_local · trigger_kind · repo settings
output:   one delivery strategy (where × how × when)
```

Once that table is settled, `build` / `ingest` can be wired in the CLI against a
real delivery contract instead of an implicit PR-only assumption.
