from contextlib import suppress

from codealmanac.prompts import PromptRenderer
from codealmanac.services.control.models import ControlRunStatus
from codealmanac.services.control.requests import (
    GetControlRunRequest,
    UpdateControlRunRequest,
)
from codealmanac.services.control.service import ControlService
from codealmanac.services.engine_runs.models import EngineRunStatus
from codealmanac.services.engine_runs.requests import (
    ReadEngineRunRequest,
    WriteEngineRunResultRequest,
)
from codealmanac.services.engine_runs.service import EngineRunsService
from codealmanac.services.harnesses.requests import RunHarnessRequest
from codealmanac.services.harnesses.service import HarnessesService
from codealmanac.workflows.lifecycle import first_line, validate_harness_result
from codealmanac.workflows.local_engine.events import (
    append_error,
    append_status,
    record_harness_events,
)
from codealmanac.workflows.local_engine.models import LocalEngineRunResult
from codealmanac.workflows.local_engine.prompt import render_update_prompt
from codealmanac.workflows.local_engine.requests import ExecuteLocalEngineRunRequest
from codealmanac.workflows.local_engine.result import (
    commit_subject_from_summary,
    engine_changed_files,
)
from codealmanac.workflows.local_runs.refs import path_ref


class LocalEngineWorkflow:
    def __init__(
        self,
        control: ControlService,
        engine_runs: EngineRunsService,
        harnesses: HarnessesService,
        prompts: PromptRenderer,
    ):
        self.control = control
        self.engine_runs = engine_runs
        self.harnesses = harnesses
        self.prompts = prompts

    def execute(self, request: ExecuteLocalEngineRunRequest) -> LocalEngineRunResult:
        run = self.control.get_run(GetControlRunRequest(run_id=request.run_id))
        try:
            engine_request = self.engine_runs.read_request(
                ReadEngineRunRequest(run_id=run.id)
            )
            self.control.update_run(
                UpdateControlRunRequest(
                    run_id=run.id,
                    status=ControlRunStatus.RUNNING,
                )
            )
            append_status(self.control, run.id, "started local engine worker")
            harness = self.harnesses.run(
                RunHarnessRequest(
                    kind=request.harness,
                    cwd=engine_request.repo_path,
                    prompt=render_update_prompt(self.prompts, engine_request),
                    title=request.title,
                )
            )
            record_harness_events(self.control, run.id, harness)
            validate_harness_result(harness)
            engine_result = self.engine_runs.write_result(
                WriteEngineRunResultRequest(
                    run_id=run.id,
                    status=EngineRunStatus.SUCCEEDED,
                    summary=harness.summary,
                    commit_subject=commit_subject_from_summary(harness.summary),
                    commit_body=harness.summary,
                    changed_files=engine_changed_files(
                        engine_request.repo_path,
                        harness,
                    ),
                )
            )
            result_ref = path_ref(self.engine_runs.paths(run.id).result_path)
            updated = self.control.update_run(
                UpdateControlRunRequest(
                    run_id=run.id,
                    result_ref=result_ref,
                    summary=engine_result.summary,
                    commit_subject=engine_result.commit_subject,
                    commit_body=engine_result.commit_body,
                )
            )
            append_status(
                self.control,
                run.id,
                "completed local engine worker; delivery pending",
                result_ref,
            )
            return LocalEngineRunResult(
                executed=True,
                run=updated,
                engine=engine_result,
                harness=harness,
            )
        except Exception as error:
            return self.fail(run.id, error)

    def fail(self, run_id: str, error: Exception) -> LocalEngineRunResult:
        message = first_line(str(error)) or error.__class__.__name__
        engine_result = None
        result_ref = None
        with suppress(Exception):
            engine_result = self.engine_runs.write_result(
                WriteEngineRunResultRequest(
                    run_id=run_id,
                    status=EngineRunStatus.FAILED,
                    error=message,
                )
            )
            result_ref = path_ref(self.engine_runs.paths(run_id).result_path)
        updated = self.control.update_run(
            UpdateControlRunRequest(
                run_id=run_id,
                status=ControlRunStatus.FAILED,
                result_ref=result_ref,
                error=message,
            )
        )
        append_error(self.control, run_id, message, result_ref)
        return LocalEngineRunResult(
            executed=False,
            reason="engine_failed",
            run=updated,
            engine=engine_result,
        )
