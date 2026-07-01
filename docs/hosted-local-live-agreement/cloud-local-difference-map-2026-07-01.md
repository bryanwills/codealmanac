# Cloud And Local Difference Map

Date: 2026-07-01.
Status: active design inventory.

This file lists the steps where cloud and local can legitimately differ. The
goal is to avoid pretending they are the same workflow when the infrastructure
and trust boundaries are different.

## End-To-End Flow

Shared conceptual flow:

```text
configure
  -> capture/collect sources
  -> observe a finalization event
  -> select relevant source sessions
  -> materialize source bundle
  -> run engine
  -> produce wiki diff
  -> deliver diff
  -> inspect result
```

Cloud and local can differ at every step except the final artifact:

```text
repo-owned wiki files are still the shared artifact
```

## Step Differences

| Step | Cloud default | Local opt-in |
| --- | --- | --- |
| Setup | login/connect, GitHub App, repo selection, default environments | initialize local repo root and local config |
| Identity | cloud account, GitHub installation, team permissions | current OS user and repo checkout |
| Config storage | cloud DB plus repo-safe settings where useful | repo config plus local user config |
| Finalization event | GitHub events, PR merge, environment branch changes, manual dashboard run, scheduled run | manual CLI, local schedule, local agent hook, local commit/merge |
| Source capture | agent hooks accumulate sessions/turn metadata in cloud source library | optional local transcript discovery/capture |
| Branch mapping | cloud stores turn-to-branch mapping for source selection | local can infer from current checkout/transcript metadata |
| Source bundle | selected full sessions and GitHub/repo context mounted into worker | local folder assembled in repo/temp state |
| Engine execution | cloud worker/container with managed credentials | local process with user credentials |
| Model credentials | cloud-managed or cloud-orchestrated | user's local model/API credentials |
| Run state | cloud run rows, dashboard, events | local run ledger/files/SQLite |
| Delivery | PR, direct commit, dedicated branch, preview/check | working tree write by default, optional local commit |
| Billing/quota | cloud billing and run limits | none, user pays local compute/API costs |
| Privacy/delete | cloud retention and deletion policy for uploaded sources | user controls local files |
| Failure surface | dashboard, GitHub checks, CLI cloud status | terminal output and local logs |

## Finalization Event Differences

Cloud finalization events should be repo/team events:

```text
PR merged to main
PR merged to dev
commit to watched environment branch
manual dashboard run
scheduled update
GitHub App check action
```

Local finalization events can be personal-machine events:

```text
manual CLI run
local schedule
agent session end
before push
local quiet-window capture
local commit or merge
```

These are not the same product behavior. Cloud triggers should be reliable team
automation. Local triggers are a convenience/lab workflow.

PR open or PR update is a possible cloud event, but it should not force a wiki
update by default. It can be used to collect context or to run previews/checks.
The default durable update should happen when the PR is merged into a maintained
environment branch, or when another configured finalization event fires.

## Delivery Differences

Cloud delivery is GitHub-native:

```text
open follow-up PR
refresh follow-up PR
commit to maintained branch
update the still-open PR branch, if explicitly enabled
commit to dedicated almanac branch
preview/check only
```

Local delivery should default to working-tree writes:

```text
write .almanac changes to working tree
user sees git status
user commits with code
```

Optional local auto-commit can exist, but it should be explicit and debounced.

## Source-Capture Differences

Cloud capture:

```text
agent hook records turn/session metadata
uploads source material or source references
server stores provider, session, turn, repo, branch mapping
later cloud runs select full sessions
```

Local capture:

```text
agent hook or scanner reads local transcripts
local run selects sources directly from disk
no cloud retention policy needed
```

Cloud capture must have an explicit installation command and a deletion story.
Local capture is optional.

## Commands That Need Posture Clarity

These commands are ambiguous and should show or accept posture:

```text
runs
status
setup
agents install
update/build/garden
sources
doctor
config
```

Possible contract:

```bash
almanac runs          # cloud by default
almanac runs --local

almanac status        # shows cloud connection and local repo status
almanac status --local

almanac update        # cloud by default when connected
almanac update --local
```

Read commands are not ambiguous:

```bash
almanac search
almanac show
almanac topics
almanac health
```

They read the current checkout's wiki.

## Architecture Consequence

The engine must not be hidden inside the CLI command implementation.

The core should expose service/workflow operations that both cloud workers and
local CLI commands can call:

```text
CollectSourcesRequest
BuildSourceBundleRequest
RunUpdateRequest
SelectDeliveryRequest
ApplyDeliveryRequest
InspectRunRequest
```

The names are placeholders. The principle is stable: CLI and cloud are adapters
over shared operation contracts.

## Open Questions To Discuss

1. Which commands should cloud-default immediately?
2. Should `almanac update` exist as a cloud command, or should cloud updates be
   started only from dashboard/GitHub triggers at first?
3. What is the exact separate command for installing cloud capture hooks:
   `agents install`, `capture install`, or `sources install`?
4. Should local capture exist in v1, or should local be read/manual only?
5. Should cloud settings live only in cloud DB, or should a repo config file
   record the selected environments for transparency?
6. Should the CLI have an explicit `almanac cloud ...` namespace, or rely on
   default cloud posture plus `--local`?
