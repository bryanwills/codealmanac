# Launch Progress

Status: active.
Updated: 2026-07-02.

This file tracks the rough percentage estimates used in RelayForge updates.
Percentages are planning estimates, not accounting metrics.

## Latest RelayForge Update

Sent: 2026-07-02 after Slice 30 cloud source-bundle materialization.

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
| CodeAlmanac backend/local | 90% | 90% | Slice 30 changed hosted worker/source-bundle behavior only; local trigger/run/workspace/delivery maturity is unchanged. |
| CodeAlmanac CLI/public UX | 64% | 64% | Slice 30 does not add public CLI commands; cloud capture hook upload remains the latest CLI movement. |
| CodeAlmanac-hosted backend/auth/API | 52% | 45% | Hosted conversation ingest now requires source refs, exposes internal artifact reads, materializes worker `sources/`, and passes the folder to CodeAlmanac. |
| Hosted frontend/onboarding | 15% | 15% | Browser onboarding/configuration screens are still not implemented. |
| Infra/deploy rename | 12% | 10% | Modal runtime now installs the Python CodeAlmanac package from a pinned git ref instead of the old npm package. |

## Update Rule

After each verified slice:

1. Move the old `Latest` values into `Previous`.
2. Set new `Latest` values.
3. Send the same values through RelayForge.
4. Record command success or failure in the worklog.
