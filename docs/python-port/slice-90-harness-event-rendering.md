# Slice 90: Harness Event Rendering

## Scope

Make the `serve` job detail page render the useful fields already present in
normalized `HarnessEvent` payloads.

This slice changes:

- `server/assets/viewer/jobs.js` event detail rendering.
- Viewer CSS for structured harness detail rows.
- Focused server/static tests for the browser asset contract.
- Steering docs and verification records.

## Why

Slice 89 exposed job detail pages, but the browser only showed the harness event
kind, actor, tool name, provider session, and total tokens. The live agreement
says the inspectable transcript surface is the CodeAlmanac-owned normalized
harness event stream: text, tool use/results, usage, provider session,
done/failure details, and agent trace events where providers expose them.

Cosmic Python chapter 12 says, "reads and writes are different." This is still
a read-side slice. We do not mutate jobs, read raw provider transcript files, or
add provider-specific parsing. The browser renders the typed event fields the
service already returns.

## Shape

```javascript
event.harness_event.tool_display  -> command/path/status/summary rows
event.harness_event.usage         -> token rows
event.harness_event.failure       -> code/message/fix rows
event.harness_event.agent_trace   -> helper-agent rows
event.harness_event.raw           -> intentionally not rendered by default
```

The API payload remains the source of truth. The browser chooses a readable
projection for humans and agents inspecting a local run.

## Out Of Scope

- No Normal/Debug mode toggle.
- No raw JSON dump.
- No browser cancel/attach controls.
- No provider-specific transcript reader.
- No new `HarnessEvent` fields.

## Verification

- Focused server/static tests.
- ES module syntax checks.
- Browser-harness dogfood against a temp run with tool, usage, failure, and
  agent trace events.
- Full `uv run pytest`, `uv run ruff check .`, and `git diff --check`.
