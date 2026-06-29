import { existsSync } from "node:fs";
import { copyFile, mkdir, readFile, rm, writeFile } from "node:fs/promises";
import path from "node:path";

export const CLAUDE_IMPORT_LINE = "@~/.claude/almanac.md";
export const LEGACY_CLAUDE_IMPORT_LINE = "@~/.claude/codealmanac.md";

export async function ensureClaudeInstructions(args: {
  claudeDir: string;
  miniGuidePath: string;
  referenceGuidePath: string;
}): Promise<string[]> {
  await mkdir(args.claudeDir, { recursive: true });
  const touched: string[] = [];

  if (await copyIfChanged(args.miniGuidePath, path.join(args.claudeDir, "almanac.md"))) {
    touched.push("almanac.md");
  }
  if (
    await copyIfChanged(
      args.referenceGuidePath,
      path.join(args.claudeDir, "almanac-reference.md"),
    )
  ) {
    touched.push("almanac-reference.md");
  }
  if (await ensureClaudeImport(path.join(args.claudeDir, "CLAUDE.md"))) {
    touched.push("CLAUDE.md");
  }

  return touched;
}

export async function removeClaudeInstructions(claudeDir: string): Promise<string[]> {
  const touched: string[] = [];
  const guideFiles = [
    "almanac.md",
    "almanac-reference.md",
    "codealmanac.md",
    "codealmanac-reference.md",
  ];
  const claudeMd = path.join(claudeDir, "CLAUDE.md");

  for (const file of guideFiles) {
    const fullPath = path.join(claudeDir, file);
    if (existsSync(fullPath)) {
      await rm(fullPath, { force: true });
      touched.push(file);
    }
  }

  if (existsSync(claudeMd)) {
    const existing = await readFile(claudeMd, "utf8");
    const { changed, body } = removeClaudeImportLine(existing);
    if (changed) {
      if (body.trim().length === 0) {
        await rm(claudeMd, { force: true });
        touched.push("CLAUDE.md (deleted)");
      } else {
        await writeFile(claudeMd, body, "utf8");
        touched.push("CLAUDE.md");
      }
    }
  }

  return touched;
}

export async function claudeInstructionsPresent(claudeDir: string): Promise<string[]> {
  const missing: string[] = [];
  const mini = path.join(claudeDir, "almanac.md");
  const ref = path.join(claudeDir, "almanac-reference.md");
  const claudeMd = path.join(claudeDir, "CLAUDE.md");

  if (!existsSync(mini)) missing.push("Claude almanac.md");
  if (!existsSync(ref)) missing.push("Claude almanac-reference.md");
  if (!existsSync(claudeMd)) {
    missing.push("Claude CLAUDE.md import");
  } else {
    try {
      if (!hasClaudeImportLine(await readFile(claudeMd, "utf8"))) {
        missing.push("Claude CLAUDE.md import");
      }
    } catch {
      missing.push("Claude CLAUDE.md import");
    }
  }

  return missing;
}

async function copyIfChanged(src: string, dest: string): Promise<boolean> {
  const srcBytes = await readFile(src);
  if (existsSync(dest)) {
    try {
      const destBytes = await readFile(dest);
      if (srcBytes.equals(destBytes)) return false;
    } catch {
      // Fall through to write.
    }
  }
  await mkdir(path.dirname(dest), { recursive: true });
  await copyFile(src, dest);
  return true;
}

async function ensureClaudeImport(claudeMdPath: string): Promise<boolean> {
  let existing = "";
  if (existsSync(claudeMdPath)) {
    existing = await readFile(claudeMdPath, "utf8");
  }
  if (hasClaudeImportLine(existing)) return false;

  const sep =
    existing.length === 0 ? "" : existing.endsWith("\n") ? "\n" : "\n\n";
  await writeFile(claudeMdPath, `${existing}${sep}${CLAUDE_IMPORT_LINE}\n`, "utf8");
  return true;
}

export function hasClaudeImportLine(contents: string): boolean {
  const lines = contents.split(/\r?\n/).map((line) => line.trim());
  return lines.some((line) => isImportLineFor(line, CLAUDE_IMPORT_LINE));
}

export function removeClaudeImportLine(contents: string): {
  changed: boolean;
  body: string;
} {
  const eol = contents.includes("\r\n") ? "\r\n" : "\n";
  const lines = contents.split(/\r?\n/);
  const indices: number[] = [];
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]!.trim();
    if (
      isImportLineFor(line, CLAUDE_IMPORT_LINE) ||
      isImportLineFor(line, LEGACY_CLAUDE_IMPORT_LINE)
    ) {
      indices.push(i);
    }
  }
  if (indices.length === 0) return { changed: false, body: contents };

  for (let i = indices.length - 1; i >= 0; i--) {
    lines.splice(indices[i]!, 1);
  }

  return {
    changed: true,
    body: lines.join(eol).replace(/\n\n\n+/g, "\n\n"),
  };
}

function isImportLineFor(line: string, importLine: string): boolean {
  if (line === importLine) return true;
  const rest = line.slice(importLine.length);
  return line.startsWith(importLine) && /^[\t ]/.test(rest);
}
