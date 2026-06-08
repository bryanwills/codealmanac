# Architecture cleanup implementation log

## Goal

Remove code paths that exist only to preserve stale integration or compatibility decisions, while leaving the `.almanac` wiki and architecture audit docs untouched. The cleanup branch should simplify the live public surface before any separate Codex SDK experiment.

## User decisions

- Remove Composio completely.
- Do not design replacement integrations in this branch; future Slack or GitHub integrations can start from a smaller source-context seam.
- Keep scheduled Garden installed by setup by default.
- Replace legacy-source auto-fix behavior with explicit migration and warnings.
- Keep Cursor for now.
- Treat the Codex SDK as a later spike on a separate branch.

## Baseline

- `npm run lint` passed before cleanup.
- `npm test` initially had one setup failure: `test/setup.test.ts > codealmanac setup > installs automation + guides + CLAUDE.md import when --yes`. The launchd plist executable was the Vitest worker entrypoint because automation resolved `process.argv[1]` when no built `dist/codealmanac.js` existed.
- `npm install` and `npm uninstall @composio/core` warn because the local Node version is `v21.7.3`, outside the repo engine range.

## Slice 1: Composio removal

Composio was not a narrow provider adapter. It leaked into config normalization, config serialization, public CLI commands, viewer API shape, prompt/runtime connector requirements, tests, and package dependencies. Keeping aliases or empty connector status objects would preserve the stale abstraction.

Implemented changes so far:

- Removed connector config types and keys from `src/config/`.
- Removed `connect github` and `source github` command registration.
- Removed the viewer `/connections` API.
- Deleted Composio connector runtime files and connector-specific tests.
- Removed `@composio/core` from the package manifest and lockfile.

Remaining cleanup in this slice:

- None.

Verification:

- `npm run lint` passed.
- `npm test -- --run test/config-command.test.ts test/cli.test.ts test/viewer-api.test.ts test/ingest-input.test.ts test/operation-commands.test.ts test/codex-harness-provider.test.ts` passed with 6 files and 93 tests.

## Slice 2: CLI cleanup

The next stale public surfaces are deprecated aliases and implicit repair commands. The intended end state is a smaller command graph with explicit migration commands and warnings where stale data still exists.

Planned changes:

- Remove deprecated `almanac set` aliases for `agents use` and `agents model`.
- Replace `health --fix` with `almanac migrate legacy-sources`.
- Make `health` warn when legacy sources are present and point to the migration command.

Implemented changes:

- Removed `almanac set`, `almanac ps`, `almanac capture status`, and CLI `show --raw`.
- Added `almanac migrate legacy-sources` for deterministic legacy source frontmatter rewrites.
- Changed `almanac health` to report-only behavior with a stderr warning when legacy source frontmatter is present.
- Removed stale `capture --account`.
- Updated active prompts and reference docs that previously pointed to `almanac health --fix`.

Verification:

- `npm run lint` passed.
- `npm test -- --run test/health.test.ts test/cli.test.ts test/show.test.ts test/config-command.test.ts test/viewer-api.test.ts test/ingest-input.test.ts test/operation-commands.test.ts test/codex-harness-provider.test.ts` passed with 8 files and 140 tests.

## Slice 3: setup automation entrypoint

The baseline setup failure exposed a real boundary issue: launchd automation inferred its CLI entrypoint from `process.argv[1]` when the package root did not contain the old `dist/codealmanac.js` entry. In a test worker that path is Vitest's Tinypool process entrypoint, and in current package metadata the durable CLI entry is `dist/launcher.js`.

Implemented changes:

- Resolve the package root by walking up to `package.json` and use `dist/launcher.js`, matching the `bin` entries in `package.json`.
- Updated setup tests and active docs/comments from `dist/codealmanac.js` to `dist/launcher.js`.

Verification:

- `npm test -- --run test/setup.test.ts test/automation.test.ts` passed with 2 files and 28 tests.
- `npm run lint` passed.
- `npm test` passed with 61 files and 558 tests.
- `npm run build` passed and produced `dist/launcher.js`.
