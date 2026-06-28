export type OperationPromptName =
  | "base/purpose"
  | "base/notability"
  | "base/syntax"
  | "operations/build"
  | "operations/absorb"
  | "operations/garden";

export const OPERATION_PROMPT_NAMES: readonly OperationPromptName[] = [
  "base/purpose",
  "base/notability",
  "base/syntax",
  "operations/build",
  "operations/absorb",
  "operations/garden",
];

export type OperationPromptLoader = (
  name: OperationPromptName | string,
) => Promise<string>;

export function joinPromptSections(
  parts: Array<string | null | undefined>,
): string {
  return parts
    .map((part) => part?.trim())
    .filter((part): part is string => part !== undefined && part.length > 0)
    .join("\n\n---\n\n");
}
