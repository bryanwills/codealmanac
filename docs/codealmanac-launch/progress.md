# Launch Progress

Status: active.
Updated: 2026-07-03.

This file tracks the rough percentage estimates used in RelayForge updates.
Percentages are planning estimates, not accounting metrics.

## Latest RelayForge Update

Sent: 2026-07-03 after Slice 61 GitHub webhook contract hardening.

Route:

```bash
doppler run --project almanac --config dev -- \
  relayforge reply \
  --config /Users/rohan/Desktop/Projects/relayforge/relay.config.json \
  --binding rohan-almanac-main "..."
```

Note: hosted webhook intake now routes by `X-GitHub-Event`. Production Render
deploy `dep-d93lvet7vvec73fpsag0` is live on commit `c9b0da1`. A signed
synthetic `check_run` webhook returned `204` and was persisted as
`status=ignored`, proving unsupported events are no longer shape-sniffed into
repository or installation messages.

## Percentages

| Area | Latest | Previous | Basis |
| --- | ---: | ---: | --- |
| CodeAlmanac backend/local | 96% | 96% | CodeAlmanac local/backend unchanged in Slice 61. |
| CodeAlmanac CLI/public UX | 98% | 98% | PyPI `0.1.1` remains published and install-smoked; no CLI code changed in Slice 61. |
| CodeAlmanac-hosted backend/auth/API | 99% | 99% | Webhook intake now matches GitHub event-header routing and production smoke proves unsupported events are ignored. |
| Hosted frontend/onboarding | 92% | 92% | Frontend unchanged in Slice 61; repository settings remained verified in Slice 60. |
| Infra/deploy rename | 99% | 99% | Render is live on `c9b0da1`; Vercel/frontend unchanged for this backend-only slice. |

## Update Rule

After each verified slice:

1. Move the old `Latest` values into `Previous`.
2. Set new `Latest` values.
3. Send the same values through RelayForge.
4. Record command success or failure in the worklog.
