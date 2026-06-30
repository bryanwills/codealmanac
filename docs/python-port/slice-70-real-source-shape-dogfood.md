# Slice 70 - Real Source Shape Dogfood

Date: 2026-06-30

## Purpose

Close the last public-beta product blocker by running lifecycle ingest against a
non-toy source shape, then fix the user-state naming issue exposed during that
dogfood.

## Scope

- Run public `codealmanac ingest` through the real Claude harness.
- Use a focused temp repo containing real CodeAlmanac source-runtime,
  filesystem adapter, ingest workflow, prompt, and live-agreement files.
- Inspect the generated wiki page, health report, and job logs.
- Move default user/global state from `~/.almanac/` to `~/.codealmanac/`.
- Keep the repo wiki root as `almanac/`.

## Dogfood Shape

The dogfood repo lived at:

```text
/tmp/codealmanac-lifecycle-dogfood-slice70-real
```

It contained copied source from the current branch:

```text
src/codealmanac/services/sources/
src/codealmanac/integrations/sources/filesystem/
src/codealmanac/workflows/ingest/
src/codealmanac/prompts/base/
src/codealmanac/prompts/operations/
docs/python-port-live-agreement.md
README.md
```

The run used the public CLI:

```bash
codealmanac init . --name lifecycle-source-dogfood
codealmanac ingest \
  src/codealmanac/services/sources \
  src/codealmanac/integrations/sources/filesystem \
  src/codealmanac/workflows/ingest \
  docs/python-port-live-agreement.md \
  --using claude \
  --title "Source Runtime Ingest Dogfood" \
  --guidance "Write or update one concise wiki page about how CodeAlmanac turns selected source inputs into prompt material for lifecycle ingest..."
```

## Findings

The first attempt used a temporary `HOME` to isolate the registry. That hid
Claude's real auth files and produced `Not logged in`. This was environmental
setup, not a CodeAlmanac lifecycle failure.

The second attempt used real `HOME` for Claude auth and temporarily isolated
CodeAlmanac's registry/config files. It exposed a product issue: the Python CLI
still read `~/.almanac/config.toml`, which contained stale old-product config
with an unsupported `[agent]` section. Because the Python rewrite is not
backward-compatible, the correct fix is not to accept that old config shape.
The fix is to put CodeAlmanac's global user state under `~/.codealmanac/`.

## Result

After isolating stale old config, the real Claude run completed:

```text
ingested ingest-20260630004924-1039ba82: done
sources: 4
wiki_changes: 1
summary: Created one durable page. Summary of what I did:
```

It created `almanac/pages/source-runtime-flow.md`. The page accurately covered:

- `SourceAddress -> SourceRef -> SourceBrief -> SourceRuntime`
- `SourcesService.resolve`, `discover_transcripts`, and `inspect_runtime`
- filesystem file and directory runtime selection
- Git listing fallback behavior
- prompt payload consumption inside `IngestWorkflow`
- gotchas for unsupported sources, missing paths, ignored wiki roots, and
  bounded runtime content

`codealmanac health --json` reported no orphans, dead refs, broken links,
broken cross-wiki links, empty topics, or empty pages. `jobs logs` recorded
queued, running, preflight, source resolution, runtime loading, Claude success,
and terminal done events.

## Fix

- `src/codealmanac/core/paths.py` now makes `~/.codealmanac/` the default
  global state directory.
- `src/codealmanac/services/automation/service.py` writes scheduler logs under
  the same product-specific state directory.
- README, MANUAL, and live-agreement docs now distinguish the repo wiki root
  `almanac/` from user/global state `~/.codealmanac/`.
- Public-contract tests pin `AppConfig()` default registry and config paths.

## Validation Note

Cosmic Python's validation appendix shaped this slice's validation answer:
Pydantic/request models validate shaped product input at the edge, while
adapter-local tolerant parsers may return `None` when reading loose external
state. The LaunchD `parse_int` helper remains acceptable because it is
adapter-local tolerance, not service-boundary validation.

## Verification

- `uv run pytest tests/test_public_contract.py::test_default_user_state_paths_are_product_specific tests/test_cli.py::test_cli_init_creates_wiki_and_prints_name tests/test_config_service.py tests/test_automation_service.py::test_automation_install_plans_sync_and_garden -q`
  passed with 8 tests.
- `git diff --check` passed after the initial code/doc edits.
- Relayforge delivered the Cosmic Python validation note in three Discord
  messages via binding `rohan-almanac-main`.
