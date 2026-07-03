# Slice 80 — hosted signup email analytics

## Scope

Current production sign-in works, but the hosted analytics event for a new user
only carries `workos_user_id` and `github_user_id`. PostHog therefore cannot
attach the signed-in email that WorkOS/AuthKit already knows after GitHub
login.

This slice adds the smallest clean seam:

```python
# frontend AuthKit callback owns provider session facts
session = authkit.handleAuth.onSuccess(...)

backend.identity.users.link_github_app_session(
    jwt=session.access_token,
    provider_token=session.oauth_tokens.access_token,
    provider_refresh_token=session.oauth_tokens.refresh_token,
    email=session.user.email,  # analytics-only, not identity or auth
)

# backend verifies identity independently
claims = workos.verify(jwt)
github_user = github.users.viewer(provider_token)

events.dispatch(UserSignedUp(..., email=email))
analytics.capture_user_signed_up(event)  # includes "$set": {"email": email}
```

## Decisions

- WorkOS/AuthKit remains the source of the browser session email.
- GitHub App OAuth tokens remain the source of GitHub identity and refreshable
  provider credentials.
- The backend must not trust email for authorization. It is optional analytics
  metadata only.
- The API request DTO, frontend DTO, identity service hook, domain event, and
  analytics event should use the same field name: `email`.
- The stale dirty `/Users/rohan/Desktop/Projects/usealmanac` checkout is not a
  source of truth. Work happens in
  `/Users/rohan/Desktop/Projects/codealmanac-hosted` on current hosted
  `origin/main`.

## Read Before Coding

- `MANUAL.md`
- `AGENTS.md`
- `docs/reference/cosmic-python/chapter_04_service_layer.md`
- `docs/reference/cosmic-python/chapter_10_commands.md`
- WorkOS AuthKit Next.js callback contract: `handleAuth` `onSuccess` exposes the
  authenticated `user`, `accessToken`, and OAuth provider tokens.

The relevant Cosmic Python pressure is the service layer chapter: the HTTP edge
maps request data into the service use case; the service verifies product truth
and emits a domain event. The commands chapter reinforces that the session-link
call is a command: it carries intent, fails noisily, and may publish a fact when
successful.

## Implementation

Backend:

- Add optional `email` to `GitHubAppSessionRequestDTO`.
- Add an immutable typed `UserCreatedContext` for optional signup metadata.
- Change `UserCreatedHandler` to receive that context.
- Add optional `email` to `UserSignedUp`.
- Include `email` and PostHog `$set.email` only when present.

Frontend:

- Add `email` to `GitHubAppSessionRequestDTO`.
- In `frontend/src/app/auth/callback/route.ts`, destructure `user` from
  WorkOS/AuthKit `onSuccess` and pass `user.email ?? null`.

Tests:

- API contract proves the request body passes email to identity service.
- Identity service contract proves created hook receives email only for new
  users.
- Analytics contract proves signup capture sends `email` and `$set.email`.

## Out Of Scope

- Changing stored `users` schema.
- Using email for access control.
- Reconciliation/backfill for historical PostHog users.
- Any WorkOS dashboard or provider setting change.

## Verification

Run from `/Users/rohan/Desktop/Projects/codealmanac-hosted`:

```bash
cd backend
uv run pytest tests/test_identity_api_contract.py tests/test_identity_auth_contract.py tests/test_analytics_contract.py
uv run ruff check .
python -m compileall src -q

cd ../frontend
npm install
npm run test:routes
npm run lint
```

If the focused gate is clean, push the hosted branch, fast-forward hosted
`main`, deploy/check production backend and frontend if affected by the merged
commit, then update the central launch notes in the root CodeAlmanac repo.
