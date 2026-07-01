# Session 019f19ac Notes

Date: 2026-06-30.
Codex thread: `019f19ac-8db5-7631-a8d7-93540285bdb1`.

These notes preserve the first-pass context behind `README.md`. Keep the README
as the current agreement; use this file as the raw discussion record.

## Whiteboard Reading

The whiteboard sketch described a relational model with these main entities:

```text
user -> account -> repo -> branch
session -> turn
turn <-> branch
```

The `turn <-> branch` relation is many-to-many. A branch belongs to one repo.
A session has many turns. Branch identity must distinguish the same branch name
across different repositories.

The query idea at the bottom of the board was:

```sql
select distinct session_id
from turn_branch
join turns on turns.id = turn_branch.turn_id
where turn_branch.branch_id in (...)
```

After finding matching sessions, the run should load the full sessions rather
than only the matching turns.

## User Agreements Captured

CodeAlmanac has been local-first until now. The current design work is about
how the local and hosted products should fit together.

The trigger concept is branch-based for now. Branches may be called
environments if that proves to be the better abstraction.

The wiki is slow-moving context. It should update at finalization events such
as merges or commits into configured branches, not continuously from every
conversation turn.

Hosted work splits into source collection and update delivery.

Source collection v1 is centered on AI coding conversations from Codex, Claude
Code, and similar agents, plus the codebase changes related to the trigger.

The model container receives a source folder by reference. It should run the
Python CodeAlmanac update operation with repo context, commit or branch
context, and collected conversations.

Turn-level branch mapping is used for source selection. The update model still
gets entire sessions, because the agent should decide what is relevant after
reading source files.

For Codex v1, use the exposed session-wide or turn-level branch metadata even
if it is not perfect. The provider extraction function should be easy to
improve later.

Delivery is unresolved. Current candidate policies are automatic commits,
opened PRs, or per-repo/per-environment choice between them.

The CLI has three major roles: querying the repo wiki, hosted setup/inspection,
and local-lab execution.

The repo wiki stays inside the repository. Hosted may keep copies or indexes
for speed and convenience, but should not become the canonical store for code
wiki content.

## Terms Under Debate

- trigger
- finalization event
- environment
- watched branch
- source collection
- source bundle
- update run
- model container
- delivery
- local lab

## Immediate Design Pressure

The next design pass should decide whether `environment` is a real product
object or just a label over configured branches. If environments become first
class, they can own trigger policy, delivery policy, retention policy, and
source-selection rules. If they are only branches, repo settings may be enough.
