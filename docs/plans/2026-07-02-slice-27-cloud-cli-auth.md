# Slice 27 Cloud CLI Auth Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Make the Python `codealmanac` CLI log in to CodeAlmanac cloud through the hosted WorkOS-backed CLI-login flow, then store and use the issued CLI token locally.

**Architecture:** `codealmanac-hosted` keeps the existing dashboard `/api` routes but exposes stable `/v1` aliases for externally callable CLI auth. `codealmanac` adds a small cloud-auth domain with a typed HTTP client, token store, browser opener port, and CLI renderers. `setup` becomes cloud-first by composing the same login/status service with the existing instruction installer; local-only setup remains under `codealmanac local setup`.

**Tech Stack:** FastAPI routers, Pydantic DTOs, pytest, Python `httpx`, argparse, file-backed local state under `~/.codealmanac/`, rich CLI rendering.

**Status:** Completed on 2026-07-02.

---

## Product Decisions

- Cloud is the default product surface.
- `codealmanac login`, `codealmanac whoami`, and `codealmanac logout` are public top-level commands.
- `codealmanac setup` is not repo-scoped. It logs in to cloud when needed and installs global agent instructions. It may later open browser onboarding; this slice should not require current-repo detection.
- `codealmanac local setup` remains the local repo/branch configuration command.
- The CLI stores a narrow hosted CLI token issued by the backend. It does not store WorkOS browser tokens.
- The backend continues to use WorkOS for browser session identity; CLI tokens authenticate future machine/CLI calls through `current_cli_user`.
- The model/worker runtime must use service/SDK code, not shell out to this human CLI.

## Task 1: Add Stable `/v1` Hosted CLI Auth Aliases

Files:

- Modify `backend/src/almanac/server/cli_auth_router.py`
- Modify `backend/src/almanac/server/app.py` if a separate router object is cleaner
- Modify `backend/tests/test_identity_api_contract.py` or create `backend/tests/test_cli_auth_api_contract.py`

Steps:

1. Keep existing `/api/cli/auth/sessions`, `/api/cli/me`, and `/api/cli/logout` routes for the frontend.
2. Add equivalent `/v1/auth/cli/start`, `/v1/auth/cli/sessions/{session_id}`, `/v1/auth/cli/sessions/{session_id}/complete`, and `/v1/auth/cli/sessions/{session_id}/poll` routes without duplicating service logic.
3. Add `/v1/me` for CLI-token authenticated identity, backed by `current_cli_user`.
4. Add `/v1/auth/logout` for CLI-token revocation and document it in the launch auth contract.
5. Ensure route DTO fields remain camelCase externally.
6. Add backend tests proving the `/v1` aliases call the same service methods and return the same token-once behavior.

## Task 2: Add CodeAlmanac Cloud Auth Models, Store, And HTTP Client

Files:

- Create `src/codealmanac/services/cloud_auth/models.py`
- Create `src/codealmanac/services/cloud_auth/requests.py`
- Create `src/codealmanac/services/cloud_auth/ports.py`
- Create `src/codealmanac/services/cloud_auth/store.py`
- Create `src/codealmanac/services/cloud_auth/service.py`
- Create `src/codealmanac/integrations/cloud/http.py`
- Modify `src/codealmanac/core/models.py`
- Modify `src/codealmanac/core/paths.py`
- Modify `src/codealmanac/app.py`
- Add tests in `tests/test_cloud_auth_service.py`

Steps:

1. Add `AppConfig.auth_path`, defaulting to `~/.codealmanac/auth.json`.
2. Define `CloudAuthState` with `api_url`, `token`, `github_user_id`, `github_login`, and `logged_in_at`.
3. Store only CLI token state in `auth.json` with mode `0600`; create the parent directory if missing.
4. Define a service-owned `CloudAuthClient` protocol with `start_login`, `poll_login`, `me`, and `logout`.
5. Implement `HttpCloudAuthClient` with `httpx.Client`, explicit timeouts, typed response parsing, and provider errors mapped to product errors.
6. Do not put CLI rendering or browser behavior inside the HTTP client.
7. Add tests for token save/load/delete, malformed auth file handling, and service status behavior.

## Task 3: Add Browser-Driven Login Workflow

Files:

- Create `src/codealmanac/workflows/cloud_login/models.py`
- Create `src/codealmanac/workflows/cloud_login/requests.py`
- Create `src/codealmanac/workflows/cloud_login/ports.py`
- Create `src/codealmanac/workflows/cloud_login/service.py`
- Create `src/codealmanac/integrations/browser.py`
- Modify `src/codealmanac/app.py`
- Add tests in `tests/test_cloud_login_workflow.py`

Steps:

1. Add a `BrowserOpener` port with one method that opens a URL.
2. Start a hosted login session through the cloud auth service.
3. Open the returned `verification_url` unless `--no-browser` is set.
4. Print the fallback URL and user code in all modes.
5. Poll until token issued, expired, or timeout.
6. Save the CLI token only on the poll response that includes it.
7. Keep polling interval and timeout request fields testable.
8. Add tests for successful login, no-browser mode, expired session, timeout, and already-logged-in behavior.

## Task 4: Add Public Cloud CLI Commands

Files:

