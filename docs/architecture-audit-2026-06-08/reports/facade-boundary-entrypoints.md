# Facade Boundary Entrypoints Follow-Up

Date: 2026-06-08

## Goal

Critically audit whether CodeAlmanac should adopt TypeScript dot-notation facades or hierarchical namespace entrypoints after the deep refactor.

Core questions:

- Would facades make the architecture easier to read, or just add another import style?
- Would a top-level `almanac` facade preserve the lazy-import and sqlite-free boundaries that were just cleaned up?
- Which modules are stable enough to deserve a public boundary entrypoint?
- Which existing `index.ts` files are useful facades, and which ones are compatibility barrels that should shrink?

Non-goals:

- Do not modify production code in this follow-up.
- Do not create a framework, command bus, service locator, or Python-style dynamic module object.
- Do not recommend a top-level namespace unless it improves dependency direction.

## Verdict

Use TypeScript facade entrypoints at stable subsystem boundaries. Do not create a single internal `src/almanac/index.ts` root facade that exports everything.

The root facade is tempting because it gives readable calls such as `almanac.capture.startRun()`, but it risks hiding dependency direction and reintroducing eager imports. Static ESM barrels are real module dependencies. If a root `almanac` module exports `wiki`, `health`, `query`, `process`, `capture`, and `operations`, importing it from a CLI registration file can pull SQLite-heavy modules back into startup. That would undermine the lazy command-registration and sqlite-free recovery cleanup.

The better shape is boundary-local dot notation:

```ts
import * as capture from "../../capture/index.js";
import * as ingest from "../../ingest/index.js";
import * as providers from "../../operations/providers.js";

await capture.startRun(request);
await ingest.startRun(request);
const provider = await providers.resolveSelection(request);
```

This gives the readability benefit without creating a global "everything bagel" facade.

## Current Evidence

The repo already has useful facades:

- `src/config/index.ts` is a clean public config surface over schema, codec, paths, providers, origins, and store.
- `src/harness/index.ts` exposes runtime harness types and provider lookup.
- `src/harness/providers/index.ts` is a real static registry over Claude, Codex, and Cursor runtime providers.
- `src/process/index.ts` is a broad process facade over run ids, records, logs, queue, manager, specs, snapshots, and types.
- `src/capture/discovery/index.ts` is a small facade over Claude/Codex transcript discovery.
- `src/cli/commands/topics/index.ts` is a command-family facade for topic verbs.

The smell is not "no facades." The smell is that some boundaries have entrypoints and others still require callers to know concrete files:

- `src/cli/commands/operations.ts` imports from `capture/start`, `ingest/start`, `operations/build`, `operations/garden`, `operations/errors`, `operations/provider-selection`, and `ingest/github`.
- `src/cli/commands/capture-sweep.ts` imports from `capture/discovery/index`, `capture/sweep`, `capture/start`, `wiki/indexer/duration`, `config/index`, and `operations/provider-selection`.
- `src/wiki/health/index.ts` now delegates source checks to `wiki/sources/health`, but `wiki/sources` has no boundary entrypoint.

Those imports are acceptable after the refactor, but they show where a few boundary entrypoints would improve the call surface.

## Recommended Shape

Add small boundary entrypoints where the subsystem has a stable product noun. Keep names concrete.

```text
src/capture/index.ts
  export { startCaptureRun as startRun } from "./start.js";
  export { executeCaptureSweep as sweep } from "./sweep.js";
  export { discoverCandidates } from "./discovery/index.js";
  export type { SessionCandidate, SweepApp } from "./discovery/index.js";

src/ingest/index.ts
  export { startIngestRun as startRun } from "./start.js";
  export { resolveIngestInput } from "./input.js";
  export { parseSourceRef } from "./source-ref.js";
  export type { Source, SourceRef, ResolvedIngestInput } from "./*.js";

src/operations/index.ts
  export { runBuildOperation as build } from "./build.js";
  export { runAbsorbOperation as absorb } from "./absorb.js";
  export { runGardenOperation as garden } from "./garden.js";
  export { resolveOperationProviderSelection as resolveProvider } from "./provider-selection.js";
  export { MissingWikiError } from "./errors.js";
  export type { OperationProviderSelection, OperationRunResult } from "./types.js";

src/wiki/query/index.ts
  export * as pages from "./pages.js";
  export * as topics from "./topics.js";
  export * as search from "./search.js";
  export { getPageView } from "./page-view.js";

src/wiki/sources/index.ts
  export { collectSourceHealthFindings } from "./health.js";
  export { migrateLegacySources, applySourceFrontmatterFix } from "./maintenance.js";
```

This gives call sites a stable shape:

```ts
import * as capture from "../../capture/index.js";
import * as operations from "../../operations/index.js";

const provider = await operations.resolveProvider({ cwd, using });
const started = await capture.startRun({ cwd, provider });
```

Avoid this as the internal default:

```ts
import * as almanac from "../../almanac/index.js";

await almanac.capture.startRun(...);
```

The root `almanac` facade can exist later only if CodeAlmanac intentionally exposes a programmatic SDK. If that happens, it should be a carefully curated external API, not a shortcut used by internal modules.

## Rules For Entry Points

1. An `index.ts` should describe a stable subsystem boundary, not hide arbitrary file layout.
2. A facade should export names that match the caller's vocabulary. Prefer `capture.startRun()` over `startCaptureRun()` when imported through `capture`.
3. A facade should not import a heavier layer than the subsystem naturally owns.
4. CLI registration modules should not import facades that transitively load SQLite-heavy command implementations.
5. Keep direct imports when a file is using an internal helper that is not part of the subsystem's boundary.
6. Avoid a root facade unless there is an external SDK surface to protect.

## What Gets Simpler

Command adapters become easier to scan because they depend on product nouns:

```ts
import * as capture from "../../capture/index.js";
import * as ingest from "../../ingest/index.js";
import * as operations from "../../operations/index.js";

const provider = await operations.resolveProvider(options);
const result = await capture.startRun({ ...options, provider });
```

The code stops teaching callers that `provider-selection.ts`, `start.ts`, and `github.ts` are the right conceptual units. Those remain implementation files under the boundary.

Tests can also import subsystem APIs instead of concrete helper files when they are testing public subsystem behavior.

## What Gets Worse If Overdone

A global facade can erase dependency direction. Once every file imports `almanac`, a CLI adapter, viewer route, provider adapter, and source maintenance module can all appear to depend on the same thing even when their real layers differ.

Static barrels can also create runtime import cost. In ESM, `export * as wiki from "./wiki/index.js"` is not a comment. It creates module links. A root facade that points at `wiki/health`, `wiki/query`, or command modules can pull `better-sqlite3` into paths that should stay SQLite-free until an action handler runs.

Over-broad `index.ts` files also make grep/navigation weaker. If a private helper is re-exported through a facade, future agents may treat it as public architecture.

## Roadmap Slice

This should be a small follow-up slice after the current refactor, not a second major rewrite.

1. Add `src/capture/index.ts`, `src/ingest/index.ts`, `src/operations/index.ts`, `src/wiki/query/index.ts`, and `src/wiki/sources/index.ts`.
2. Rename exports only at the facade boundary where it improves dot notation, such as `startCaptureRun as startRun`.
3. Update a small number of call sites that benefit directly: `src/cli/commands/operations.ts`, `src/cli/commands/capture-sweep.ts`, selected viewer/query files, and selected tests.
4. Do not update every import mechanically.
5. Run `npm run lint`, `npm test`, and `npm run build`.

Success condition: imports read more like product boundaries, no sqlite-free/lazy-registration regression appears, and no top-level root facade becomes a dumping ground.
