import { viewerApi } from "./api.js";
import { emptyState, pageIntro } from "./components.js";
import { jobHref } from "./routes.js";

const ACTIVE_JOB_STATUSES = new Set(["queued", "running"]);
const JOB_POLL_INTERVAL_MS = 1500;

let jobPollTimer = null;

export function clearJobPolling() {
  if (jobPollTimer === null) return;
  window.clearTimeout(jobPollTimer);
  jobPollTimer = null;
}

export async function renderJobs(context) {
  const { elements, setRouteTitle, wiki } = context;
  const routeHash = window.location.hash;
  const result = await viewerApi.jobs(wiki);
  if (window.location.hash !== routeHash) return;
  setRouteTitle("Jobs");
  replaceMain(
    elements,
    pageIntro("CodeAlmanac runs", "Jobs", `${result.runs.length} local runs.`),
    jobList(result.runs),
  );
  if (result.runs.some((run) => isActiveJobStatus(run.status))) {
    scheduleJobPolling(routeHash, () => renderJobs(context));
  }
}

export async function renderJob(context, runId) {
  const { elements, setRouteTitle, wiki } = context;
  const routeHash = window.location.hash;
  const detail = await viewerApi.job(runId, wiki);
  if (window.location.hash !== routeHash) return;
  const run = detail.run;
  setRouteTitle(run.title || run.run_id);
  replaceMain(
    elements,
    pageIntro("Job", run.title || run.run_id, `${run.kind} · ${run.status}`),
    jobDetail(run),
    stepList(detail.steps),
  );
  if (isActiveJobStatus(run.status)) {
    scheduleJobPolling(routeHash, () => renderJob(context, runId));
  }
}

function scheduleJobPolling(routeHash, render) {
  clearJobPolling();
  jobPollTimer = window.setTimeout(() => {
    jobPollTimer = null;
    if (window.location.hash !== routeHash) return;
    render().catch((error) => {
      console.error("CodeAlmanac job refresh failed", error);
    });
  }, JOB_POLL_INTERVAL_MS);
}

function isActiveJobStatus(status) {
  return ACTIVE_JOB_STATUSES.has(status);
}

function jobList(runs) {
  if (runs.length === 0) {
    return emptyState(
      "No jobs yet",
      "CodeAlmanac runs appear here after ingest, garden, or sync.",
    );
  }
  const list = document.createElement("nav");
  list.className = "job-list";
  list.setAttribute("aria-label", "Jobs");
  for (const run of runs) {
    list.append(jobRow(run));
  }
  return list;
}

function jobRow(run) {
  const item = document.createElement("a");
  item.className = "job-row";
  item.href = jobHref(run.run_id);

  const main = document.createElement("span");
  main.className = "job-row-main";
  const title = document.createElement("span");
  title.className = "job-row-title";
  title.textContent = run.title || run.run_id;
  const summary = document.createElement("span");
  summary.className = "job-row-summary";
  summary.textContent = run.summary || run.error || run.run_id;
  main.append(title, summary);

  const meta = document.createElement("span");
  meta.className = "job-row-meta";
  meta.append(
    jobPill(run.status),
    textSpan(run.kind),
    textSpan(shortTime(run.updated_at)),
  );

  item.append(main, meta);
  return item;
}

function jobDetail(run) {
  const section = document.createElement("section");
  section.className = "job-detail";
  section.append(
    detailRow("Run", run.run_id),
    detailRow("Status", run.status),
    detailRow("Kind", run.kind),
    detailRow("Updated", shortTime(run.updated_at)),
    detailRow("Logs", "run output below"),
  );
  if (run.harness_transcript) {
    section.append(
      detailRow(
        "Transcript",
        `${run.harness_transcript.kind} ${run.harness_transcript.session_id}`,
      ),
    );
  }
  if (run.summary) section.append(detailRow("Summary", run.summary));
  if (run.error) section.append(detailRow("Error", run.error));
  return section;
}

function stepList(steps) {
  if (steps.length === 0) {
    return emptyState("No output", "This run has no readable output yet.");
  }
  const section = document.createElement("section");
  section.className = "job-steps";
  const heading = document.createElement("h2");
  heading.textContent = "Run output";
  section.append(heading);
  for (const step of steps) {
    section.append(stepRow(step));
  }
  return section;
}

function stepRow(step) {
  const row = document.createElement("article");
  row.className = `job-step job-step--${step.kind}`;
  if (step.error) row.classList.add("job-step--error");

  const header = document.createElement("header");
  header.className = "job-step-header";
  header.append(
    textSpan(`#${step.sequence}`),
    jobPill(step.kind),
    textSpan(shortTime(step.timestamp)),
  );
  if (step.status) header.append(jobPill(step.status));

  const title = document.createElement("h3");
  title.className = "job-step-title";
  title.textContent = step.title;

  row.append(header, title);
  if (step.body) {
    const body = document.createElement("p");
    body.className = "job-step-body";
    body.textContent = step.body;
    row.append(body);
  }
  const meta = stepMeta(step);
  if (meta.length > 0) {
    const list = document.createElement("dl");
    list.className = "job-step-meta";
    for (const [label, value] of meta) {
      const term = document.createElement("dt");
      term.textContent = label;
      const detail = document.createElement("dd");
      detail.textContent = valueText(value);
      list.append(term, detail);
    }
    row.append(list);
  }
  return row;
}

function stepMeta(step) {
  return [
    ["Tool", step.tool],
    ["Target", step.target],
    ["Detail", step.detail],
    ["Input", step.input],
    ["Output", step.output],
    ["Actor", step.actor],
  ].filter(([, value]) => value !== null && value !== undefined && value !== "");
}

function detailRow(label, value) {
  const row = document.createElement("div");
  row.className = "job-detail-row";
  const key = document.createElement("span");
  key.textContent = label;
  const val = document.createElement("strong");
  val.textContent = value;
  row.append(key, val);
  return row;
}

function valueText(value) {
  if (typeof value === "string") return value;
  if (typeof value === "number" || typeof value === "boolean") return String(value);
  return JSON.stringify(value);
}

function jobPill(value) {
  const pill = document.createElement("span");
  pill.className = `job-pill job-pill--${String(value).replace(/[^a-z0-9_-]/gi, "")}`;
  pill.textContent = value;
  return pill;
}

function textSpan(value) {
  const span = document.createElement("span");
  span.textContent = value;
  return span;
}

function shortTime(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return String(value);
  return new Intl.DateTimeFormat(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
    timeZoneName: "short",
  }).format(date);
}

function replaceMain(elements, ...children) {
  elements.main.replaceChildren(...children);
  elements.main.focus();
}
