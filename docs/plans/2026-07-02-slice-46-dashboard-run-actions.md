# Slice 46: Dashboard Run Actions

## Goal

Make cloud run cancellation and retry visible and usable from the hosted
dashboard activity list.

The public browser behavior:

```text
queued/running run      -> show Cancel
failed/stale/cancelled  -> show Retry
delivered run           -> no mutation action
```

The browser uses the existing BFF commands:

```text
POST /api/dashboard/runs/{run_id}/cancel
POST /api/dashboard/runs/{run_id}/retry
```

## Product Contract

- Run actions live on the repository activity row, next to the existing Events
  control.
- Cancel is only visible for `queued` and `running`.
- Retry is only visible for `failed`, `stale`, and `cancelled`.
- Delivered runs stay read-only.
- A pending action disables row actions and uses explicit pending copy.
- A failed action renders an inline row error; the old run data remains visible.
- Successful cancellation replaces that run row with the returned cancelled run.
- Successful retry inserts or updates the returned run at the top of the list
  while keeping the original terminal run visible.
- Polling remains unchanged: it is active only while a visible run is queued or
  running.

## Architecture Wireframe

```tsx
// app state owner
await runsList.handleCancel(run)
  updated = await cancelRun(run.runId)
  replaceRun(updated)

await runsList.handleRetry(run)
  created = await retryRun(run.runId)
  upsertRunAtTop(created)

// presentation-only row
<RunRow
  run={run}
  action={runActionFor(run.status)}
  actionPending={pendingByRun[run.runId]}
  actionError={errorByRun[run.runId]}
  onCancel={...}
  onRetry={...}
/>
```

`RunsList` owns mutation effects, pending state, errors, and list replacement.
`RunRow` stays a rendering component. The BFF client remains the only browser
transport boundary.

## Hosted Files

- `frontend/src/components/runs/run-actions.ts`
- `frontend/src/components/runs/run-row.tsx`
- `frontend/src/components/runs/runs-list.tsx`
- `frontend/tests/frontend/run-row.test.tsx`
- `frontend/tests/frontend/run-actions.test.ts`

## Verification

Focused:

```bash
cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/frontend
npm run test:frontend
npm run lint
npm run build
```

Before commit:

```bash
cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence/frontend
npm run test:routes
npm run test:frontend
npm run lint
npm run build

cd /Users/rohan/.config/superpowers/worktrees/usealmanac/hosted-baseline-convergence
git diff --check
```

