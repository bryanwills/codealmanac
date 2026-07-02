# Launch Progress

Status: active.
Updated: 2026-07-02.

This file tracks the rough percentage estimates used in RelayForge updates.
Percentages are planning estimates, not accounting metrics.

## Latest RelayForge Update

Sent: 2026-07-02 after Slice 53 hosted main convergence verification.

Route:

```bash
doppler run --project almanac --config dev -- \
  relayforge reply \
  --config /Users/rohan/Desktop/Projects/relayforge/relay.config.json \
  --binding rohan-almanac-main "..."
```

Note: rate limits were postponed. PyPI Trusted Publishing workflow is on
CodeAlmanac `main`; the remaining external action is adding the trusted
publisher entry in the PyPI `codealmanac` project.

## Percentages

| Area | Latest | Previous | Basis |
| --- | ---: | ---: | --- |
| CodeAlmanac backend/local | 95% | 95% | Local engine and control surfaces are unchanged in Slice 53. |
| CodeAlmanac CLI/public UX | 94% | 94% | PyPI release workflow is on `main`; actual publish still requires PyPI project configuration and workflow run. |
| CodeAlmanac-hosted backend/auth/API | 96% | 96% | Hosted backend/auth/API unchanged in Slice 53. |
| Hosted frontend/onboarding | 73% | 72% | Hosted setup/login guardrails are now converged to hosted `main`; signed-in production walkthrough still remains. |
| Infra/deploy rename | 96% | 95% | CodeAlmanac `main` and hosted `main` are converged with verified launch branches; PyPI setup/run and provider cleanup remain. |

## Update Rule

After each verified slice:

1. Move the old `Latest` values into `Previous`.
2. Set new `Latest` values.
3. Send the same values through RelayForge.
4. Record command success or failure in the worklog.
