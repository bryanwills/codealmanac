# Public Release Readiness

Date: 2026-06-29

## Current Read

CodeAlmanac is usable as an internal local alpha. It is not public-release
ready until the gates below pass from a clean install and at least one real
repo dogfood run.

The main remaining work is release proof, prompt quality, and real-world
dogfood. More generic architecture seams are diminishing returns unless a gate
below exposes a boundary problem.

## Public Beta Gate

| Area | Required Evidence |
|---|---|
| Fresh install | Build a wheel, install it into a clean environment, run `codealmanac --help`, `init`, `search`, `show`, `health`, `serve`, and `jobs` without relying on editable checkout state. |
| Package metadata | Wheel metadata includes README and Apache-2.0 license text; package data includes server assets, manual files, and prompts. |
| Public docs | `README.md` describes only the Python `codealmanac` local surface: no Node/npm install path, no `almanac` alias, no hosted dashboard happy path. |
| Local wiki read path | A new repo can initialize, search, show a page, inspect topics, run health, and serve the local viewer. |
| Lifecycle write path | Real Codex or Claude ingest writes useful wiki changes under the configured Almanac root and leaves readable `jobs logs`. |
| Sync path | A synthetic and a real local transcript can be discovered, claimed, ingested, and skipped on a second run. |
| Safety | Lifecycle runs reject non-wiki mutations, preserve dirty app files, and record harness events before terminal errors. |
| Viewer | Browser dogfood checks desktop and mobile routes for overview, page, topic, search, file refs, and no horizontal overflow. |
| Contract guards | Tests reject hosted verbs, compatibility aliases, public SDK/MCP modules, and stale README install language. |
| Release command | `codealmanac update --check` reports a coherent package-manager plan from non-editable pip and uv-tool installs. |

## Stop Doing

- Do not add hosted verbs, login/connect/upload, SDK, MCP, or aliases.
- Do not add a frontend build step until the static viewer becomes the harder
  path.
- Do not port Codex app-server for parity. Port it only when normalized harness
  event completeness is required.
- Do not add a source pool or candidate object without a concrete product
  workflow that needs it.

## Next Useful Pressure Tests

1. Clean install dogfood from a built wheel.
2. Real Codex ingest on this repo or another messy repo.
3. Real Claude ingest on a small repo.
4. Browser-harness pass over `serve` after any viewer copy or layout changes.
5. Wheel metadata/package-data inspection before any publish attempt.