- Create `src/codealmanac/cli/parser/cloud_auth.py`
- Create `src/codealmanac/cli/dispatch/cloud_auth.py`
- Create `src/codealmanac/cli/render/cloud_auth.py`
- Modify `src/codealmanac/cli/parser/admin.py`
- Modify `src/codealmanac/cli/dispatch/admin.py`
- Modify `tests/test_cli.py`
- Modify `tests/test_public_contract.py`
- Modify `README.md`

Commands:

```text
codealmanac login [--api-url URL] [--no-browser] [--timeout SECONDS] [--json]
codealmanac whoami [--api-url URL] [--json]
codealmanac logout [--api-url URL] [--json]
```

Steps:

1. Add top-level parser entries for `login`, `whoami`, and `logout`.
2. Dispatch through cloud auth workflows/services, not direct HTTP calls.
3. Render concise text:
   - login: signed in user and cloud URL
   - whoami: signed-in GitHub login and cloud URL, or not signed in
   - logout: signed-out user or already signed out
4. JSON output must include stable status fields and never print the raw token.
5. Add CLI tests proving commands call the service and render expected text/JSON.
6. Update public contract tests to remove "No hosted login/connect/upload commands."

## Task 5: Make `codealmanac setup` Cloud-First Without Repo Coupling

Files:

- Modify `src/codealmanac/services/setup/requests.py`
- Modify `src/codealmanac/services/setup/models.py`
- Modify `src/codealmanac/services/setup/planning.py`
- Modify `src/codealmanac/services/setup/service.py`
- Modify `src/codealmanac/cli/parser/setup.py`
- Modify `src/codealmanac/cli/dispatch/setup.py`
- Modify `src/codealmanac/cli/render/setup.py`
- Modify `tests/test_cli.py`
- Modify `tests/test_public_contract.py`
- Modify `README.md`

Steps:

1. Add setup request fields for `api_url`, `no_browser`, `login_timeout`, and `skip_login`.
2. By default, `setup` should ensure cloud login before installing instructions.
3. `--skip-login` is allowed for CI or local-only instruction install.
4. Preserve `--skip-instructions`.
5. Keep automation flags working for now, but do not make them the primary setup story.
6. Render setup state as: cloud connected/not connected, instruction changes, automation changes when requested.
7. Do not inspect or configure the current repo in `setup`.
8. Add tests proving `setup` can be run from any directory and composes login plus instruction installation.

## Task 6: Update Launch Docs And Verification

Files:

- Modify `docs/codealmanac-launch/auth-api-contract.md`
- Modify `docs/codealmanac-launch/cli-contract.md`
- Modify `docs/codealmanac-launch/worklog.md`
- Modify `docs/codealmanac-launch/progress.md`
- Modify `docs/codealmanac-launch/verification-matrix.md`
- Modify `docs/codealmanac-launch/next-agent-brief.md`

Steps:

1. Record the exact public CLI auth commands and `/v1` endpoint names.
2. Record auth storage location and token secrecy rule.
3. Record that `setup` is cloud-first and not repo-scoped.
4. Record verification output.
5. Send RelayForge with new percentages after the slice is verified and pushed.

## Verification Commands

Hosted:

```bash
cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend
uv run pytest tests/test_cli_auth_api_contract.py tests/test_identity_api_contract.py tests/test_architecture_contract.py -q
uv run pytest
uv run ruff check .
uv run ruff format --check .
```

## Completion Notes

Implemented hosted `/v1` aliases over the existing CLI token service:

```text
POST /v1/auth/cli/start
GET  /v1/auth/cli/sessions/{session_id}
POST /v1/auth/cli/sessions/{session_id}/complete
POST /v1/auth/cli/sessions/{session_id}/poll
GET  /v1/me
POST /v1/auth/logout
```

Implemented `codealmanac login`, `codealmanac whoami`, `codealmanac logout`,
and cloud-first `codealmanac setup`. The CLI stores only the issued hosted
`alm_...` CLI token in `~/.codealmanac/auth.json` with mode `0600`.

Verification completed:

```text
hosted backend: uv run pytest -q -> 289 passed, 1 warning
hosted backend: uv run ruff check . -> passed
hosted backend: uv run ruff format --check . -> 255 files already formatted
codealmanac: uv run pytest -q -> 474 passed
codealmanac: uv run ruff check . -> passed
codealmanac: git diff --check -> passed
codealmanac: login/setup/whoami/logout --help -> passed
```

CodeAlmanac:

```bash
cd /Users/rohan/Desktop/Projects/codealmanac
uv run pytest tests/test_cloud_auth_service.py tests/test_cloud_login_workflow.py tests/test_cli.py tests/test_public_contract.py tests/test_architecture.py -q
uv run pytest
uv run ruff check .
git diff --check
uv run codealmanac login --help
uv run codealmanac setup --help
uv run codealmanac whoami --help
uv run codealmanac logout --help
```

## Open Implementation Checks

- The existing hosted `/api/cli/...` routes remain as legacy/dashboard aliases.
- The launch identity command is `whoami`; broader product status remains a
  separate future command.
- This slice used `auth.json` mode `0600`; macOS Keychain remains a future store
  implementation behind the same store boundary.
