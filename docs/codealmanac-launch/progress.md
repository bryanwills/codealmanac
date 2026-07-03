# Launch Progress

Status: active.
Updated: 2026-07-03.

This file tracks the rough percentage estimates used in RelayForge updates.
Percentages are planning estimates, not accounting metrics.

## Latest RelayForge Update

Sent: 2026-07-03 after Slice 71 production conversation-trigger smoke.

Route:

```bash
doppler run --project almanac --config dev -- \
  relayforge reply \
  --config /Users/rohan/Desktop/Projects/relayforge/relay.config.json \
  --binding rohan-almanac-main "..."
```

Note: production captured-conversation routing now passed a live maintained
branch trigger smoke. A routable Codex capture became a
`conversation_batch` run, delivered, and was visible in the production activity
feed.

## Percentages

| Area | Latest | Previous | Basis |
| --- | ---: | ---: | --- |
| CodeAlmanac backend/local | 96% | 96% | Local/backend unchanged in Slice 71; published CLI remains `0.1.4`. |
| CodeAlmanac CLI/public UX | 99% | 99% | Public CLI handled setup/open/capture/runs paths used by the production smoke. |
| CodeAlmanac-hosted backend/auth/API | 100% | 99% | Live branch trigger claimed captured conversation source, created a `conversation_batch` run, and delivered. |
| Hosted frontend/onboarding | 98% | 97% | Chrome verified `/setup`, repository dashboard, and activity feed with the delivered conversation-batch run. |
| Infra/deploy rename | 99% | 99% | Render is live on `eb8dba0`; Modal app `codealmanac-hosted-updates` is redeployed; Vercel frontend unchanged. |

## Update Rule

After each verified slice:

1. Move the old `Latest` values into `Previous`.
2. Set new `Latest` values.
3. Send the same values through RelayForge.
4. Record command success or failure in the worklog.
