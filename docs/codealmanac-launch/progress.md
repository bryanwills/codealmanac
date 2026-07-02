# Launch Progress

Status: active.
Updated: 2026-07-02.

This file tracks the rough percentage estimates used in RelayForge updates.
Percentages are planning estimates, not accounting metrics.

## Latest RelayForge Update

Sent: 2026-07-02 after Slice 46 dashboard run actions and production deploy.

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
| CodeAlmanac backend/local | 95% | 95% | Slice 46 is hosted-frontend only; local worker behavior is unchanged. |
| CodeAlmanac CLI/public UX | 91% | 91% | No CLI change after Slice 45 retry; dashboard now exposes the same run controls. |
| CodeAlmanac-hosted backend/auth/API | 92% | 92% | No backend API change after Slice 45; Slice 46 consumes existing BFF commands. |
| Hosted frontend/onboarding | 52% | 44% | Repository activity rows now expose cancel/retry with pending and inline-error states. |
| Infra/deploy rename | 86% | 84% | Vercel production and Render backend are live on the Slice 46 commit. |

## Update Rule

After each verified slice:

1. Move the old `Latest` values into `Previous`.
2. Set new `Latest` values.
3. Send the same values through RelayForge.
4. Record command success or failure in the worklog.
