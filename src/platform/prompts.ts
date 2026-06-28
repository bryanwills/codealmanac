import { existsSync } from "node:fs";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

import {
  OPERATION_PROMPT_NAMES,
  type OperationPromptName,
} from "../shared/operation-prompts.js";

let overrideDir: string | null = null;
let resolvedDir: string | null = null;

export function setPromptsDirForTesting(dir: string | null): void {
  overrideDir = dir;
}

export function resolvePromptsDir(): string {
  if (overrideDir !== null) return overrideDir;
  if (resolvedDir !== null) return resolvedDir;

  const here = path.dirname(fileURLToPath(import.meta.url));
  const candidates = [
    path.resolve(here, "..", "prompts"),
    path.resolve(here, "..", "..", "prompts"),
    path.resolve(here, "..", "..", "..", "prompts"),
  ];

  for (const dir of candidates) {
    if (isPromptsDir(dir)) {
      resolvedDir = dir;
      return dir;
    }
  }

  throw new Error(
    "could not locate bundled prompts/ directory. Tried:\n" +
      candidates.map((candidate) => `  - ${candidate}`).join("\n"),
  );
}

export async function loadBundledPrompt(
  name: OperationPromptName | string,
): Promise<string> {
  const dir = resolvePromptsDir();
  return readFile(resolvePromptPath(dir, name), "utf8");
}

function isPromptsDir(dir: string): boolean {
  if (!existsSync(dir)) return false;
  return OPERATION_PROMPT_NAMES.every((name) =>
    existsSync(path.join(dir, `${name}.md`)),
  );
}

function resolvePromptPath(dir: string, name: string): string {
  if (
    name.length === 0 ||
    path.isAbsolute(name) ||
    name.includes("\\") ||
    name.split("/").some((part) => part === "" || part === "." || part === "..")
  ) {
    throw new Error(`invalid prompt name: ${name}`);
  }
  const file = path.resolve(dir, `${name}.md`);
  const relative = path.relative(dir, file);
  if (relative.startsWith("..") || path.isAbsolute(relative)) {
    throw new Error(`invalid prompt name: ${name}`);
  }
  return file;
}
