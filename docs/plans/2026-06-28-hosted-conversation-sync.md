# Hosted Conversation Sync

## Goal

Add a hosted conversation-to-wiki path that works alongside the existing PR update path.

The product shape:

```txt
Claude/Codex UserPromptSubmit hook
-> Claude/Codex Stop hook
-> almanac cloud capture-hook
-> usealmanac DB stores completed turns
-> hosted 5h repo+branch ingest scheduler
-> Modal worker
-> almanac absorb
-> auto-commit .almanac changes to the same branch
```

This is a new trigger source, not a replacement for PR-triggered runs.

## Current Trigger And Delivery Model

Current hosted path:

```txt
trigger:  GitHub PR event
source:   pull request
worker:   Modal update worker
delivery: existing update delivery path
```

New hosted path:

```txt
upload trigger: Claude/Codex UserPromptSubmit + Stop hook pair
ingest trigger: hosted scheduler finds repo+branch due for wiki update
source:   conversation batch
worker:   Modal update worker
delivery: auto-commit to the same branch
```

The hook upload and wiki ingest are separate. Hook uploads keep the hosted DB
current at turn granularity. The hosted 5h scheduler decides when stored turns
become a Modal wiki update run.

The maintained unit is:

```txt
repo_id + branch + almanac root
```

If a transcript segment has no branch after fallback, store it as unroutable and do not enqueue a run.

## Command Surface

Use the executable name `almanac`.

Add:

```txt
almanac login
almanac logout
almanac cloud status
```

Update existing onboarding:

```txt
almanac setup
```

`setup` asks whether to send Claude/Codex turns to Almanac Cloud. If the user
opts in, setup installs provider hooks. There is no user-facing
`almanac cloud install`, no `almanac cloud sync`, and no cloud scheduled scanner.

Hooks call an internal command:

```txt
almanac cloud capture-hook --provider codex --event UserPromptSubmit
almanac cloud capture-hook --provider codex --event Stop
almanac cloud capture-hook --provider claude --event UserPromptSubmit
almanac cloud capture-hook --provider claude --event Stop
```

Local self-managed wiki automation keeps using existing local commands such as
`almanac sync` and `almanac automation install`. Cloud capture does not reuse
that scheduler path.

## Authentication

`almanac login` should use a browser authorization flow.

```txt
almanac login
-> CLI requests a login session from usealmanac
-> usealmanac returns verification URL, short code, device/session id
-> user signs in in browser
-> usealmanac creates a CLI token
-> CLI polls until the token is ready
-> CLI stores the raw token locally
```

Local storage:

```txt
~/.almanac/credentials.json
```

Server storage:

```txt
cli_tokens
- id
- user_id
- account_id nullable
- token_hash
- name
- created_at
- last_used_at
- revoked_at nullable
```

The backend stores only the token hash. Requests use:

```http
Authorization: Bearer <raw_cli_token>
```

The backend hashes the bearer token and resolves it to a user.

## Codealmanac CLI Changes

### 1. Add Cloud Auth And Client Modules

New files:

```txt
src/cloud/auth.ts
src/cloud/client.ts
src/cloud/config.ts
src/cloud/types.ts
```

Responsibilities:

- `auth.ts`: login polling flow, credential read/write, logout.
- `client.ts`: typed HTTP calls to usealmanac.
- `config.ts`: hosted base URL, defaulting to production but test-overridable.
- `types.ts`: request/response types shared by cloud commands.

Update:

```txt
src/cli/register-commands.ts
src/cli/register-cloud-commands.ts
```

`src/cli/register-commands.ts` is the top-level command registration path. It is
where root commands such as `almanac login` and `almanac logout` belong.

`src/cli/register-cloud-commands.ts` should register `almanac cloud status` and
the internal `almanac cloud capture-hook` command. Keep cloud capture out of
`src/cli/register-wiki-lifecycle-commands.ts`, because it is not a local
lifecycle operation like `sync`, `ingest`, or `garden`.

### 2. Add Hook-Driven Cloud Capture

New files:

```txt
src/cloud/capture/hooks.ts
src/cloud/capture/providers/codex.ts
src/cloud/capture/providers/claude.ts
src/cloud/capture/turn-state.ts
src/cloud/capture/upload.ts
```

Responsibilities:

- `hooks.ts`: entrypoint for `almanac cloud capture-hook`.
- provider modules: parse Codex and Claude hook payloads and transcript metadata.
- `turn-state.ts`: small local state used to pair `UserPromptSubmit` and `Stop`.
- `upload.ts`: build the completed-turn payload and call the hosted API.

