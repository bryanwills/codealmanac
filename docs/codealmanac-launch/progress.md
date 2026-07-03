# Launch Progress

Status: active.
Updated: 2026-07-03.

This file tracks the rough percentage estimates used in RelayForge updates.
Percentages are planning estimates, not accounting metrics.

## Latest RelayForge Update

Sent: 2026-07-03 after Slice 73 hosted setup copy deploy.

Route:

```bash
doppler run --project almanac --config dev -- \
  relayforge reply \
  --config /Users/rohan/Desktop/Projects/relayforge/relay.config.json \
  --binding rohan-almanac-main "..."
```

Note: hosted production now matches published CLI `0.1.5`: `codealmanac setup`
does cloud login plus agent instructions, and capture is the separate explicit
`codealmanac capture enable` step. Chrome verified `/setup` and
`/dashboard/local-agent-access` on `https://www.codealmanac.com`.

## Percentages

| Area | Latest | Previous | Basis |
| --- | ---: | ---: | --- |
| CodeAlmanac backend/local | 96% | 96% | Local/backend unchanged in Slice 73. |
| CodeAlmanac CLI/public UX | 100% | 100% | Published CLI `0.1.5` remains the source of truth for setup/capture commands. |
| CodeAlmanac-hosted backend/auth/API | 100% | 100% | Unchanged in Slice 73; live trigger path was already verified in Slice 71. |
| Hosted frontend/onboarding | 99% | 98% | Production setup and CLI guide copy now match the public CLI; Chrome verified stale setup-capture wording is gone. |
| Infra/deploy rename | 99% | 99% | Hosted frontend deployed to Vercel production at `af0d7da` and aliased to `https://www.codealmanac.com`. |

## Update Rule

After each verified slice:

1. Move the old `Latest` values into `Previous`.
2. Set new `Latest` values.
3. Send the same values through RelayForge.
4. Record command success or failure in the worklog.
