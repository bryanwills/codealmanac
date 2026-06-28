import { resolve } from "node:path";

import {
  resolveGitHubSource,
} from "../../../platform/github/source.js";
import type { AbsorbInputSource } from "./input-source.js";
import { parseSourceRef, type SourceRef } from "./source-ref.js";

export type AbsorbInputKind = "path" | "source" | "mixed";

export interface ResolvedAbsorbInput {
  kind: AbsorbInputKind;
  targets: string[];
  paths: string[];
  sources: AbsorbInputSource[];
  networkAccess: boolean;
}

export type ResolveSourceFn = (
  ref: SourceRef,
  cwd: string,
) => Promise<AbsorbInputSource>;

export interface ResolveAbsorbInputOptions {
  cwd: string;
  inputs: string[];
  resolveSource?: ResolveSourceFn;
}

type ParsedAbsorbInput =
  | { kind: "path"; path: string }
  | { kind: "source"; ref: SourceRef };

export async function resolveAbsorbInput(
  options: ResolveAbsorbInputOptions,
): Promise<
  | { ok: true; value: ResolvedAbsorbInput }
  | { ok: false; message: string }
> {
  const parsedInputs: ParsedAbsorbInput[] = [];
  let hasSourceRef = false;
  for (const input of options.inputs) {
    const parsed = parseSourceRef(input);
    if (parsed.ok) {
      parsedInputs.push({ kind: "source", ref: parsed.value });
      hasSourceRef = true;
      continue;
    }
    if (parsed.reason === "not-source-ref") {
      parsedInputs.push({ kind: "path", path: input });
      continue;
    }
    return { ok: false, message: parsed.message };
  }

  const targets: string[] = [];
  const resolvedPaths: string[] = [];
  const sources: AbsorbInputSource[] = [];
  const resolveSource = hasSourceRef
    ? options.resolveSource ?? defaultResolveSource
    : null;
  for (const input of parsedInputs) {
    if (input.kind === "path") {
      const path = resolve(options.cwd, input.path);
      resolvedPaths.push(path);
      targets.push(path);
    } else if (resolveSource !== null) {
      const source = await resolveSource(input.ref, options.cwd);
      sources.push(source);
      targets.push(source.raw);
    }
  }

  const kind: AbsorbInputKind = resolvedPaths.length > 0 && sources.length > 0
    ? "mixed"
    : sources.length > 0
    ? "source"
    : "path";
  return {
    ok: true,
    value: {
      kind,
      targets,
      paths: resolvedPaths,
      sources,
      networkAccess: sources.length > 0,
    },
  };
}

function defaultResolveSource(
  ref: SourceRef,
  cwd: string,
): Promise<AbsorbInputSource> {
  if (ref.provider === "github") {
    return resolveGitHubSource({ ref, cwd });
  }
  if (ref.provider === "web") {
    return Promise.resolve({
      kind: "web.url",
      raw: ref.raw,
      url: ref.url,
    });
  }
  const _exhaustive: never = ref;
  throw new Error(`unsupported source provider ${String(_exhaustive)}`);
}
