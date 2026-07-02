# Launch Progress

Status: active.
Updated: 2026-07-02.

This file tracks the rough percentage estimates used in RelayForge updates.
Percentages are planning estimates, not accounting metrics.

## Latest RelayForge Update

Sent: 2026-07-02 after Slice 55 cloud setup checklist verification and
deployment.

Route:

```bash
doppler run --project almanac --config dev -- \
  relayforge reply \
  --config /Users/rohan/Desktop/Projects/relayforge/relay.config.json \
  --binding rohan-almanac-main "..."
```

Note: rate limits were postponed. PyPI Trusted Publishing workflow is on
CodeAlmanac `main` and its build/test/artifact gates pass. PyPI upload is
blocked by `invalid-publisher`; the remaining external action is adding the
matching trusted publisher entry in the PyPI `codealmanac` project.

## Percentages

| Area | Latest | Previous | Basis |
| --- | ---: | ---: | --- |
| CodeAlmanac backend/local | 96% | 96% | CodeAlmanac local/backend unchanged in Slice 55. |
| CodeAlmanac CLI/public UX | 95% | 95% | CLI/PyPI state unchanged in Slice 55; PyPI upload remains blocked by trusted publisher configuration. |
| CodeAlmanac-hosted backend/auth/API | 96% | 96% | Hosted backend/auth/API unchanged in Slice 55. |
| Hosted frontend/onboarding | 78% | 73% | Hosted `/setup` now has an ordered cloud setup checklist, route guardrails, passing frontend tests/build, and unauthenticated browser verification. |
| Infra/deploy rename | 96% | 96% | CodeAlmanac and hosted branch/main convergence remains done; PyPI provider configuration and provider cleanup remain. |

## Update Rule

After each verified slice:

1. Move the old `Latest` values into `Previous`.
2. Set new `Latest` values.
3. Send the same values through RelayForge.
4. Record command success or failure in the worklog.
