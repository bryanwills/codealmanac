# Launch Progress

Status: active.
Updated: 2026-07-03.

This file tracks the rough percentage estimates used in RelayForge updates.
Percentages are planning estimates, not accounting metrics.

## Latest RelayForge Update

Sent: 2026-07-03 after Slice 62 branch-trigger delivery guard.

Route:

```bash
doppler run --project almanac --config dev -- \
  relayforge reply \
  --config /Users/rohan/Desktop/Projects/relayforge/relay.config.json \
  --binding rohan-almanac-main "..."
```

Note: hosted branch-push updates now ignore non-truncated `.almanac/`-only
pushes before policy lookup so CodeAlmanac delivery commits do not loop into
new runs. Delivery commits and PRs now use `docs almanac: <summary>`. Production
Render deploy `dep-d93mceekanas73aeia30` is live on commit `fdad34d`; both
canonical API and Render health checks returned `{"status":"ok"}`.

## Percentages

| Area | Latest | Previous | Basis |
| --- | ---: | ---: | --- |
| CodeAlmanac backend/local | 96% | 96% | CodeAlmanac local/backend unchanged in Slice 62. |
| CodeAlmanac CLI/public UX | 98% | 98% | PyPI `0.1.1` remains published and install-smoked; no CLI code changed in Slice 62. |
| CodeAlmanac-hosted backend/auth/API | 99% | 99% | Branch-trigger loop guard and deterministic `docs almanac:` delivery messages are implemented, tested, pushed, and deployed. |
| Hosted frontend/onboarding | 92% | 92% | Frontend unchanged in Slice 62; repository settings remained verified in Slice 60 and auth/setup in Chrome after Slice 61. |
| Infra/deploy rename | 99% | 99% | Render is live on `fdad34d`; Vercel/frontend unchanged for this backend-only slice. |

## Update Rule

After each verified slice:

1. Move the old `Latest` values into `Previous`.
2. Set new `Latest` values.
3. Send the same values through RelayForge.
4. Record command success or failure in the worklog.
