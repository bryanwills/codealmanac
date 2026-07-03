# Launch Progress

Status: active.
Updated: 2026-07-03.

This file tracks the rough percentage estimates used in RelayForge updates.
Percentages are planning estimates, not accounting metrics.

## Latest RelayForge Update

Sent: 2026-07-03 after Slice 63 production setup pressure test.

Route:

```bash
doppler run --project almanac --config dev -- \
  relayforge reply \
  --config /Users/rohan/Desktop/Projects/relayforge/relay.config.json \
  --binding rohan-almanac-main "..."
```

Note: production Chrome verified setup, repository list, repository settings,
reversible branch trigger/delivery save, and the CLI setup guide. Hosted
frontend commit `47b1ada` is deployed to Vercel production at
`codealmanac-hosted-gutvigm88-thealmanac.vercel.app` and aliased to
`https://www.codealmanac.com`.

## Percentages

| Area | Latest | Previous | Basis |
| --- | ---: | ---: | --- |
| CodeAlmanac backend/local | 96% | 96% | CodeAlmanac local/backend unchanged in Slice 63. |
| CodeAlmanac CLI/public UX | 98% | 98% | PyPI `0.1.1` remains published and install-smoked; setup guide remains PyPI-shaped in production. |
| CodeAlmanac-hosted backend/auth/API | 99% | 99% | Backend unchanged in Slice 63; production BFF trigger reads/writes succeeded through the frontend session. |
| Hosted frontend/onboarding | 95% | 92% | Production Chrome verified setup, repository list, settings, live settings summary, reversible branch trigger save/restore, and CLI setup guide after Vercel deploy. |
| Infra/deploy rename | 99% | 99% | Vercel production is live on `47b1ada`; Render remains live on `fdad34d`. |

## Update Rule

After each verified slice:

1. Move the old `Latest` values into `Previous`.
2. Set new `Latest` values.
3. Send the same values through RelayForge.
4. Record command success or failure in the worklog.
