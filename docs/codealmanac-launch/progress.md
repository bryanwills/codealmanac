# Launch Progress

Status: active.
Updated: 2026-07-02.

This file tracks the rough percentage estimates used in RelayForge updates.
Percentages are planning estimates, not accounting metrics.

## Latest RelayForge Update

Sent: 2026-07-02 after Slice 49 token-storage hardening local verification.

Route:

```bash
doppler run --project almanac --config dev -- \
  relayforge reply \
  --config /Users/rohan/Desktop/Projects/relayforge/relay.config.json \
  --binding rohan-almanac-main "..."
```

Note: Slice 49 was not deployed immediately. Deployment is intentionally
batched with the next infrastructure/deploy gate so database migration and
backend rollout happen together.

## Percentages

| Area | Latest | Previous | Basis |
| --- | ---: | ---: | --- |
| CodeAlmanac backend/local | 95% | 95% | Slice 49 is hosted token-storage work; local worker behavior is unchanged. |
| CodeAlmanac CLI/public UX | 91% | 91% | No CLI change after Slice 45 retry. |
| CodeAlmanac-hosted backend/auth/API | 95% | 94% | GitHub provider tokens are encrypted at rest with Fernet/MultiFernet, store/service decrypt failures are mapped, and migration guards prevent plaintext rename into ciphertext. |
| Hosted frontend/onboarding | 60% | 60% | No frontend behavior change after Slice 47 setup summary. |
| Infra/deploy rename | 90% | 89% | `GITHUB_TOKEN_ENCRYPTION_KEYS` is set in Doppler `codealmanac/prd`; migration/deploy intentionally deferred for a batched rollout. |

## Update Rule

After each verified slice:

1. Move the old `Latest` values into `Previous`.
2. Set new `Latest` values.
3. Send the same values through RelayForge.
4. Record command success or failure in the worklog.
