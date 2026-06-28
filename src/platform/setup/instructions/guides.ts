import { existsSync } from "node:fs";
import { readFile } from "node:fs/promises";
import path from "node:path";

export interface SetupInstructionGuides {
  miniGuidePath: string;
  referenceGuidePath: string;
  miniContents: string;
}

export async function readSetupInstructionGuides(
  guidesDir: string,
): Promise<SetupInstructionGuides> {
  const miniGuidePath = requireBundledGuide(guidesDir, "mini.md");
  const referenceGuidePath = requireBundledGuide(guidesDir, "reference.md");

  return {
    miniGuidePath,
    referenceGuidePath,
    miniContents: await readFile(miniGuidePath, "utf8"),
  };
}

function requireBundledGuide(guidesDir: string, name: string): string {
  const guidePath = path.join(guidesDir, name);
  if (!existsSync(guidePath)) {
    throw new Error(`missing bundled guide: ${guidePath}`);
  }
  return guidePath;
}
