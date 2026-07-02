# Launch Progress

Status: active.
Updated: 2026-07-02.

This file tracks the rough percentage estimates used in RelayForge updates.
Percentages are planning estimates, not accounting metrics.

## Latest RelayForge Update

Sent: 2026-07-02 after Slice 41 hosted rename/provider convergence.

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
| CodeAlmanac backend/local | 95% | 95% | Slice 41 is hosted/provider-only; local worker behavior is unchanged. |
| CodeAlmanac CLI/public UX | 87% | 87% | Slice 41 adds no public CLI verbs. |
| CodeAlmanac-hosted backend/auth/API | 86% | 85% | Active hosted runtime identity now says `codealmanac-hosted`; the exact commit is deployed on Render. |
| Hosted frontend/onboarding | 35% | 35% | Slice 41 changes support defaults and deploy identity, not onboarding screens. |
| Infra/deploy rename | 70% | 15% | GitHub repo, Vercel project, Render service, Doppler project, Modal target, production frontend, and backend health are verified under CodeAlmanac names. |

## Update Rule

After each verified slice:

1. Move the old `Latest` values into `Previous`.
2. Set new `Latest` values.
3. Send the same values through RelayForge.
4. Record command success or failure in the worklog.
