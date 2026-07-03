# Launch Progress

Status: active.
Updated: 2026-07-03.

This file tracks the rough percentage estimates used in RelayForge updates.
Percentages are planning estimates, not accounting metrics.

## Latest RelayForge Update

Sent: 2026-07-03 after Slice 79 root uninstall split publish and smoke.

Route:

```bash
doppler run --project almanac --config dev -- \
  relayforge reply \
  --config /Users/rohan/Desktop/Projects/relayforge/relay.config.json \
  --binding rohan-almanac-main "..."
```

Published CLI `0.1.9` removes root uninstall's stale local-scheduler coupling.
GitHub Actions publish run `28672818638` passed full tests, lint, diff hygiene,
build, Twine checks, artifact upload, and PyPI upload. Fresh public PyPI
install smoke passed with `--refresh --no-cache`: root uninstall no longer
shows `--keep-automation` or automation JSON fields, and explicit
`codealmanac automation uninstall` remains available.

## Latest Local Notes

2026-07-03 provider correction:

- Vercel production was re-linked to project `thealmanac/codealmanac-hosted`
  and redeployed. `https://www.codealmanac.com` now serves deployment
  `dpl_BNAWQDiWydrtXUXfM1D4f61FiwCB`.
- Hosted Modal app `codealmanac-hosted-updates` was redeployed with the current
  `codealmanac` git SHA. Modal image logs showed `codealmanac 0.1.9`.
- Architecture cleanup notes now live under
  `docs/refactor-audit-2026-07-03-hosted-local-architecture/`.

## Percentages

| Area | Latest | Previous | Basis |
| --- | ---: | ---: | --- |
| CodeAlmanac backend/local | 97% | 97% | No local engine change in Slice 79; full source gates still passed after the setup/uninstall split. |
| CodeAlmanac CLI/public UX | 100% | 100% | Published CLI `0.1.9` passed public install smoke; root uninstall is now scoped to setup-owned artifacts, while automation teardown remains explicit. |
| CodeAlmanac-hosted backend/auth/API | 100% | 100% | Slice 75 added production `/v1/repositories`; production repo list and repo status pass without per-repo permission fanout. |
| Hosted frontend/onboarding | 100% | 99% | Slice 76 shipped repository readiness, capture handoff, maintained branches, and per-branch delivery to Vercel; Chrome verified production with no console errors. |
| Infra/deploy rename | 100% | 99% | Vercel now targets `thealmanac/codealmanac-hosted`, Render health is live, and Modal `codealmanac-hosted-updates` was redeployed with current `codealmanac` `0.1.9` engine logs. |

## Update Rule

After each verified slice:

1. Move the old `Latest` values into `Previous`.
2. Set new `Latest` values.
3. Send the same values through RelayForge.
4. Record command success or failure in the worklog.
