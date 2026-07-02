# Cloud Open Handoff Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add cloud-first browser handoff commands so `codealmanac`, `codealmanac open`, and repo-scoped open/setup commands send users to the right hosted pages from the current GitHub checkout.

**Architecture:** Keep the CLI auth-light for open commands. The local package detects the current GitHub checkout and opens stable cloud URLs; the hosted frontend resolves those URLs through browser auth into the existing account-scoped dashboard. The CLI never owns account IDs, installation IDs, or dashboard routing decisions.

**Tech Stack:** CodeAlmanac Python workflows, argparse, Pydantic request/result models, Next.js App Router redirect routes, FastAPI browser-session repository resolve API, pytest, Node route tests.

---

## Scope

Implement now:

- Bare `codealmanac` opens the current checkout's hosted wiki route.
- `codealmanac open` opens the current checkout's hosted wiki route.
- `codealmanac repo setup` opens hosted repo setup.
- `codealmanac repo open [activity|settings|github|github-app]` opens the matching cloud or GitHub target.
- Local `cloud_open` workflow owns URL construction and browser invocation.
- Hosted `/wiki/github/[owner]/[repo]` redirects to the existing account-scoped wiki page.
- Hosted `/setup/repo?provider=github&owner=...&repo=...&target=...` redirects to existing account-scoped activity/settings pages or GitHub App installation settings.
- Backend `/api/repositories/resolve` resolves a browser-authenticated full repo name to repo/account IDs.

Defer:

- A richer hosted onboarding page for missing repositories.
- Direct CLI mutation of GitHub App installation scope.
- Custom app URL persistence in config.

## Design Wireframe

```python
# CLI edge
args = parser.parse_args(argv)
result = app.workflows.cloud_open.open(
    OpenCloudTargetRequest(cwd=Path.cwd(), target="wiki")
)
render_cloud_open(result)

# Local workflow
checkout = repository_probe.read(cwd)
url = cloud_url_for(target, checkout.owner_login, checkout.name, app_url)
opened = browser.open(url) if not no_browser else False

# Hosted redirect
resolved = await resolveRepositoryByFullName("owner/repo")
redirect(routes.repositoryWiki(resolved.accountId, resolved.repoId))
```

## Task 1: Hosted Browser Resolve API And Redirect Routes

**Files:**

