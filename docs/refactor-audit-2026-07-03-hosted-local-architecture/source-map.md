# Current Source Map

## `codealmanac`

Current root package:

```text
src/codealmanac/
  app.py
  cli/
  core/
  database/
  integrations/
  maintenance/
  manual/
  prompts/
  server/
  services/
  workflows/
```

Current service folders:

```text
automation
cloud_auth
cloud_capture
cloud_repositories
cloud_runs
config
control
deliveries
diagnostics
engine_runs
harnesses
health
index
local_hooks
pages
runs
search
setup
source_bundles
sources
tagging
topics
updates
viewer
wiki
worker_workspaces
workspaces
```

Current workflow folders:

```text
cloud_login
cloud_open
cloud_repo
cloud_runs
cloud_status
garden
ingest
init
local_delivery
local_engine
local_jobs
local_policy
local_runs
local_setup
local_status
local_update
local_worker
page_run
run_queue
sync
```

### Main Smells

- `services` and `workflows` both contain product verbs.
- `runs`, `engine_runs`, `local_runs`, `local_jobs`, and `run_queue` are hard to distinguish by name.
- `cloud_*` services are client/product adapters for the hosted API, not local domain services.
- `control/store.py` is large enough to hide multiple concepts.
- `app.py` is a valid composition root in intent, but it imports and wires too many similarly named concepts.

## `codealmanac-hosted`

Current backend package:

```text
backend/src/almanac/
  app.py
  core/
  db/
  integrations/
  messages/
  server/
  services/
  utils/
  wiring/

backend/modal_app/
```

Current hosted services:

```text
access
analytics
billing
capture_tokens
cli_tokens
conversations
events
github
identity
repositories
source_artifacts
updates
wiki
```

### Main Smells

- Package name is still `almanac`, while the product/repo is `codealmanac-hosted`.
- `updates` owns too many different product reasons to change.
- `modal_app` is top-level, but the Modal worker is a hosted edge and should live with backend source.
- `messages` and `wiring/fanout` form an event bus, but the naming hides that.
- `capture_tokens` and `cli_tokens` need review against the WorkOS-backed auth decision.
- Some old `usealmanac` provider names still exist in deployment history and docs.

