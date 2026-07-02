# Launch Progress

Status: active.
Updated: 2026-07-02.

This file tracks the rough percentage estimates used in RelayForge updates.
Percentages are planning estimates, not accounting metrics.

## Latest RelayForge Update

Sent: 2026-07-02 after Slice 44 cloud run cancellation.

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
| CodeAlmanac backend/local | 95% | 95% | Slice 44 is cloud-run control; local worker behavior is unchanged. |
| CodeAlmanac CLI/public UX | 90% | 88% | `codealmanac runs cancel <run-id>` now exists alongside list/show/logs/start. |
| CodeAlmanac-hosted backend/auth/API | 90% | 88% | Hosted runs now support real cancellation through SQL state plus Modal function-call cancellation. |
| Hosted frontend/onboarding | 43% | 42% | Frontend DTOs, status metadata, and BFF allowlist now understand `cancelled` runs, though no visible cancel button has been added. |
| Infra/deploy rename | 72% | 72% | Slice 44 has not yet changed provider naming; deploy state will be updated after this slice lands. |

## Update Rule

After each verified slice:

1. Move the old `Latest` values into `Previous`.
2. Set new `Latest` values.
3. Send the same values through RelayForge.
4. Record command success or failure in the worklog.
