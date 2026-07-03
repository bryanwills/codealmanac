# Worklog

## 2026-07-03

- Confirmed `codealmanac` has a wide flat service/workflow shape that obscures the product model.
- Confirmed `codealmanac-hosted` still uses package name `almanac`.
- Confirmed hosted Modal worker source lives in top-level `backend/modal_app`.
- Confirmed hosted `updates` package contains branch policy, bundle materialization, queueing, worker invocation, cancellation, completion, retry, and delivery.
- Confirmed local `control/store.py` is the largest local file at more than 1000 lines.
- Confirmed hosted `conversations/store.py` is the largest hosted backend file at nearly 700 lines.
- Corrected Vercel deployment target earlier in the run: production now points at project `thealmanac/codealmanac-hosted` and serves `https://www.codealmanac.com`.
- Corrected hosted Modal worker pin earlier in the run: `codealmanac-hosted-updates` now installs `codealmanac` from current git SHA and image logs showed `codealmanac 0.1.9`.

