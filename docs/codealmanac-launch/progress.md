# Launch Progress

Status: active.
Updated: 2026-07-02.

This file tracks the rough percentage estimates used in RelayForge updates.
Percentages are planning estimates, not accounting metrics.

## Latest RelayForge Update

Sent: 2026-07-02 after Slice 28 cloud capture install.

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
| CodeAlmanac backend/local | 90% | 88% | Slice 29 makes local capture hooks upload transcript artifacts and metadata; local trigger/run/workspace/delivery maturity is unchanged. |
| CodeAlmanac CLI/public UX | 64% | 62% | Hidden capture hook now performs cloud upload, while repo, runs, status, and open commands remain. |
| CodeAlmanac-hosted backend/auth/API | 45% | 40% | Hosted now accepts capture-token artifact and turn uploads; repo API, run storage, worker source-bundle materialization, and rate limits remain. |
| Hosted frontend/onboarding | 15% | 15% | Slice 28 added DTO parity only; browser onboarding/configuration screens are still not implemented. |
| Infra/deploy rename | 10% | 10% | Slice 29 changed capture/API/CLI only. |

## Update Rule

After each verified slice:

1. Move the old `Latest` values into `Previous`.
2. Set new `Latest` values.
3. Send the same values through RelayForge.
4. Record command success or failure in the worklog.
