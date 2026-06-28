import type { JobView } from "../../../stores/jobs/types.js";
import type { JobLogEvent, JobRunProjection } from "./types.js";
import {
  firstMeaningfulLine,
  truncate,
} from "./text.js";

export function enrichJobView(
  view: JobView,
  events: JobLogEvent[],
  specPrompt: string | null,
): JobRunProjection {
  return {
    ...view,
    displayTitle: jobDisplayTitle(view),
    displaySubtitle: jobDisplaySubtitle(view, events),
    transcriptSource: transcriptSource(view, specPrompt),
  };
}

function jobDisplayTitle(view: JobView): string {
  const operation = operationTitle(view.operation);
  if (view.targetKind === "session") return `${operation} session transcript`;
  if (view.targetKind === "wiki") return `${operation} wiki`;
  if (view.targetKind !== undefined) return `${operation} ${view.targetKind}`;
  return `${operation} job`;
}

function jobDisplaySubtitle(view: JobView, events: JobLogEvent[]): string | null {
  const finalText = finalResultText(events);
  if (finalText !== null) return finalText;
  const target = view.targetPaths?.[0];
  if (target !== undefined) return targetLabel(target);
  return view.model ?? null;
}

function finalResultText(events: JobLogEvent[]): string | null {
  for (let i = events.length - 1; i >= 0; i--) {
    const entry = events[i];
    if (entry === undefined) continue;
    if ("invalid" in entry) continue;
    const event = entry.event;
    if (event.type !== "done" && event.type !== "text") continue;
    const text = event.type === "done" ? event.result : event.content;
    const line = firstMeaningfulLine(text);
    if (line !== null) return truncate(line, 120);
  }
  return null;
}

function operationTitle(operation: string): string {
  if (operation === "absorb") return "Absorb";
  if (operation === "build") return "Build";
  if (operation === "garden") return "Garden";
  return operation.charAt(0).toUpperCase() + operation.slice(1);
}

function transcriptSource(
  view: JobView,
  specPrompt: string | null,
): JobRunProjection["transcriptSource"] {
  if (view.targetKind !== "session") return null;
  const fromPrompt = specPrompt?.match(/^- App: (claude|codex)\s*$/m)?.[1];
  if (fromPrompt === "claude" || fromPrompt === "codex") return fromPrompt;
  const target = view.targetPaths?.[0] ?? "";
  if (target.includes("/.codex/") || basename(target).startsWith("rollout-")) {
    return "codex";
  }
  if (target.includes("/.claude/")) return "claude";
  return "file";
}

function basename(path: string): string {
  return path.split(/[\\/]/).filter(Boolean).at(-1) ?? path;
}

function targetLabel(path: string): string {
  return path.startsWith("/") ? basename(path) : path;
}
