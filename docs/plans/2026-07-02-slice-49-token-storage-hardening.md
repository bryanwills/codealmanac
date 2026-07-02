# Slice 49: GitHub Token Storage Hardening

Date: 2026-07-02
Repos:

- `/Users/rohan/Desktop/Projects/codealmanac`
- `/Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence`

## Goal

Make the hosted WorkOS/GitHub auth boundary launch-safe enough to build on:

- keep the browser session on the WorkOS AuthKit Next.js SDK path
- validate WorkOS AuthKit access tokens against the documented issuer/JWKS shape
- stop storing GitHub OAuth provider tokens as plaintext DB fields
- keep token encryption as a persistence concern, not a route or product-workflow concern

## Source Guidance

Read before coding:

- `slow-development` skill
- `python-code-quality` skill
- CodeAlmanac `MANUAL.md`
- hosted `MANUAL.md`
- WorkOS AuthKit Next.js guidance
- WorkOS AuthKit sessions docs
- WorkOS Vault guidance
- `cryptography` Fernet/MultiFernet docs

Relevant provider facts:

- WorkOS AuthKit Next.js owns browser session cookies and can pass upstream
  OAuth tokens through `handleAuth({ onSuccess })`.
- WorkOS sessions docs describe AuthKit access tokens as JWTs, signed by the
  WorkOS JWKS, with issuer `https://api.workos.com/` unless a custom auth
  domain is configured.
- WorkOS Vault is WorkOS-organization-scoped. The current product model has not
  made WorkOS organizations the owner for every GitHub account/repository yet,
  so using Vault for GitHub user tokens now would force a fake hierarchy.
- `cryptography.fernet.MultiFernet` encrypts with the first key and decrypts
  with any configured key, which fits launch key rotation without inventing a
  local crypto scheme.

## Architecture

Wireframe:

```python
# Browser owns WorkOS session through the WorkOS Next SDK.
access_token = withAuth().accessToken

# FastAPI receives only an AuthKit access-token bearer.
claims = almanac.workos.verify(access_token)

# Product service keeps usable domain tokens.
user = User(oauth_token="ghu_...", refresh_token="ghr_...")

# Store owns persistence translation.
row.oauth_token_ciphertext = token_cipher.encrypt(user.oauth_token)
row.refresh_token_ciphertext = token_cipher.encrypt(user.refresh_token)

# Reads invert the translation before returning domain data.
user = User(oauth_token=token_cipher.decrypt(row.oauth_token_ciphertext))
```

Ownership:

- `integrations/workos` owns WorkOS token verification.
- `services/identity/users/store.py` owns user persistence and row/domain
  conversion.
- `services/identity/users/secrets.py` owns the service-local token cipher seam
  and the `cryptography` Fernet adapter.
- `app.py` wires the concrete cipher from settings.
- Supabase migrations store ciphertext column names explicitly.

## Scope

Implement:

- normalize WorkOS issuer comparison/validation to the documented trailing slash
  form while preserving custom-domain support
- add `github_token_encryption_keys` setting
- add a Fernet/MultiFernet token cipher
- rename user token DB/table columns to `oauth_token_ciphertext` and
  `refresh_token_ciphertext`
- encrypt on `UsersStore.upsert`
- decrypt on `UsersStore.get` / row-to-domain conversion
- add a migration that removes plaintext columns from existing databases and
  invalidates any legacy plaintext user links because SQL cannot safely encrypt
  them without the app secret
- update backend tests and architecture guards
- set the backend encryption key in Doppler before deploying

Out of scope:

- WorkOS organization ownership migration
- WorkOS Vault adoption
- real authenticated browser session smoke
- CLI token storage hardening

## Verification

Minimum gates:

- focused backend identity/store/auth tests
- backend architecture contract tests
- full backend pytest
- ruff
- compileall
- frontend route tests if frontend routes are touched or auth route contracts
  need confirmation
- backend smoke with the new required settings
- no immediate deploy after a small token-storage checkpoint; Render/Vercel
  promotion and Supabase migration application happen only at a batched
  deploy gate

## Risks

- Existing live plaintext GitHub links cannot be encrypted in SQL. The migration
  deactivates those links and drops plaintext columns. This is acceptable under
  the launch assumption that there are no real users to preserve.
- Missing `GITHUB_TOKEN_ENCRYPTION_KEYS` must fail at startup. Silent plaintext
  fallback is not allowed.
- If the WorkOS issuer setting is manually configured without a slash, the app
  should normalize it before JWT validation because WorkOS documents the issuer
  with the slash.