The confirmed provider model:

```txt
UserPromptSubmit = turn opened
Stop             = turn completed
```

This was verified locally for both Codex and Claude. Cloud capture relies on
these hooks as the primary upload mechanism. There is no cloud scanner and no
cloud polling/backfill loop.

### 3. Add Conversation Turn Extraction

New file:

```txt
src/cloud/capture/conversation-turn.ts
```

This module turns hook events and the matching transcript delta into one
uploadable turn. Hosted delivery needs a repo and branch before it can later
auto-commit, so the turn payload carries branch routing metadata.

Output type:

```ts
interface ConversationTurnUpload {
  app: "claude" | "codex";
  sessionId: string;
  turnId: string;
  cwd: string;
  repoRoot: string;
  repoFullName: string;
  branch: string | null;
  branchSource: "transcript" | "git_fallback" | "missing";
  headSha: string | null;
  startedAt: string;
  completedAt: string;
  routingStatus: "routable" | "missing_branch" | "missing_repo";
  messages: ConversationMessage[];
}
```

Rules:

- Prefer branch from transcript metadata.
- If missing, run `git branch --show-current` in the transcript `cwd`.
- Capture `git rev-parse HEAD` when possible.
- If branch is still missing, upload the turn with `routingStatus = "missing_branch"`.
- If repo cannot be resolved to a hosted repository, do not upload and report it in local status.
- A completed turn is the unit stored in hosted DB.

The local scan found real Codex sessions without branch metadata, so fallback is required.

### 4. Add Cloud Commands

New file:

```txt
src/cli/commands/cloud.ts
```

Commands:

```txt
almanac cloud status
almanac cloud capture-hook --provider <codex|claude> --event <UserPromptSubmit|Stop>
```

`cloud status`:

- does not upload
- checks auth
- checks cloud reachability
- shows whether Codex hooks are installed
- shows whether Claude hooks are installed
- shows hook trust/disabled/missing states when detectable
- shows current repo/branch if inside a repo
- shows last upload and latest hosted ingest run if known

`cloud capture-hook`:

```txt
UserPromptSubmit:
  record turn-open metadata locally
  optionally notify hosted that a turn started

Stop:
  read completed turn delta
  upload completed turn to hosted DB
```

This command is internal. Users should not need to run it manually.

### 5. Add Cloud Setup Step

Update:

```txt
src/cli/commands/setup/index.ts
src/cli/commands/setup/setup-plan.ts
src/cli/commands/setup/next-steps.ts
```

New files:

```txt
src/cli/commands/setup/cloud-capture-step.ts
src/platform/cloud-hooks/codex.ts
src/platform/cloud-hooks/claude.ts
```

Setup adds one hosted question:

```txt
Send Claude/Codex turns to Almanac Cloud?
```

If yes:

```txt
- ensure the user is logged in or start the login flow
- install Codex UserPromptSubmit and Stop hooks
- install Claude UserPromptSubmit and Stop hooks
- print a status summary
```

Do not add a scheduled cloud task to `src/platform/automation/tasks.ts`.
Scheduled local automation remains for local self-managed `sync`, Garden, and
CLI update only.

The next-steps box should show:

```txt
almanac cloud status
```

## Usealmanac Backend Changes

### 1. Add CLI Token Auth

New service:

```txt
backend/src/almanac/services/cli_tokens/
```

Files:

```txt
models.py
tables.py
store.py
service.py
__init__.py
```

New router:

```txt
backend/src/almanac/server/cli_auth_router.py
```

Update:

```txt
backend/src/almanac/server/app.py
backend/src/almanac/server/deps.py
```

Routes:

```http
POST /api/cli/auth/sessions
GET  /api/cli/auth/sessions/{session_id}
POST /api/cli/auth/sessions/{session_id}/complete
GET  /api/cli/me
```

The complete route is called by the signed-in browser session. The polling route is called by the CLI.

### 2. Add Conversation Source Storage

New service:

```txt
backend/src/almanac/services/conversations/
```

Files:

```txt
models.py
tables.py
store.py
service.py
__init__.py
```

New router:

```txt
backend/src/almanac/server/conversations_router.py
```

Update:

```txt
backend/src/almanac/server/app.py
```

Tables:

```txt
conversation_sources
- id
- account_id
- repo_id
- user_id
- provider
- provider_session_id
- transcript_path_hash
- first_cwd
- created_at
- last_seen_at

conversation_turns
- id
- source_id
- account_id
- repo_id
- branch nullable
- branch_source
- routing_status
- head_sha nullable
- provider_turn_id
- started_at
- completed_at nullable
- uploaded_at
- ingest_batch_id nullable
- ingested_run_id nullable

conversation_messages
- id
- turn_id
- sequence
- role
- content
- occurred_at nullable
```

