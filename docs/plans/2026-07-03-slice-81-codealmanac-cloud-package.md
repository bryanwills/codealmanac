# Slice 81 — CodeAlmanac cloud package boundary

## Scope

Move the local package's cloud-facing code out of the generic
`services/cloud_*` and `workflows/cloud_*` folders into a first-class
`codealmanac.cloud` package.

This slice is about code organization, not public behavior.

## Why This Slice

The launch model says cloud is the default product path, while local remains a
clear explicit surface. The current package shape hides that:

```text
services/cloud_auth
services/cloud_capture
services/cloud_repositories
services/cloud_runs
workflows/cloud_login
workflows/cloud_open
workflows/cloud_repo
workflows/cloud_runs
workflows/cloud_status
```

Those modules are not generic services or generic workflows. They are the
client-side cloud product surface used by the CLI.

## Target Shape

```text
src/codealmanac/cloud/
  __init__.py
  auth/
    models.py
    ports.py
    requests.py
    service.py
    store.py
    login_models.py
    login_ports.py
    login_requests.py
    login_workflow.py
  capture/
    event_store.py
    models.py
    ports.py
    requests.py
    service.py
    store.py
  repositories/
    models.py
    ports.py
    requests.py
    service.py
    workflow_models.py
    workflow_requests.py
    workflow.py
  runs/
    models.py
    ports.py
    requests.py
    service.py
    workflow_models.py
    workflow_requests.py
    workflow.py
  open/
    models.py
    requests.py
    workflow.py
  status/
    models.py
    requests.py
    workflow.py
```

The CLI remains the terminal edge. `codealmanac.cloud` is the local package's
client-side cloud domain.

## Decisions

- Do not leave compatibility modules under `services/cloud_*` or
  `workflows/cloud_*` once imports have moved.
- Keep class names stable in this slice. Rename modules first, concepts later
  only if the tests and docs show clearer names.
- Keep `integrations/cloud/http.py` as a provider adapter. It should import the
  new cloud models but remain under `integrations`.
- Keep CLI parser/render modules in `cli/`; they are terminal presentation, not
  product logic.

## Read Before Coding

- `MANUAL.md`
- `.almanac/README.md`
- `docs/refactor-audit-2026-07-03-hosted-local-architecture/target-architecture.md`
- `docs/refactor-audit-2026-07-03-hosted-local-architecture/refactor-roadmap.md`
- `docs/reference/cosmic-python/chapter_04_service_layer.md`
- `docs/reference/cosmic-python/chapter_13_dependency_injection.md`
- Wiki pages:
  - `github-native-wiki-maintenance`
  - `evidence-bundles`

Relevant Cosmic pressure: edges call a service/use-case layer; composition
roots wire concrete adapters. This slice moves the cloud use-case layer into a
package whose name matches the product boundary.

## Implementation

1. Create `src/codealmanac/cloud/`.
2. Move cloud auth service files and login workflow files into
   `cloud/auth/`.
3. Move cloud capture files into `cloud/capture/`.
4. Move cloud repository service and workflow files into
   `cloud/repositories/`.
5. Move cloud run service and workflow files into `cloud/runs/`.
6. Move cloud open and status workflows into `cloud/open/` and
   `cloud/status/`.
7. Rewrite imports across `src/` and `tests/`.
8. Add or update an architecture test that forbids new imports from
   `codealmanac.services.cloud_*` and `codealmanac.workflows.cloud_*`.
9. Update refactor audit docs and launch worklog.

## Verification

Focused:

```bash
uv run pytest \
  tests/test_cloud_auth_service.py \
  tests/test_cloud_login_workflow.py \
  tests/test_cloud_open_workflow.py \
  tests/test_cloud_repo_workflow.py \
  tests/test_cloud_repositories_service.py \
  tests/test_cloud_runs_service.py \
  tests/test_cloud_runs_workflow.py \
  tests/test_cloud_capture_service.py \
  tests/test_capture_transcript_upload.py \
  tests/test_setup_service.py \
  tests/test_cli.py \
  tests/test_architecture.py -q
```

Gates:

```bash
uv run ruff check src tests
uv run pytest
git diff --check
```

No Vercel/Render/Modal deploy is required because this slice only changes the
local package's internal import paths. A PyPI publish is not required until a
behavioral or public-package release slice.

## Out Of Scope

- Hosted package rename.
- Hosted `updates` split.
- Local wiki/engine/local package moves.
- CLI command renames.
- Changing WorkOS/capture credentials.

