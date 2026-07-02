# Slice 52: PyPI Trusted Publishing

Status: planned.
Date: 2026-07-02.

## Scope

Turn PyPI publishing from a blocked local-token operation into a documented
trusted-publishing release path.

This slice covers:

- replace the disabled `.github/workflows/publish.yml` placeholder with a
  manual PyPI Trusted Publishing workflow
- use the official `pypa/gh-action-pypi-publish@release/v1` action
- keep publishing gated to the `main` branch
- require a human-entered version confirmation that must match
  `pyproject.toml`
- use GitHub environment `pypi`, matching the PyPI trusted publisher config
- update `RELEASE.md` with the exact one-time PyPI setup fields
- update launch progress, worklog, verification matrix, and next-agent brief

This slice does not cover:

- creating the PyPI trusted publisher in the PyPI UI
- running the publish workflow
- publishing from `dev`
- adding a PyPI token or GitHub secret

## Design

Official PyPI guidance recommends the PyPA publish action for trusted
publishing rather than hand-writing the OIDC exchange. The workflow follows that
shape:

```yaml
permissions:
  contents: read
  id-token: write

environment:
  name: pypi
  url: https://pypi.org/p/codealmanac

uses: pypa/gh-action-pypi-publish@release/v1
```

Publishing stays manual because the launch is still being coordinated. The
workflow refuses non-`main` refs and refuses versions that do not match the
manual `confirm_version` input.

PyPI trusted publisher settings:

```text
PyPI project: codealmanac
Owner: AlmanacCode
Repository: codealmanac
Workflow filename: publish.yml
Environment name: pypi
```

## Files

- `.github/workflows/publish.yml`
- `RELEASE.md`
- `docs/codealmanac-launch/next-agent-brief.md`
- `docs/codealmanac-launch/progress.md`
- `docs/codealmanac-launch/verification-matrix.md`
- `docs/codealmanac-launch/worklog.md`

## Verification

```text
uv run pytest
uv run ruff check .
rm -rf dist
uv build --out-dir dist
uvx twine check dist/*
python - <<'PY'
import yaml
with open(".github/workflows/publish.yml", "r", encoding="utf-8") as f:
    yaml.safe_load(f)
PY
git diff --check
```
