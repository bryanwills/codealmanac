import { resolve } from "node:path";

import type { AbsorbInputSource } from "./input-source.js";
import { parseSourceRef, type SourceRef, type WebSourceRef } from "./source-ref.js";

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
  for (const input of parsedInputs) {
    if (input.kind === "path") {
      const path = resolve(options.cwd, input.path);
      resolvedPaths.push(path);
      targets.push(path);
    } else if (hasSourceRef) {
      const source = await resolveSourceRef({
        ref: input.ref,
        cwd: options.cwd,
        resolveSource: options.resolveSource,
      });
      if (source.ok === false) return source;
      sources.push(source.value);
      targets.push(source.value.raw);
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

async function resolveSourceRef(args: {
  ref: SourceRef;
  cwd: string;
  resolveSource?: ResolveSourceFn;
}): Promise<
  | { ok: false; message: string }
  | { ok: true; value: AbsorbInputSource }
> {
  if (args.resolveSource !== undefined) {
    return {
      ok: true,
      value: await args.resolveSource(args.ref, args.cwd),
    };
  }
  if (args.ref.provider === "web") {
    return {
      ok: true,
      value: webInputSource(args.ref),
    };
  }
  return {
    ok: false,
    message: "GitHub source refs require a source resolver.",
  };
}

function webInputSource(ref: WebSourceRef): AbsorbInputSource {
  return {
    kind: "web.url",
    raw: ref.raw,
    url: ref.url,
  };
}
