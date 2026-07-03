# Slice 75: Cloud repo list

## Scope

Add the canonical `codealmanac repo list` command and the matching hosted
`GET /v1/repositories` API route.

## Product Contract

- `repo` is the only public namespace. Do not add `repos`.
- `repo list` is cloud-first and does not require a current checkout.
- The list shows repositories from GitHub App installations visible to the
  signed-in GitHub user.
- Listing must use the mirrored installation rows, not per-repository GitHub
  collaborator permission checks.

## Design

Hosted:

```text
GET /v1/repositories
  current_cli_user
  Repositories.connected_for_user(user, PageRequest)
  PageDTO[RepositoryListItemDTO]
```

`connected_for_user` asks GitHub for the user's visible app installations, then
reads mirrored repository rows for those account ids. It does not call
`permission_for` for each repository.

CLI:

```text
codealmanac repo list [--api-url URL] [--limit N] [--cursor C] [--json]
  CloudRepositoriesService.list()
  HttpCloudAuthClient.GET /v1/repositories
  render rows as: full_name<TAB>repo_id<TAB>account_id
```

## Files

CodeAlmanac:

- `src/codealmanac/cli/parser/repo.py`
- `src/codealmanac/cli/dispatch/repo.py`
- `src/codealmanac/cli/render/repo.py`
- `src/codealmanac/services/cloud_repositories/models.py`
- `src/codealmanac/services/cloud_repositories/ports.py`
- `src/codealmanac/services/cloud_repositories/requests.py`
- `src/codealmanac/services/cloud_repositories/service.py`
- `src/codealmanac/integrations/cloud/http.py`
- `src/codealmanac/workflows/cloud_repo/*`
- CLI and service tests

Hosted:

- `backend/src/almanac/server/cli_repositories_router.py`
- `backend/src/almanac/services/repositories/service.py`
- `backend/src/almanac/services/repositories/store.py`
- CLI route and service tests

## Verification

- CodeAlmanac targeted pytest for cloud repository service, workflow, and CLI.
- CodeAlmanac targeted ruff on changed Python files.
- Hosted targeted pytest for CLI repository API and repository service.
- Hosted targeted ruff on changed Python files.
- Production smoke after deploy:
  `codealmanac repo list`, `codealmanac repo status`,
  `codealmanac repo triggers list`.
