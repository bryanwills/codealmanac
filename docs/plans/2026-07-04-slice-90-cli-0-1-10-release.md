# Slice 90: CLI 0.1.10 Release

## Intent

Publish the Slice 89 CLI run-surface cleanup so fresh PyPI installs get the
launch command contract.

The cleanup is already behavior-complete on a release branch based on
`origin/main`. This slice is the distribution gate: bump the package version,
prove the wheel, land the release branch on `main`, run the trusted publishing
workflow, and smoke the public package.

## Read Before Coding

- `MANUAL.md`: release work is still codebase-shaping work.
- `docs/codealmanac-launch/cli-inconsistency-ledger.md`: current command
  contract to verify against the packaged CLI.
- `docs/codealmanac-launch/verification-matrix.md`: release evidence must be
  recorded there after the public smoke passes.
- `.github/workflows/publish.yml`: PyPI publishing is allowed only from
  `refs/heads/main` and the workflow's `confirm_version` must match
  `pyproject.toml`.

Cosmic Python relevance: the command chapter's distinction between commands and
events is why this release does not restore `sync` or scheduler verbs. Public
commands express user intent; local trigger events are private facts recorded
behind the local service boundary.

## Scope

Must change:

- Bump `pyproject.toml` from `0.1.9` to `0.1.10`.
- Build and check local release artifacts.
- Smoke the local wheel in an isolated environment.
- Push the verified release branch.
- Fast-forward/push `main` only after local verification passes.
- Run the GitHub Actions `publish` workflow with `confirm_version=0.1.10`.
- Smoke a fresh public install from PyPI after propagation.
- Update launch worklog, verification matrix, progress percentages, and next
  agent brief with exact evidence.
- Send a RelayForge update with the same percentage table after public smoke.

Out of scope:

- New CLI product commands.
- Hosted API/frontend changes.
- Pulling unrelated `dev` documentation into `main`.

## Verification

Local gates before pushing `main`:

```bash
uv run pytest -q
uv run ruff check .
git diff --check
rm -rf dist && uv build --out-dir dist
uvx twine check dist/*
python -m venv /tmp/codealmanac-wheel-smoke
/tmp/codealmanac-wheel-smoke/bin/python -m pip install dist/*.whl
/tmp/codealmanac-wheel-smoke/bin/codealmanac --version
/tmp/codealmanac-wheel-smoke/bin/codealmanac --help
/tmp/codealmanac-wheel-smoke/bin/codealmanac local --help
```

Remote gates after `main` push:

```bash
gh workflow run publish.yml --repo AlmanacCode/codealmanac --ref main \
  -f confirm_version=0.1.10
gh run watch <run-id> --repo AlmanacCode/codealmanac --exit-status
uv tool install --python 3.12 --refresh --no-cache --force codealmanac==0.1.10
codealmanac --version
codealmanac --help
codealmanac local --help
```

The public smoke must prove `sync`, root scheduled `automation`, `local update`,
and `local jobs` are absent from the launch-facing help while
`codealmanac local runs` and the private package entrypoints are present where
expected.

## Risk

PyPI propagation can lag. If `uv tool install ... codealmanac==0.1.10` cannot
see the version immediately after a successful publish, wait and retry with
`--refresh --no-cache`; do not claim the public release until the fresh install
smoke passes.
