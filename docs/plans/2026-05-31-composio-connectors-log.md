# Composio Connectors Decision And Implementation Log

## 2026-05-31

- User corrected the connector direction: Composio is the only connector substrate for now. Almanac should not choose among connector providers. GitHub is only the first native Almanac connection UX over Composio.
- User wants `almanac connect github` and an `almanac serve` connections screen with icons and connect/manage affordances.
- User wants multiple accounts supported.
- User wants the temporary `gh` connector removed, but the prompt/source-material leak must be fixed first.
- Implemented and pushed branch `codex/github-ingest-simple` with commit `32930af`, removing eager GitHub issue/PR material prefetch from ingest prompts.
- Started branch `codex/composio-connectors` from that fix so the connector branch includes the simplified boundary while `dev` remains untouched until final squash merge.

## Research Notes

- Composio docs describe connected accounts as authenticated user-to-toolkit connections and say Composio handles token refresh and credential management.
- Composio docs show TypeScript `connectedAccounts.list({ userIds, statuses })`, `connectedAccounts.get(id)`, account enable/disable/delete, and explicit `connectedAccountId` tool execution.
- Composio docs recommend `link()` for Composio-managed OAuth and note that multiple accounts are supported.
- Composio docs show sessions can be restricted with `toolkits: ["github"]`, keep meta tools enabled by default for runtime discovery, and expose both `session.tools()` and `session.mcp.url`.
- Composio CLI docs show `composio link github`, `composio search`, `composio execute`, `composio proxy`, and developer commands for connected-account listing and auth configs.

## Open Decisions

- Decided: v1 uses the TypeScript SDK directly for `almanac connect github` and `almanac source github ...`; the Composio CLI is not part of the runtime contract.
- Decided: `almanac connect github` prints the connect URL by default, supports `--wait`, and `almanac connect github --status` refreshes/list accounts.
- Decided: operation specs now carry connector runtime requirements. GitHub source ingest gives the agent an `almanac source github ...` command and enables Codex network only when a connector runtime is declared.
- Decided: source semantics live under the GitHub connector, while Composio owns session/proxy execution as the connector substrate.
- Decided: non-ACTIVE Composio accounts are setup-needed and cannot be selected for GitHub source ingest.
- Decided: the viewer connections screen landed in this branch with connected, pending, failed, and not-connected states derived from stored account statuses.

## Review Notes

- Review found that prompt-only connector wording was misleading because Codex runs had no connector runtime requirement and defaulted to no network. The fix was to make connector requirements explicit on `AgentRunSpec`, pass those from ingest resolution into Absorb, and enable Codex network access only for connector-backed runs.
- Review found pending Composio accounts were accepted as usable. The fix was to require `ACTIVE` status in both GitHub source resolution and `almanac source github ...`.
- Review recommended separating Composio substrate code from GitHub source semantics. The fix moved session/proxy execution to `src/connectors/composio/runtime.ts` and GitHub source endpoint semantics to `src/connectors/github/source.ts`.
- Review found connector config keys were modeled but not exposed through `almanac config`. The fix added `connectors.composio.api_key_env` and `connectors.github.default_account` to the canonical config key surface.