Uniqueness:

```txt
source_id + provider_turn_id
```

or:

```txt
provider + provider_session_id + provider_turn_id
```

Routes:

```http
POST /api/cli/repositories/resolve
POST /api/cli/repositories/{repo_id}/conversation-turns/start
POST /api/cli/repositories/{repo_id}/conversation-turns/complete
GET  /api/accounts/{account_id}/repositories/{repo_id}/conversation-sources
```

The upload route validates:

- CLI token is valid.
- User has access to the repo.
- The GitHub repo full name maps to an installed usealmanac repository.
- Turn uploads are idempotent.
- Turns with missing branch are stored but excluded from automatic ingest.

### 3. Add Hosted Conversation Ingest Scheduler

Add table:

```txt
conversation_ingest_state
- repo_id
- branch
- next_ingest_due_at nullable
- last_ingest_enqueued_at nullable
- active_run_id nullable
- updated_at
```

Hosted scheduler check:

```py
for repo_id, branch in repo_branches_due_for_conversation_ingest(now):
    if has_completed_uningested_routable_turns(repo_id, branch):
        if no_active_conversation_run(repo_id, branch):
            create_conversation_batch(repo_id, branch)
            create_update_run(...)
            set next_ingest_due_at = now + 5h
```

The CLI does not own the 5h clock. Hooks upload completed turns when they happen.
The hosted scheduler owns wiki update cadence per repo+branch.

### 4. Add Conversation Batch Source To Update Runs

Update:

```txt
backend/src/almanac/services/updates/models.py
backend/src/almanac/services/updates/tables.py
backend/src/almanac/services/updates/records.py
backend/src/almanac/services/updates/queue.py
backend/src/almanac/services/updates/codealmanac.py
backend/src/almanac/services/updates/delivery.py
```

Add source kind:

```py
ConversationBatchSource(
    kind="conversation_batch",
    repo_id=...,
    branch=...,
    batch_id=...,
    head_sha=...,
)
```

Add delivery:

```py
CommitToBranch(
    branch=branch,
    expected_head_sha=current_branch_head_or_null,
)
```

Commit message:

```txt
docs(almanac): update wiki from agent chats [skip ci]
```

Delivery must keep the existing safety invariant:

```txt
Only .almanac/** paths may be committed.
No empty commits.
No non-Almanac files.
```

### 5. Update Modal Worker Behavior

Update:

```txt
backend/modal_app/updates_worker.py
backend/src/almanac/services/updates/codealmanac.py
```

For `ConversationBatchSource`:

```txt
fetch batch turns/messages from DB
render a temporary source file outside the repo checkout
run almanac absorb <temp-file> --foreground --using codex -y
collect .almanac changes
submit UpdateBundle
delivery auto-commits to the same branch
mark turns ingested after successful completion
```

Temporary source file shape:

```md
# Agent Conversation Batch

Repository: owner/name
Branch: dev
Providers: codex, claude
Message range: ...

## Messages

...
```

This temp file is operation input only. It is not committed.

## Usealmanac Frontend Changes

### 1. Add Sources API DTOs

New file:

```txt
frontend/src/lib/api/dto/conversations.ts
```

Update:

```txt
frontend/src/lib/api/dto/index.ts
frontend/src/lib/api/server.ts
frontend/src/lib/routes.ts
```

DTOs:

```ts
ConversationSourceSummary
ConversationIngestState
ConversationUploadStatus
```

API function:

```ts
listRepositoryConversationSources(accountId, repoId)
```

### 2. Add Repository Sources Page

New route:

```txt
frontend/src/app/dashboard/accounts/[accountId]/repositories/[repoId]/sources/page.tsx
```

Update nav:

```txt
frontend/src/components/shell/sidebar-nav.tsx
```

UI content:

```txt
provider
branch
last upload
message count
unroutable count
last ingest
latest run status
```

Do not show raw message content in v1.

### 3. Update Local Agent Setup Copy

Update:

```txt
frontend/src/app/dashboard/local-agent-access/page.tsx
frontend/src/components/shell/local-agent-access-banner.tsx
frontend/src/components/dashboard/quickstart-command.tsx
```

Setup commands:

```txt
npx codealmanac@latest setup
almanac login
```

Explain the distinction:

