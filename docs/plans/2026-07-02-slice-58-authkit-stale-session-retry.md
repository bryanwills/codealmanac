# Slice 58: AuthKit Production Schema Repair

Date: 2026-07-02 to 2026-07-03.

## Problem

Launch sign-in must be GitHub-only. The initial hypothesis was a stale
WorkOS/AuthKit browser session after Slice 57. Production evidence changed the
root cause: WorkOS/GitHub OAuth returned tokens, but the backend crashed when it
persisted the user because production Supabase still had the old Supabase
Auth-era `users.supabase_user_id` schema.

## Contract

- WorkOS/AuthKit and GitHub OAuth should stay on the standard SDK/provider
  path. Do not add another hand-rolled OAuth callback or state verifier.
- Production `users` must be WorkOS-shaped:
  `workos_user_id`, encrypted GitHub access token, encrypted GitHub refresh
  token.
- Old Supabase Auth user ids cannot be translated safely. Launch has no
  meaningful user data to preserve, so old identity-linked rows may be deleted
  during repair.
- The repair path must be tracked as a migration, not left as an invisible
  console patch.
- A signed-in production `/setup` page with connected GitHub accounts is the
  end-to-end proof for this slice.

## Wireframe

```text
WorkOS callback succeeds
  -> frontend sends WorkOS accessToken + GitHub oauthTokens to backend
  -> backend verifies WorkOS bearer
  -> users store writes WorkOS id + encrypted GitHub token pair
  -> /setup renders connected GitHub accounts
```

## Files

Hosted:

- `supabase/migrations/20260703000000_repair_workos_identity_schema.sql`

CodeAlmanac launch docs:

- progress, worklog, verification matrix, next-agent brief.

## Verification

- Hosted backend focused auth tests:
  `uv run pytest tests/test_identity_auth_contract.py tests/test_github_auth_contract.py tests/test_installations_contract.py -q`
- Production DB row check for active WorkOS user with encrypted GitHub access
  and refresh tokens.
- Render deploy for hosted commit `01c8463`.
- Browser-harness signed-in production `/setup` check.

## Out of Scope

- Changing WorkOS dashboard authentication methods.
- Adding email/password support.
- Rate limits.
