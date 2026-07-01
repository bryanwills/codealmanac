# Slice 91 - Serve Job Polling

## Scope

Make the read-only `serve` jobs views refresh while queued or running jobs are
active.

This slice covers:

- `#/jobs` polling when any listed run is `queued` or `running`
- `#/jobs/<run-id>` polling while that run is `queued` or `running`
- clearing the polling timer when the browser route or selected wiki changes
- tests that keep this as a read-only viewer behavior
- browser dogfood against a run that moves from `running` to `done`

Out of scope:

- browser-side cancel, attach, or retry controls
- server-sent events or websockets
- changing the runs service, queue worker, or lifecycle state machine
- reading raw provider transcript files

## Current Shape

`ViewerService` already exposes run records and run logs through read-only DTOs.
`server/app.py` maps those DTOs to `/api/jobs` and `/api/jobs/{run_id}`. The
static viewer renders the result once and then stays stale even if a background
worker advances the run record.

The viewer is the right layer for a small timer. The server and service should
continue to answer read queries only.

## Design

```javascript
// arch: browser timer refreshes read model; services stay read-only
renderJobs(context)
  -> viewerApi.jobs(wiki)
  -> render current run list
  -> schedule refresh only if a run is queued/running

renderJob(context, runId)
  -> viewerApi.job(runId, wiki)
  -> render current run detail/log
  -> schedule refresh only if that run is queued/running

clearJobPolling()
  -> called before every hash route render and before wiki switching
```

Cosmic Python chapter 12 frames the boundary I am using here: "reads
(queries) and writes (commands) are different, so they should be treated
differently." The polling loop is a read-side freshness behavior; it must not
become run-control machinery.

## Implementation Notes

- Keep polling state local to `server/assets/viewer/jobs.js`.
- Export `clearJobPolling` and call it from `viewer/main.js` before route
  dispatch and before switching workspaces.
- Use the existing JSON APIs. Do not add new server endpoints.
- Poll only for active statuses: `queued` and `running`.
- Keep the interval modest and explicit in one constant.

## Tests

- Static asset/server test asserts the jobs module exports the polling cleanup,
  uses `setTimeout`, and recognizes `queued`/`running`.
- Architecture read-only test continues to prevent `serve` from importing run
  mutation requests.
- ES module syntax check for `jobs.js` and `main.js`.
- Browser dogfood: open a running job detail, finish the run from the service,
  and verify the browser updates to `done` without manual refresh.
