export function stringifyClaudeToolResult(content: unknown): string {
  if (typeof content === "string") return content;
  return stringifyClaudeInput(content) ?? "";
}

export function promptFromClaudeAgentInput(input: unknown): string {
  if (input !== null && typeof input === "object") {
    const prompt = (input as { prompt?: unknown }).prompt;
    if (typeof prompt === "string") return prompt;
    const description = (input as { description?: unknown }).description;
    if (typeof description === "string") return description;
  }
  return "";
}

export function textDeltaFromClaudeStreamEvent(event: unknown): string | undefined {
  if (event === null || typeof event !== "object") return undefined;
  const raw = event as {
    type?: unknown;
    delta?: { type?: unknown; text?: unknown };
  };
  return raw.type === "content_block_delta" &&
    raw.delta?.type === "text_delta" &&
    typeof raw.delta.text === "string"
    ? raw.delta.text
    : undefined;
}

export function stringifyClaudeInput(input: unknown): string | undefined {
  if (input === undefined) return undefined;
  if (typeof input === "string") return input;
  try {
    return JSON.stringify(input);
  } catch {
    return String(input);
  }
}