- Modify: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend/src/almanac/server/repositories_router.py`
- Modify: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/frontend/src/lib/api/server.ts`
- Modify: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/frontend/src/lib/api/dto/repositories.ts`
- Modify: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/frontend/src/lib/routes.ts`
- Create: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/frontend/src/app/wiki/github/[owner]/[repo]/page.tsx`
- Create: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/frontend/src/app/setup/repo/page.tsx`
- Modify: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/frontend/tests/routes.test.mjs`
- Test: `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/backend/tests/test_repositories_api_contract.py`

**Steps:**

1. Add a backend test proving browser auth can resolve `fullName` through `/api/repositories/resolve`.
2. Add the backend route using `current_user`, `RepositoryResolveRequestDTO`, `RepositoryResolveDTO`, and `Action.VIEW_REPO`.
3. Add `resolveRepositoryByFullName(fullName)` to the frontend server API client.
4. Add stable route builders for `wikiGithub(owner, repo)` and `repoSetup(owner, repo, target)`.
5. Add `/wiki/github/[owner]/[repo]` as a tiny server redirect into `routes.repositoryWiki`.
6. Add `/setup/repo` as a tiny server redirect into activity, settings, GitHub repo, or GitHub App installation settings.
7. Extend route tests to lock the redirector routes and ensure they reuse existing account-scoped routes.

## Task 2: CodeAlmanac Cloud Open Workflow

**Files:**

- Create: `/Users/rohan/Desktop/Projects/codealmanac/src/codealmanac/workflows/cloud_open/models.py`
- Create: `/Users/rohan/Desktop/Projects/codealmanac/src/codealmanac/workflows/cloud_open/requests.py`
- Create: `/Users/rohan/Desktop/Projects/codealmanac/src/codealmanac/workflows/cloud_open/service.py`
- Create: `/Users/rohan/Desktop/Projects/codealmanac/src/codealmanac/workflows/cloud_open/__init__.py`
- Modify: `/Users/rohan/Desktop/Projects/codealmanac/src/codealmanac/services/cloud_auth/models.py`
- Modify: `/Users/rohan/Desktop/Projects/codealmanac/src/codealmanac/app.py`
- Test: `/Users/rohan/Desktop/Projects/codealmanac/tests/test_cloud_open_workflow.py`

**Steps:**

1. Add `DEFAULT_CLOUD_APP_URL = "https://codealmanac.com"` and app URL normalization.
2. Add typed targets: `wiki`, `repo`, `setup`, `settings`, `github`, and `github-app`.
3. Build URLs from `LocalRepositoryState.owner_login` and `LocalRepositoryState.name`; reject unavailable or non-GitHub checkouts.
4. Invoke `BrowserOpener` unless `no_browser` is true.
5. Test URL construction, no-browser mode, browser invocation, GitHub direct open, and unavailable checkout failures.

## Task 3: CodeAlmanac CLI Commands

**Files:**

- Modify: `/Users/rohan/Desktop/Projects/codealmanac/src/codealmanac/cli/parser/root.py`
- Modify: `/Users/rohan/Desktop/Projects/codealmanac/src/codealmanac/cli/dispatch/root.py`
- Create: `/Users/rohan/Desktop/Projects/codealmanac/src/codealmanac/cli/parser/open.py`
- Create: `/Users/rohan/Desktop/Projects/codealmanac/src/codealmanac/cli/dispatch/open.py`
- Create: `/Users/rohan/Desktop/Projects/codealmanac/src/codealmanac/cli/render/cloud_open.py`
- Modify: `/Users/rohan/Desktop/Projects/codealmanac/src/codealmanac/cli/parser/repo.py`
- Modify: `/Users/rohan/Desktop/Projects/codealmanac/src/codealmanac/cli/dispatch/repo.py`
- Modify: `/Users/rohan/Desktop/Projects/codealmanac/src/codealmanac/cli/dispatch/admin.py`
- Modify: `/Users/rohan/Desktop/Projects/codealmanac/tests/test_cli.py`
- Modify: `/Users/rohan/Desktop/Projects/codealmanac/tests/test_architecture.py`

**Steps:**

1. Make top-level subcommands optional so bare `codealmanac` can dispatch to `cloud_open`.
2. Add `open [--app-url URL] [--no-browser] [--json]`.
3. Add `repo setup [--app-url URL] [--no-browser] [--json]`.
4. Add `repo open [activity|settings|github|github-app] [--app-url URL] [--no-browser] [--json]`.
5. Keep existing repo trigger/status commands unchanged.
6. Render a compact human line and typed JSON.
7. Add CLI tests with `CliBrowserOpener` and `CliLocalRepositoryProbe`.

## Task 4: Docs, Verification, Commit, Push

**Files:**

- Modify: `/Users/rohan/Desktop/Projects/codealmanac/docs/codealmanac-launch/auth-api-contract.md`
- Modify: `/Users/rohan/Desktop/Projects/codealmanac/docs/codealmanac-launch/cli-contract.md`
- Modify: `/Users/rohan/Desktop/Projects/codealmanac/docs/codealmanac-launch/frontend-surface-contract.md`
- Modify: `/Users/rohan/Desktop/Projects/codealmanac/docs/codealmanac-launch/progress.md`
- Modify: `/Users/rohan/Desktop/Projects/codealmanac/docs/codealmanac-launch/verification-matrix.md`
- Modify: `/Users/rohan/Desktop/Projects/codealmanac/docs/codealmanac-launch/worklog.md`
- Modify: `/Users/rohan/Desktop/Projects/codealmanac/docs/codealmanac-launch/next-agent-brief.md`

**Verification:**

Hosted:

```bash
cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence
cd backend && uv run pytest tests/test_repositories_api_contract.py tests/test_cli_repositories_api_contract.py -q
cd ../frontend && npm test -- --runTestsByPath tests/routes.test.mjs
cd ../backend && uv run ruff check .
cd .. && git diff --check
```

CodeAlmanac:

```bash
cd /Users/rohan/Desktop/Projects/codealmanac
uv run pytest tests/test_cloud_open_workflow.py tests/test_cli.py tests/test_architecture.py -q
uv run ruff check .
uv run python -m compileall src -q
git diff --check
```

Commit/push:

```bash
cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence
git commit -m "feat: add cloud route handoff"
git push origin codex/workos-authkit-api-foundation

cd /Users/rohan/Desktop/Projects/codealmanac
git commit -m "feat: open cloud pages from CLI"
git push origin dev
```
