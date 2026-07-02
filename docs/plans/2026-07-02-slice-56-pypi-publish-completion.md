# Slice 56: PyPI Publish Completion

Status: implemented.
Date: 2026-07-02.

## Scope

Complete the PyPI release path after the trusted publisher entry was added for
the `codealmanac` project.

This slice covers:

- rerun `.github/workflows/publish.yml` on `main`
- wait for the workflow's build and publish jobs
- confirm PyPI serves `codealmanac` `0.1.0`
- smoke install the released CLI through the public `uv tool install` path
- update launch progress, worklog, verification matrix, and next-agent brief

This slice does not cover:

- changing package contents
- changing the release workflow
- broad auth/onboarding verification

## Result

GitHub Actions run `28619144624` succeeded on `main` at
`43ec4800311b2f66f6095bff231f5fde7740eb07`.

The build job passed tests, lint, diff hygiene, artifact build, Twine checks,
and artifact upload. The publish job successfully uploaded through
`pypa/gh-action-pypi-publish@release/v1`.

PyPI now serves both `0.1.0.dev0` and `0.1.0`; the simple index includes
provenance links for the `0.1.0` wheel and sdist.

Fresh install smoke passed:

```text
UV_TOOL_DIR=<tmp> UV_TOOL_BIN_DIR=<tmp> uv tool install --python 3.12 codealmanac==0.1.0
<tmp>/codealmanac --version
0.1.0
```

The installed CLI exposed the expected public command surface, including
`open`, `init`, `sync`, `local`, read commands, cloud auth commands, `capture`,
`repo`, `repos`, and `runs`.