```txt
local sync updates your local .almanac
cloud capture uploads completed Claude/Codex turns so hosted Almanac can maintain repo wiki branches
```

### 4. Extend Run Source Rendering

Update:

```txt
frontend/src/lib/api/dto/runs.ts
frontend/src/components/runs/run-row.tsx
frontend/src/components/runs/runs-list.tsx
```

Render:

```txt
Captured chats on <branch>
```

for conversation batch runs.

## Database Migration

New migration in `../usealmanac`:

```txt
supabase/migrations/<timestamp>_conversation_sync.sql
```

Migration creates:

```txt
cli_tokens
cli_login_sessions
conversation_sources
conversation_turns
conversation_messages
conversation_ingest_batches
conversation_ingest_state
```

Indexes:

```txt
cli_tokens(token_hash)
conversation_sources(repo_id, provider, provider_session_id)
conversation_turns(repo_id, branch, ingest_batch_id)
conversation_turns(source_id, provider_turn_id)
conversation_messages(turn_id, sequence)
conversation_ingest_state(repo_id, branch)
```

RLS/grants should follow the existing usealmanac backend migration pattern.

## Tests

### Codealmanac

Add tests for:

```txt
almanac login polling success
credential read/write redacts token in errors
setup installs Codex cloud hooks
setup installs Claude cloud hooks
capture-hook records UserPromptSubmit turn-open state
capture-hook uploads Stop completed turn
Codex branch extraction
Claude branch extraction
git fallback branch extraction
missing branch becomes unroutable
cloud status is read-only
```

Likely files:

```txt
test/cloud-auth.test.ts
test/cloud-capture.test.ts
test/conversation-turn.test.ts
test/setup-cloud-capture.test.ts
```

### Usealmanac Backend

Add tests for:

```txt
CLI token hash auth
token revocation
repository resolve from owner/name
turn upload idempotency
missing branch stored but not enqueued
hosted 5h ingest cadence
active run suppresses new run
conversation batch creates update run
worker renders conversation temp source
delivery commits only .almanac changes
```

### Usealmanac Frontend

Add tests or focused checks for:

```txt
Sources page renders empty state
Sources page renders provider/branch/upload/ingest rows
Run row renders conversation batch source
Local agent setup copy includes cloud capture setup
```

## Implementation Order

### Slice 1: Contracts And Storage

Do first:

- usealmanac migration
- CLI token service
- conversation storage service
- upload endpoint
- no worker integration yet

This proves completed turns can land in DB with repo and branch.

### Slice 2: CLI Cloud Capture

Do second:

- `almanac login`
- `almanac logout`
- `almanac cloud status`
- `almanac cloud capture-hook`
- setup cloud hook installation
- branch fallback
- upload tests

This proves Claude/Codex turns can reach hosted storage through hooks.

### Slice 3: Hosted Scheduler And Modal Runs

Do third:

- conversation ingest state
- hosted 5h ingest scheduler
- `ConversationBatchSource`
- Modal worker temp source
- auto-commit delivery

This proves chats become `.almanac` commits.

### Slice 4: Frontend And Setup

Do fourth:

- repo Sources page
- run-source rendering
- setup/banner copy
- cloud status polish

This makes the product understandable.

## Open Decisions

1. Token storage path:

```txt
~/.almanac/credentials.json
```

is the recommended path.

2. Hosted base URL config:

Use production by default, with env override for development:

```txt
ALMANAC_CLOUD_URL
```

3. Raw transcript path:

Do not upload raw local paths by default. Upload a stable hash plus optional basename for diagnostics.

4. Message content retention:

V1 stores message content because Absorb needs it. Add retention/revocation controls after the core loop works.

5. Branch protection:

If direct auto-commit fails because of branch protection, mark the run failed with a clear reason. Do not silently open a PR in v1 unless the product decision changes.

6. CI behavior:

Use `[skip ci]` in the bot commit message, but keep `.almanac/**` path filtering as a recommended customer setup rather than assuming every CI respects the marker.

7. Hook reliability:

Cloud capture is hook-only. If a hook is disabled, untrusted, times out, or the
machine is offline, that turn may not upload. `almanac cloud status` should make
hook health visible, but v1 will not add a cloud scanner/backfill loop.

## Non-Goals

- No manual "ingest now" button in v1.
- No hosted chat UI in v1.
- No cloud scanner or cloud transcript polling fallback.
- No local 5h cloud upload automation.
- No default-branch guessing for missing branch.
- No committed source sidecar files.
- No raw transcript blob upload when message rows are enough.
- No new AI pipeline that decides relevance before Absorb.
