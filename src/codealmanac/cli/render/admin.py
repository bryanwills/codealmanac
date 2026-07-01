import json
import shlex
import sys
from datetime import timedelta

from codealmanac.services.automation.models import (
    AutomationInstallResult,
    AutomationStatusReport,
    AutomationTask,
    AutomationUninstallResult,
    ScheduledJob,
    ScheduledJobStatus,
)
from codealmanac.services.diagnostics.models import DoctorCheck, DoctorReport
from codealmanac.services.runs.models import (
    RunAttachSnapshot,
    RunCancelResult,
    RunLogEvent,
    RunRecord,
)
from codealmanac.services.updates.models import UpdatePlan, UpdateResult


def render_automation_install(
    result: AutomationInstallResult,
    json_output: bool,
) -> None:
    if json_output:
        print(json.dumps(result.model_dump(mode="json"), indent=2))
        return
    print("automation installed")
    for job in result.jobs:
        print_automation_job(job)
    for job in result.disabled:
        print(f"  {job.task.value}: disabled")


def render_automation_uninstall(
    result: AutomationUninstallResult,
    json_output: bool,
) -> None:
    if json_output:
        print(json.dumps(result.model_dump(mode="json"), indent=2))
        return
    if len(result.removed) == 0:
        print("automation not installed")
        return
    print("automation removed")
    for path in result.removed:
        print(f"  plist: {path}")


def render_automation_status(
    report: AutomationStatusReport,
    json_output: bool,
) -> None:
    if json_output:
        print(json.dumps(report.model_dump(mode="json"), indent=2))
        return
    for status in report.statuses:
        render_automation_job_status(status)


def print_automation_job(job: ScheduledJob) -> None:
    print(f"  {job.task.value} interval: {duration_label(job.interval)}")
    if job.task == AutomationTask.SYNC:
        quiet = job.program_arguments[job.program_arguments.index("--quiet") + 1]
        print(f"  sync quiet: {quiet}")
    print(f"  {job.task.value} command: {' '.join(job.program_arguments)}")
    if job.working_directory is not None:
        print(f"  {job.task.value} cwd: {job.working_directory}")
    print(f"  {job.task.value} plist: {job.plist_path}")


def render_automation_job_status(status: ScheduledJobStatus) -> None:
    label = f"{status.task.value} automation"
    if not status.installed:
        print(f"{label}: not installed")
        return
    print(f"{label}: installed")
    print(f"  plist: {status.plist_path}")
    print(f"  launchd loaded: {'yes' if status.loaded else 'no'}")
    if status.interval is not None:
        print(f"  interval: {duration_label(status.interval)}")
    if status.quiet is not None:
        print(f"  quiet: {duration_label(status.quiet)}")


def duration_label(value: timedelta) -> str:
    seconds = int(value.total_seconds())
    return f"{seconds}s"


def render_doctor(report: DoctorReport, json_output: bool) -> None:
    if json_output:
        print(json.dumps(report.model_dump(mode="json"), indent=2))
        return
    print(f"codealmanac v{report.version}")
    print("")
    render_doctor_section("Install", report.install)
    render_doctor_section("Current wiki", report.wiki)


def render_doctor_section(title: str, checks: tuple[DoctorCheck, ...]) -> None:
    if len(checks) == 0:
        return
    print(f"## {title}")
    for check in checks:
        print(f"  {check.status.value} {check.message}")
        if check.fix is not None:
            print(f"    {check.fix}")
    print("")


def render_update_plan(plan: UpdatePlan, json_output: bool) -> None:
    if json_output:
        print(json.dumps(plan.model_dump(mode="json"), indent=2))
        return
    print(f"codealmanac {plan.installed_version}")
    print(f"update status: {plan.status.value}")
    print(f"install method: {plan.method.value}")
    print(f"message: {plan.message}")
    if plan.command:
        print(f"command: {shell_command(plan.command)}")
    if plan.fix is not None:
        print(plan.fix)


def render_update_result(result: UpdateResult, json_output: bool) -> None:
    if json_output:
        print(json.dumps(result.model_dump(mode="json"), indent=2))
        return
    render_update_plan(result.plan, json_output=False)
    if result.exit_code is not None:
        print(f"exit_code: {result.exit_code}")
    if result.stdout:
        print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
    if result.stderr:
        print(result.stderr, end="" if result.stderr.endswith("\n") else "\n")


def shell_command(command: tuple[str, ...]) -> str:
    return shlex.join(command)


def render_runs(records: tuple[RunRecord, ...], json_output: bool) -> None:
    if json_output:
        data = [record.model_dump(mode="json") for record in records]
        print(json.dumps(data, indent=2))
        return
    if len(records) == 0:
        print("# 0 jobs", file=sys.stderr)
        return
    for record in records:
        title = record.title or ""
        print(
            f"{record.run_id}\t{record.status.value}\t"
            f"{record.operation.value}\t{title}"
        )


def render_run(record: RunRecord, json_output: bool) -> None:
    if json_output:
        print(json.dumps(record.model_dump(mode="json"), indent=2))
        return
    print(f"id: {record.run_id}")
    print(f"operation: {record.operation.value}")
    print(f"status: {record.status.value}")
    if record.title is not None:
        print(f"title: {record.title}")
    if record.summary is not None:
        print(f"summary: {record.summary}")
    if record.error is not None:
        print(f"error: {record.error}")
    if record.harness_transcript is not None:
        print(
            "harness_transcript: "
            f"{record.harness_transcript.kind.value} "
            f"{record.harness_transcript.session_id}"
        )
        if record.harness_transcript.transcript_path is not None:
            print(
                "harness_transcript_path: "
                f"{record.harness_transcript.transcript_path}"
            )
    print(f"created_at: {record.created_at.isoformat()}")
    print(f"updated_at: {record.updated_at.isoformat()}")


def render_run_log(events: tuple[RunLogEvent, ...], json_output: bool) -> None:
    if json_output:
        data = [event.model_dump(mode="json") for event in events]
        print(json.dumps(data, indent=2))
        return
    for event in events:
        print(f"{event.sequence}\t{event.kind.value}\t{event.message}")


def render_run_attach(snapshot: RunAttachSnapshot, json_output: bool) -> None:
    if json_output:
        print(json.dumps(snapshot.model_dump(mode="json"), indent=2))
        return
    render_run_log(snapshot.events, json_output=False)
    if len(snapshot.events) == 0:
        print("no log events")
    print(f"status: {snapshot.record.status.value}")


def render_run_cancel(result: RunCancelResult, json_output: bool) -> None:
    if json_output:
        print(json.dumps(result.model_dump(mode="json"), indent=2))
        return
    if result.changed:
        print(f"cancelled {result.record.run_id}")
        return
    print(f"job already {result.record.status.value}: {result.record.run_id}")
