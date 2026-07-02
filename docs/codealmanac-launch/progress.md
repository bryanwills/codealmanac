# Launch Progress

Status: active.
Updated: 2026-07-02.

This file tracks the rough percentage estimates used in RelayForge updates.
Percentages are planning estimates, not accounting metrics.

## Latest RelayForge Update

Sent: 2026-07-02 after Slice 32 hosted run events.

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
| CodeAlmanac backend/local | 92% | 92% | Slice 32 changed hosted persistence only; the local package API and local worker maturity are unchanged. |
| CodeAlmanac CLI/public UX | 64% | 64% | Slice 32 does not add public CLI commands; cloud capture hook upload remains the latest CLI movement. |
| CodeAlmanac-hosted backend/auth/API | 62% | 58% | Hosted runs now have SQL-backed `run_events` recorded from queued/running/delivered/failed transitions, matching the local run/run-event spine. |
| Hosted frontend/onboarding | 15% | 15% | Browser onboarding/configuration screens are still not implemented. |
| Infra/deploy rename | 15% | 15% | Slice 32 does not change deployment naming or provider configuration. |

## Update Rule

After each verified slice:

1. Move the old `Latest` values into `Previous`.
2. Set new `Latest` values.
3. Send the same values through RelayForge.
4. Record command success or failure in the worklog.
