# Launch Progress

Status: active.
Updated: 2026-07-02.

This file tracks the rough percentage estimates used in RelayForge updates.
Percentages are planning estimates, not accounting metrics.

## Latest RelayForge Update

Sent: 2026-07-02 after Slice 33 hosted stale delivery outcomes.

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
| CodeAlmanac backend/local | 92% | 92% | Slice 33 changed hosted delivery only; the local package API and local worker maturity are unchanged. |
| CodeAlmanac CLI/public UX | 64% | 64% | Slice 33 does not add public CLI commands; cloud capture hook upload remains the latest CLI movement. |
| CodeAlmanac-hosted backend/auth/API | 65% | 62% | Hosted expected-head drift now records a deterministic terminal `stale` run outcome with run-event evidence instead of bubbling delivery errors. |
| Hosted frontend/onboarding | 17% | 15% | Frontend DTOs, run status metadata, and status icons now render the backend `stale` state; onboarding/configuration screens are still not implemented. |
| Infra/deploy rename | 15% | 15% | Slice 33 does not change deployment naming or provider configuration. |

## Update Rule

After each verified slice:

1. Move the old `Latest` values into `Previous`.
2. Set new `Latest` values.
3. Send the same values through RelayForge.
4. Record command success or failure in the worklog.
