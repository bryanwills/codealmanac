import type { JobView } from "../../../stores/jobs/types.js";
import type { JobLogEvent, JobWarning } from "./types.js";

export function deriveJobWarnings(
  operation: string,
  run: JobView,
  events: JobLogEvent[],
): JobWarning[] {
  const warnings: JobWarning[] = [];
  const unknownEntry = events.find((entry) =>
    "invalid" in entry
      ? false
      : (entry.actor ?? entry.event.actor)?.role === "unknown",
  );
  if (unknownEntry !== undefined && !("invalid" in unknownEntry)) {
    warnings.push({
      code: "unknown_actor_events",
      severity: "warning",
      message: "Some events could not be attributed to the main agent or a helper.",
      eventSequence: unknownEntry.sequence ?? unknownEntry.line,
      threadId: (unknownEntry.actor ?? unknownEntry.event.actor)?.threadId ??
        undefined,
    });
  }

  let doneEntry: JobLogEvent | undefined;
  for (let i = events.length - 1; i >= 0; i--) {
    const entry = events[i];
    if (
      entry !== undefined &&
      !("invalid" in entry) &&
      entry.event.type === "done"
    ) {
      doneEntry = entry;
      break;
    }
  }
  if (doneEntry !== undefined && !("invalid" in doneEntry)) {
    const done = doneEntry.event;
    if (done.type === "done") {
      if (done.sourceRole === undefined) {
        warnings.push({
          code: "unattributed_done",
          severity: "warning",
          message: "The terminal result does not record which agent produced it.",
          eventSequence: doneEntry.sequence ?? doneEntry.line,
        });
      } else if (done.sourceRole !== "root") {
        warnings.push({
          code: done.sourceRole === "helper"
            ? "helper_result_used_as_done"
            : "done_source_not_root",
          severity: "error",
          message: `The terminal result came from ${done.sourceRole}, not the main agent.`,
          eventSequence: doneEntry.sequence ?? doneEntry.line,
          threadId: done.sourceThreadId,
        });
      }
    }
  }

  if (
    operation === "build" &&
    run.displayStatus === "done" &&
    (run.summary?.created ?? 0) === 0 &&
    (run.summary?.updated ?? 0) === 0
  ) {
    warnings.push({
      code: "zero_page_build",
      severity: "warning",
      message: "Build finished successfully but did not create or update any pages.",
    });
  }

  const mcpEntry = events.find((entry) =>
    "invalid" in entry
      ? false
      : entry.event.type === "tool_use" && entry.event.display?.kind === "mcp",
  );
  if (mcpEntry !== undefined && !("invalid" in mcpEntry)) {
    warnings.push({
      code: "mcp_used_in_build",
      severity: operation === "build" ? "warning" : "info",
      message: "The job used an MCP tool; check whether that was intended for this operation.",
      eventSequence: mcpEntry.sequence ?? mcpEntry.line,
    });
  }

  return warnings;
}
