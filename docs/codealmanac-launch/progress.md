# Launch Progress

Status: active.
Updated: 2026-07-02.

This file tracks the rough percentage estimates used in RelayForge updates.
Percentages are planning estimates, not accounting metrics.

## Latest RelayForge Update

Sent: 2026-07-02 after Slice 44 cloud run cancellation and production deploy.

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
| CodeAlmanac CLI/public UX | 90% | 90% | `codealmanac runs cancel <run-id>` is pushed to `origin/dev` at `a7cbc7d5`. |
| CodeAlmanac-hosted backend/auth/API | 90% | 90% | Hosted cancellation is pushed to the launch branch and fast-forwarded to hosted `main` at `0e17a34`. |
| Hosted frontend/onboarding | 43% | 43% | Frontend DTOs, status metadata, and BFF allowlist understand `cancelled`; visible cancel UI remains future work. |
| Infra/deploy rename | 82% | 72% | Vercel production and Render backend are live on the Slice 44 code; hosted `main` now matches the launch branch. |

## Update Rule

After each verified slice:

1. Move the old `Latest` values into `Previous`.
2. Set new `Latest` values.
3. Send the same values through RelayForge.
4. Record command success or failure in the worklog.
