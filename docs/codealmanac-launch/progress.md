# Launch Progress

Status: active.
Updated: 2026-07-02.

This file tracks the rough percentage estimates used in RelayForge updates.
Percentages are planning estimates, not accounting metrics.

## Latest RelayForge Update

Sent: 2026-07-02 after Slice 17 verification.

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
| CodeAlmanac backend/local | 76% | 72% | Slice 17 added local setup workflow, GitHub checkout detection, branch policy registration, hook installation, and working-tree delivery parity. |
| CodeAlmanac CLI/public UX | 18% | 13% | `codealmanac local setup` is now a real public local command with JSON/text output. Broader launch CLI reshaping remains. |
| CodeAlmanac-hosted backend/auth/API | 8% | 8% | WorkOS/Doppler setup and hosted rename groundwork exist; public API migration is not implemented yet. |
| Hosted frontend/onboarding | 5% | 5% | Existing frontend is deployed under CodeAlmanac; new onboarding/configuration screens are not implemented yet. |
| Infra/deploy rename | 5% | 5% | GitHub rename, Modal, Render, Vercel production deploy, and health checks were exercised; durable cleanup remains. |

## Update Rule

After each verified slice:

1. Move the old `Latest` values into `Previous`.
2. Set new `Latest` values.
3. Send the same values through RelayForge.
4. Record command success or failure in the worklog.
