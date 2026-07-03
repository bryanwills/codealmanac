# Launch Progress

Status: active.
Updated: 2026-07-03.

This file tracks the rough percentage estimates used in RelayForge updates.
Percentages are planning estimates, not accounting metrics.

## Latest RelayForge Update

Sent: 2026-07-03 after Slice 76 hosted repository-settings UX verification.

Route:

```bash
doppler run --project almanac --config dev -- \
  relayforge reply \
  --config /Users/rohan/Desktop/Projects/relayforge/relay.config.json \
  --binding rohan-almanac-main "..."
```

Published CLI `0.1.6` includes the canonical `codealmanac repo list` command,
production `/v1/repositories` works, and Chrome verified the live hosted
repository settings page after the Vercel deployment.

## Percentages

| Area | Latest | Previous | Basis |
| --- | ---: | ---: | --- |
| CodeAlmanac backend/local | 97% | 97% | No local engine change in Slice 76; previous full suite passed with the repo-list service/workflow additions. |
| CodeAlmanac CLI/public UX | 100% | 100% | Published CLI `0.1.6` setup/whoami/repo list/repo status/capture status passed against production from a clean Chrome-approved HOME. |
| CodeAlmanac-hosted backend/auth/API | 100% | 100% | Slice 75 added production `/v1/repositories`; production repo list and repo status pass without per-repo permission fanout. |
| Hosted frontend/onboarding | 100% | 99% | Slice 76 shipped repository readiness, capture handoff, maintained branches, and per-branch delivery to Vercel; Chrome verified production with no console errors. |
| Infra/deploy rename | 99% | 99% | Hosted frontend deployed to Vercel production at `bff009b` and aliased to `https://www.codealmanac.com`. |

## Update Rule

After each verified slice:

1. Move the old `Latest` values into `Previous`.
2. Set new `Latest` values.
3. Send the same values through RelayForge.
4. Record command success or failure in the worklog.
