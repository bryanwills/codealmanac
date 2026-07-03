# Slice 64: Production CLI Endpoint Smoke

## Goal

Make the public CLI path match the production product path:

```text
uv tool install codealmanac
codealmanac setup
```

The CLI should use canonical CodeAlmanac URLs by default, work through the
production Chrome/AuthKit approval flow, and leave no stale Render or old Node
binary surprise in the launch notes.

## Pre-Plan Evidence

- Source CLI `uv run codealmanac login --api-url https://api.codealmanac.com`
  completed the browser approval flow in Chrome.
- The approval page showed `CLI login approved`.
- The CLI stored auth and `whoami` returned `Signed in as rohans0509`.
- `capture enable --target codex` issued a cloud capture credential and wrote a
  hook under a temp HOME.
- `capture disable --target codex` revoked that credential and removed the hook.
- The repo default still points at
  `https://codealmanac-backend-docker.onrender.com`.
- The machine PATH has an old Node-era `codealmanac` before the Python binary:
  `/Users/rohan/.nvm/versions/node/v21.7.3/bin/codealmanac`.

## Scope

- Change public cloud defaults to:
  - API: `https://api.codealmanac.com`
  - App: `https://www.codealmanac.com`
- Update tests and launch docs that assert or explain the public defaults.
- Add a concise note for stale PATH installs and the exact cleanup/install
  command.
- Smoke-test an isolated PyPI-style install with temp `UV_TOOL_DIR`,
  `UV_TOOL_BIN_DIR`, and `HOME`.
- Publish a new PyPI version only if the installed public package still ships
  the non-canonical default.

## Out Of Scope

- Reworking WorkOS AuthKit architecture.
- Moving capture credentials to WorkOS API Keys.
- Changing GitHub webhook reconciliation.
- Editing the user-modified `README.md` unless the release test proves the
  install command itself is misleading.

## Design

The default URL is composition/configuration, not workflow logic. Keep it in
`services.cloud_auth.models` where existing request models already import it.
The CLI remains a thin adapter over services/workflows.

```python
login_request = RunCloudLoginRequest(api_url=DEFAULT_CLOUD_API_URL)
setup_request = RunSetupRequest(api_url=DEFAULT_CLOUD_API_URL)
repo_request = CloudRepositoryRequest(api_url=DEFAULT_CLOUD_API_URL)
```

The source of truth should be one constant used by login, setup, capture, repo
commands, and cloud open.

## Verification

- `uv run pytest` targeted tests for cloud auth/setup/capture defaults.
- `uv run ruff check .`
- Isolated source CLI login/setup/capture smoke against production.
- Isolated installed CLI smoke using `uv tool install codealmanac`.
- Confirm no remote capture credential is left behind after the smoke test.

## Risk

The only risky part is publishing. If PyPI publish is needed, verify from a
fresh isolated tool install after the workflow completes.
