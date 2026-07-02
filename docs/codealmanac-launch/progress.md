# Launch Progress

Status: active.
Updated: 2026-07-02.

This file tracks the rough percentage estimates used in RelayForge updates.
Percentages are planning estimates, not accounting metrics.

## Latest RelayForge Update

Sent: 2026-07-02 after Slice 43 cloud setup copy.

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
| CodeAlmanac backend/local | 95% | 95% | Slice 43 is hosted frontend copy only; local worker behavior is unchanged. |
| CodeAlmanac CLI/public UX | 88% | 87% | Browser setup now presents the single cloud setup command and no longer advertises `almanac login`. |
| CodeAlmanac-hosted backend/auth/API | 88% | 88% | Slice 43 changes no backend API; Slice 42 Check Runs remain deployed. |
| Hosted frontend/onboarding | 42% | 35% | GitHub App install, CLI setup, capture-consent copy, and repo settings handoff now align with the cloud-first setup model. |
| Infra/deploy rename | 72% | 70% | Production Vercel deploy is live after the setup-copy change, and the GitHub App was verified with `checks: write`. |

## Update Rule

After each verified slice:

1. Move the old `Latest` values into `Previous`.
2. Set new `Latest` values.
3. Send the same values through RelayForge.
4. Record command success or failure in the worklog.
