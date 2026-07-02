# Launch Progress

Status: active.
Updated: 2026-07-02.

This file tracks the rough percentage estimates used in RelayForge updates.
Percentages are planning estimates, not accounting metrics.

## Latest RelayForge Update

Sent: 2026-07-02 after Slice 31 hosted direct maintenance API.

Route:

```bash
doppler run --project almanac --config dev -- \
  relayforge reply \
  --config /Users/rohan/Desktop/Projects/relayforge/relay.config.json \
  --binding rohan-almanac-main "..."
```

Note: `DISCORD_BOT_TOKEN` is currently present in Doppler `almanac/dev`.
It was not present in `codealmanac/prd` when checked.

## Percentages

| Area | Latest | Previous | Basis |
| --- | ---: | ---: | --- |
| CodeAlmanac backend/local | 92% | 90% | Slice 31 added the `codealmanac.maintenance` package API over the real init/ingest workflows, giving hosted a typed non-CLI caller path. |
| CodeAlmanac CLI/public UX | 64% | 64% | Slice 31 does not add public CLI commands; cloud capture hook upload remains the latest CLI movement. |
| CodeAlmanac-hosted backend/auth/API | 58% | 52% | Hosted Modal now calls `codealmanac.maintenance` directly, removes the production CLI subprocess bridge, and keeps source-to-operation mapping typed. |
| Hosted frontend/onboarding | 15% | 15% | Browser onboarding/configuration screens are still not implemented. |
| Infra/deploy rename | 15% | 12% | Modal runtime now pins to the CodeAlmanac commit that contains the maintenance API used by the hosted worker. |

## Update Rule

After each verified slice:

1. Move the old `Latest` values into `Previous`.
2. Set new `Latest` values.
3. Send the same values through RelayForge.
4. Record command success or failure in the worklog.
