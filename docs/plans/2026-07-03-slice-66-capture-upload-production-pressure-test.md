# Slice 66: Capture Upload Production Pressure Test

## Purpose

Prove the published CodeAlmanac CLI can issue a cloud capture credential, install capture hooks into an isolated user home, upload a raw transcript artifact to production, upload normalized turn routing metadata, and cleanly revoke the credential.

This slice pressure-tests the seam between:

- `codealmanac capture ...`
- `codealmanac __capture-hook`
- `POST /v1/capture/credentials`
- `POST /v1/capture/artifacts`
- `POST /v1/capture/turns`

## Out Of Scope

- Installing hooks into the real `~/.codex` or `~/.claude`.
- Uploading a real private transcript.
- Triggering a full wiki update run from the uploaded source.
- Changing the GitHub webhook contract; `2026-07-03-github-webhook-contract-hardening.md` remains separate.

## Design Contract

The CLI is an edge adapter. It must parse command arguments, read hook JSON from stdin, call `CloudCaptureService`, and render output. The service owns the product verb. The HTTP integration owns provider transport. The hosted API accepts source material by reference: artifact bytes are stored once, and turn metadata stores the `artifactRef`.

Cosmic Python anchors:

- `chapter_04_service_layer.md`: the service layer is the main entrypoint for use cases.
- `chapter_10_commands.md`: hook upload is a command because failures need a local diagnostic event.
- `chapter_06_uow.md`: hosted capture upload must persist artifact/source/turn state atomically inside the API boundary.

## Verification Plan

Use a temporary `HOME`:

1. Run published PyPI CLI `setup` and complete browser login in Chrome if needed.
2. Run `codealmanac capture enable --target codex --check-cloud-equivalent via status`.
3. Confirm `~/.codealmanac/capture.json` is mode `0600`.
4. Confirm temp `~/.codex/hooks.json` contains `codealmanac __capture-hook --provider codex`.
5. Create a synthetic JSONL transcript with a Codex session id, cwd, and timestamp.
6. Pipe synthetic hook payload into `codealmanac __capture-hook --provider codex`.
7. Expect local hook output and `~/.codealmanac/capture-events/events.jsonl` to show `upload_status=uploaded`.
8. Expect production `/v1/capture/turns` response to be accepted. It may be routed or accepted-unroutable depending on current GitHub installation/repository permissions.
9. Run `codealmanac capture disable --target codex` to revoke the production capture credential and remove temp hooks.

## Risk Checks

- If hook upload fails but setup works, inspect the exact server response before changing code.
- If route response is accepted but unroutable, record whether the repo is unavailable or the GitHub installation mirror lacks the repository.
- Do not add a second capture auth mechanism. Capture credentials remain `cap_...` until WorkOS provides a cleaner machine-auth primitive that replaces them.

## Results

- Fresh PyPI setup was re-run from `HOME=/tmp/codealmanac-chrome-again.HMdNYn` with `uvx --refresh --from codealmanac codealmanac setup --api-url https://api.codealmanac.com --no-browser --skip-instructions`.
- Chrome opened the printed `https://www.codealmanac.com/cli-login?...` URL and showed `CLI login approved` for code `2XFTF7KK`.
- The CLI finished signed in as `rohans0509`; `whoami` from the same fresh HOME returned cloud `https://api.codealmanac.com`.
- Capture status started with no local credential and no cloud credentials.
- `codealmanac capture enable --target codex --api-url https://api.codealmanac.com --json` created production credential `ba28b4ec-611e-4549-b6d1-6d0f21fef810`, wrote temp `~/.codealmanac/capture.json` with mode `0600`, and installed the temp Codex Stop hook.
- A synthetic Codex transcript uploaded through `codealmanac __capture-hook --provider codex`.
- The hook returned `upload_status: uploaded`, `repo_full_name: AlmanacCode/codealmanac`, `branch: dev`, and `routing_status: routable`.
- The source artifact was read back from production through `GET /api/internal/source-artifacts` using the Render production Doppler target `codealmanac/prd`; it returned `HTTP/2 200`, `122` bytes, and SHA-256 `dd2fe50510ad2cc3a664d840f9e5431e265c6e3d47f6a19ff4f98f3e5b7de32e`.
- `codealmanac capture disable --target codex --api-url https://api.codealmanac.com --json` revoked the production credential, removed temp capture config, and left temp `~/.codex/hooks.json` as `{}`.
- Final `capture status --check-cloud --json` returned `credential_present: false`, no hooks, and no cloud credentials.
- CodeAlmanac focused tests passed: `uv run pytest tests/test_capture_transcript_upload.py tests/test_cloud_capture_service.py tests/test_cli.py -k capture` (`7 passed`).
- Hosted focused tests passed: `uv run pytest tests/test_capture_upload_api_contract.py tests/test_capture_tokens_api_contract.py tests/test_internal_route_contract.py` (`14 passed`, `1` Starlette warning).
