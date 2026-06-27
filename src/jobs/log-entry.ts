import type { HarnessEvent, RunActor } from "../harness/events.js";

export interface JobLogEntryV1 {
  timestamp: string;
  event: HarnessEvent;
}

export interface JobLogEntryV2 {
  version: 2;
  timestamp: string;
  sequence: number;
  jobId: string;
  actor: RunActor;
  event: HarnessEvent;
  raw?: unknown;
}

export type JobLogEntry = JobLogEntryV1 | JobLogEntryV2;

export interface AppendJobEventOptions {
  jobId?: string;
  sequence?: number;
}

export function buildJobLogEntry(
  event: HarnessEvent,
  now: Date,
  options: AppendJobEventOptions = {},
): JobLogEntry {
  const timestamp = now.toISOString();
  return options.jobId !== undefined && options.sequence !== undefined
    ? {
        version: 2,
        timestamp,
        sequence: options.sequence,
        jobId: options.jobId,
        actor: event.actor ?? inferActor(event),
        event: stripEnvelopeFields(event),
        ...(event.raw !== undefined ? { raw: event.raw } : {}),
      }
    : {
        timestamp,
        event,
      };
}

export function inferActor(event: HarnessEvent): RunActor {
  if (event.type === "done" && event.sourceRole !== undefined) {
    return {
      threadId: event.sourceThreadId ?? null,
      role: event.sourceRole,
      confidence: event.sourceRole === "unknown" ? "unknown" : "provider",
      label: actorLabel(event.sourceRole),
    };
  }

  return {
    threadId: null,
    role: "unknown",
    confidence: "unknown",
    label: "Unknown actor",
  };
}

function stripEnvelopeFields(event: HarnessEvent): HarnessEvent {
  const { actor: _actor, raw: _raw, ...rest } = event;
  return rest as HarnessEvent;
}

function actorLabel(role: RunActor["role"]): string {
  if (role === "root") return "Main";
  if (role === "helper") return "Helper";
  return "Unknown actor";
}
