# Launch Progress

Status: active.
Updated: 2026-07-03.

This file tracks the rough percentage estimates used in RelayForge updates.
Percentages are planning estimates, not accounting metrics.

## Latest RelayForge Update

Sent: 2026-07-03 after Slice 60 capture-token schema repair.

Route:

```bash
doppler run --project almanac --config dev -- \
  relayforge reply \
  --config /Users/rohan/Desktop/Projects/relayforge/relay.config.json \
  --binding rohan-almanac-main "..."
```

Note: production repository settings now loads. The root cause was a missing
`public.capture_tokens` table while backend code already queried
`CaptureTokenRow`. Migration `20260703010000` was applied and marked applied in
Supabase history. Signed-in Chrome verification reached repository settings, and
Render logs showed fresh `/api/capture/status` `200 OK`.

## Percentages

| Area | Latest | Previous | Basis |
| --- | ---: | ---: | --- |
| CodeAlmanac backend/local | 96% | 96% | CodeAlmanac local/backend unchanged in Slice 60. |
| CodeAlmanac CLI/public UX | 98% | 98% | PyPI `0.1.1` remains published and install-smoked; no CLI code changed in Slice 60. |
| CodeAlmanac-hosted backend/auth/API | 99% | 98% | Production DB now includes capture credential storage and `/api/capture/status` returns 200 for signed-in settings loads. |
| Hosted frontend/onboarding | 92% | 88% | Signed-in production repository settings now renders readiness, branch, and delivery surfaces. |
| Infra/deploy rename | 99% | 99% | Production Supabase migration history includes `20260703010000`; Render and Vercel surfaces remain live. |

## Update Rule

After each verified slice:

1. Move the old `Latest` values into `Previous`.
2. Set new `Latest` values.
3. Send the same values through RelayForge.
4. Record command success or failure in the worklog.
