# Slice 84: CodeAlmanac Local Package Boundary

## Intent

Make the local control plane a first-class package. After slices 81-83,
`cloud/`, `wiki/`, and `engine/` have clear package ownership, but local-only
control code still lives partly in `services/` and partly in
`workflows/local_*`. That keeps the codebase teaching an old split-brain model.

This slice moves local-only code under `src/codealmanac/local/` without changing
CLI behavior, database schemas, or run semantics.

## Read Before Coding

- `MANUAL.md`
- `.almanac/README.md`
- `docs/python-port-live-agreement.md`
- `docs/reference/cosmic-python/chapter_02_repository.md`
- `docs/reference/cosmic-python/chapter_04_service_layer.md`
- `docs/reference/cosmic-python/chapter_13_dependency_injection.md`

Relevant principles:

- Cosmic Python's repository chapter says the repository pattern hides storage
  details behind a simple abstraction. Here, local control stores stay local
  store packages, not generic services.
- The service-layer chapter says use cases should sit behind thin edges. Here,
  local setup/status/policy/update remain use-case packages called by the CLI
  and app composition root.
- The dependency-injection chapter says runtime wiring belongs in one
  composition root. Here, `src/codealmanac/app.py` remains the wiring point.

## Architecture Wireframe

```text
src/codealmanac/local/
  control/             # user-level local control DB and trigger/run rows
  hooks/               # local Git hook installation and status
  delivery/
    ledger/            # delivery records in the local control DB
    execution/         # deterministic local delivery workflow
  runs/
    artifacts/         # request/result files for an engine run
    preparation/       # claim trigger, build source bundle, prepare workspace
    execution/         # run the model/engine and record result artifacts
    jobs/              # local jobs/status read surface
    worker/            # compose preparation -> execution -> delivery
  policies/            # branch trigger and delivery policy updates
  setup/               # local setup workflow
  status/              # local status workflow
  update/              # manual local update workflow
```

Call feel after the move:

```python
app.local.control.record_trigger_event(...)
app.local.runs.worker.run_next(...)
app.local.delivery.execution.deliver(...)
```

The existing dataclass can keep top-level compatibility attributes for now
(`app.control`, `app.workflows.local_worker`, etc.) because CLI/tests already
call them. The important architectural improvement in this slice is import
ownership and package location.

## Scope

Move:

- `services/control -> local/control`
- `services/local_hooks -> local/hooks`
- `services/deliveries -> local/delivery/ledger`
- `services/engine_runs -> local/runs/artifacts`
- `workflows/local_setup -> local/setup`
- `workflows/local_status -> local/status`
- `workflows/local_policy -> local/policies`
- `workflows/local_update -> local/update`
- `workflows/local_jobs -> local/runs/jobs`
- `workflows/local_runs -> local/runs/preparation`
- `workflows/local_engine -> local/runs/execution`
- `workflows/local_worker -> local/runs/worker`
- `workflows/local_delivery -> local/delivery/execution`

Update:

- imports in `src/`, `tests/`, and active launch/refactor docs
- architecture tests so old local service/workflow source roots cannot return
- `src/codealmanac/app.py` imports only local-control code from
  `codealmanac.local.*`

## Out Of Scope

- DB table or column renames
- CLI command behavior changes
- class/model renames such as `EngineRunsService`
- moving root package resources `prompts/` or `manual/`
- hosted repo changes
- merging old repo-local `.almanac/jobs` lifecycle queue concepts with the new
  local control-plane run concepts

Those belong in later slices, especially the planned local run-name collapse.

## Verification

Focused:

```bash
uv run pytest tests/test_architecture.py \
  tests/test_control_service.py \
  tests/test_local_setup_workflow.py \
  tests/test_local_status_workflow.py \
  tests/test_local_policy_workflow.py \
  tests/test_local_run_preparation_workflow.py \
  tests/test_local_engine_workflow.py \
  tests/test_local_delivery_workflow.py \
  tests/test_local_worker_workflow.py \
  tests/test_local_update_workflow.py \
  tests/test_local_hooks.py \
  tests/test_engine_runs_service.py \
  tests/test_deliveries_service.py
```

Full:

```bash
uv run ruff check src tests
uv run pytest -q --tb=short
git diff --check
```

## Documentation Updates

- `docs/refactor-audit-2026-07-03-hosted-local-architecture/target-architecture.md`
- `docs/refactor-audit-2026-07-03-hosted-local-architecture/refactor-roadmap.md`
- `docs/refactor-audit-2026-07-03-hosted-local-architecture/worklog.md`
- `docs/codealmanac-launch/progress.md`
- `docs/codealmanac-launch/next-agent-brief.md`
- `docs/codealmanac-launch/verification-matrix.md`
- `docs/codealmanac-launch/worklog.md`
