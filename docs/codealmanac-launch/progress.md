# Launch Progress

Status: active.
Updated: 2026-07-02.

This file tracks the rough percentage estimates used in RelayForge updates.
Percentages are planning estimates, not accounting metrics.

## Latest RelayForge Update

Sent: 2026-07-02 after Slice 56 PyPI publish completion.

Route:

```bash
doppler run --project almanac --config dev -- \
  relayforge reply \
  --config /Users/rohan/Desktop/Projects/relayforge/relay.config.json \
  --binding rohan-almanac-main "..."
```

Note: rate limits were postponed. PyPI Trusted Publishing is now working for
CodeAlmanac `0.1.0`; the package is public on PyPI and the `uv tool install`
smoke passed with Python 3.12.

## Percentages

| Area | Latest | Previous | Basis |
| --- | ---: | ---: | --- |
| CodeAlmanac backend/local | 96% | 96% | CodeAlmanac local/backend unchanged in Slice 56. |
| CodeAlmanac CLI/public UX | 98% | 95% | PyPI `0.1.0` is published and `uv tool install --python 3.12 codealmanac==0.1.0` works from a fresh tool dir. |
| CodeAlmanac-hosted backend/auth/API | 96% | 96% | Hosted backend/auth/API unchanged in Slice 56; AuthKit callback issue remains the next active pressure test. |
| Hosted frontend/onboarding | 78% | 78% | Hosted `/setup` remains verified unauthenticated; signed-in production walkthrough remains open. |
| Infra/deploy rename | 98% | 96% | PyPI Trusted Publishing provider setup is complete; remaining infra work is provider cleanup and auth/onboarding live verification. |

## Update Rule

After each verified slice:

1. Move the old `Latest` values into `Previous`.
2. Set new `Latest` values.
3. Send the same values through RelayForge.
4. Record command success or failure in the worklog.
