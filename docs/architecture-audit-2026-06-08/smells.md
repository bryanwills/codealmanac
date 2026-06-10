# Architecture Smells

This file captures suspected problems during the audit. A smell here is not yet
a final refactor directive; each still needs severity and cost/value judgment.

## High Confidence

### SQLite-free CLI path duplicates Commander

`src/cli/sqlite-free.ts` manually re-parses setup, automation, agents, config,
set, update, doctor, and uninstall flags before Commander sees them.

Why it exists: some commands must run even when `better-sqlite3` cannot load,
especially setup, update, doctor, and uninstall.

Why it smells: the workaround is a parallel command router with duplicated flag
parsing and dynamic imports. This is hidden CLI machinery rather than an
obvious boundary.

Possible target: make command registration itself SQLite-free by default.
Register Commander command shapes without importing SQLite-dependent command
implementations, and lazy-import implementations only inside actions. Keep the
ABI guard, but delete the separate hand-written parser.

### Manual capture discovery lags scheduled capture discovery

`src/capture/input.ts` supports explicit transcript files and Claude
auto-discovery. It rejects `--all-apps` and non-Claude app discovery.

`src/capture/discovery/*` supports Claude and Codex candidate discovery for
scheduled capture.

Why it smells: the same product noun, "capture transcript discovery", has two
paths with different capabilities. This is likely accidental special-case
architecture, not a durable product distinction.

Possible target: one capture discovery module that both manual capture and
sweep use. Manual capture can still have different selection policy, but should
not have a separate provider-specific scanner.

### Project doctrine and source behavior disagree on CLI page writes

Repo docs say normal CLI commands do not write page content and only lifecycle
operations write pages. Current commands intentionally rewrite frontmatter:

- `tag`
- `untag`
- `topics rename`
- `topics delete`
- `health --fix`

This may be a legitimate narrowed exception because these commands preserve
body bytes and mutate metadata only. But the invariant is no longer expressed
accurately.

Possible target: rename the invariant to "only lifecycle agents write page
prose; deterministic CLI edit commands may rewrite metadata/frontmatter." Then
ensure command organization makes metadata edit commands visibly separate from
query commands and agent write operations.

### Provider identity is duplicated under different names

`src/config/providers.ts` defines `AgentProviderId`; `src/harness/types.ts`
defines `HarnessProviderId`. Both are currently `claude | codex | cursor`.

The documented split says config owns availability and harness owns runtime
capabilities. That split can stay. The smell is that the duplicate names make
the code feel like two provider systems rather than one provider identity used
by separate lifecycles.

Possible target: one small provider identity catalog with runtime metadata in
`harness` and readiness/status metadata in `agent/readiness`. Avoid broad
enterprise naming; something like `src/providers/id.ts` may be enough if it
does not become a god catalog.

### Process manager knows operation report semantics

`src/process/manager.ts` imports `ALMANAC_OPERATION_REPORT_NAME` and
`parseAlmanacOperationReport` from `src/operations/reports.ts` to derive a run
summary from structured output.

Why it smells: process manager should own execution lifecycle and durable run
observability, while operation-specific output contracts belong to operations.

Possible target: operations provide a small projection function or metadata
field for output summarization, and process manager calls a neutral projection
hook without importing concrete operation report contracts.

## Medium Confidence

### Viewer query projection may drift from CLI query projection

`src/viewer/api.ts` reuses `getPageView()` and search helper builders, but owns
its own SQL for recent pages, search, topic pages, page summaries, and file
mentions.

This may be acceptable because the viewer has different UX needs. The risk is
that file mention semantics, archived-page scope, search ranking, and topic
projection drift from CLI behavior.

Possible target: keep viewer-specific shape, but move shared page-summary and
file-mention SQL into `src/wiki/query/` rather than duplicating inside viewer.

### Codex app-server policy is buried in adapter process code

`src/harness/providers/codex/app-server.ts` owns JSON-RPC process handling and
also hardcodes responses to approval, elicitation, tool-call, permissions, and
token-refresh server requests.

This is bounded inside the Codex adapter, which is good. The smell is that
noninteractive policy is mixed with stream/process management.

Possible target: move request-response policy into a small Codex protocol
policy module, still inside `src/harness/providers/codex/`.

### Connector machinery needs product justification

Composio/GitHub connector support has config schema, connect/source commands,
viewer connection status, source ref parsing, network-access behavior, and
runtime session creation.

The code is not currently huge, but the feature is broad relative to the local
wiki core. Hosted GitHub-native plans in the wiki also suggest Composio should
not be the long-term core GitHub path.

Possible target: keep only if local PR/issue ingest is an active product need.
If kept, frame it as a source-tool boundary and avoid letting `connectors` in
`AgentRunSpec` become the hosted GitHub architecture.

### Deprecated aliases have stuck around

Current CLI still supports deprecated surfaces such as `almanac ps`,
`almanac capture status`, `show --raw`, and `almanac set ...`.

These may be cheap compatibility. The risk is that compatibility surfaces keep
tests, help groups, and parsing branches alive indefinitely.

Possible target: define a removal policy for deprecated aliases, or explicitly
document that they are permanent low-cost compatibility. Do not leave them in a
half-state.

## Things That Look Legitimate

### Capture ledger complexity

The capture ledger, prefix hash checks, pending reconciliation, quiet-window
gating, repo locks, and internal-session skipping all protect real correctness
invariants. They are unusual but not automatically bad.

### Operation/process/harness split

The flow from operation spec to process manager to harness provider is coherent.
The main refactor need is around small ownership leaks and command-side context
assembly, not a full rewrite.

### Config split

`src/config/{schema,codec,store,paths,providers}.ts` is a good level of
separation for this project. The hand-written TOML codec is bounded and may be
preferable to another dependency at this scale.

### Codex adapter module split

The Codex adapter has many moving pieces, but current submodules are mostly
named by real responsibility: request building, app-server process, app
notifications, tool display, usage, failures, actors, and status.
