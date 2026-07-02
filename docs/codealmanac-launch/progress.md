# Launch Progress

Status: active.
Updated: 2026-07-02.

This file tracks the rough percentage estimates used in RelayForge updates.
Percentages are planning estimates, not accounting metrics.

## Latest RelayForge Update

Pending send: 2026-07-02 after Slice 27 cloud CLI auth.

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
| CodeAlmanac backend/local | 88% | 88% | Slice 27 changed cloud auth/CLI surface only; local trigger, run, workspace, delivery, init/update surfaces remain at prior maturity. |
| CodeAlmanac CLI/public UX | 52% | 40% | `setup`, `login`, `whoami`, and `logout` now exist for cloud auth; repo, capture, runs, status, and open commands remain. |
| CodeAlmanac-hosted backend/auth/API | 34% | 28% | `/v1` CLI auth aliases now exist on top of the WorkOS/AuthKit foundation; capture credentials, repo API, run storage, and worker APIs still remain. |
| Hosted frontend/onboarding | 15% | 15% | Slice 27 changed backend/CLI auth only; browser onboarding/configuration screens are still not implemented. |
| Infra/deploy rename | 10% | 10% | Slice 27 changed auth/API/CLI only. |

## Update Rule

After each verified slice:

1. Move the old `Latest` values into `Previous`.
2. Set new `Latest` values.
3. Send the same values through RelayForge.
4. Record command success or failure in the worklog.
