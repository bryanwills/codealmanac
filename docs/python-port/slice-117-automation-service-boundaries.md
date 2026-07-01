# Slice 117: Automation Service Boundaries

## Scope

Keep local automation behavior unchanged while splitting scheduler task
selection and scheduled-job construction out of `AutomationService`.

## Out of scope

- No new automation tasks.
- No change to scheduled command arguments.
- No change to setup automation behavior.
- No launchd adapter changes.
- No scheduled update automation.

## Design

Cosmic Python chapter 4 says the application service orchestrates an operation.
For automation, `AutomationService` should orchestrate install, uninstall, and
status. It should not also own task defaulting, install validation, launch PATH
construction, plist path construction, or command argv assembly.

Target shape:

```python
selection = install_task_selection(request)
jobs = tuple(job_factory.job_for_task(task, request, selection.explicit_tasks, True)
             for task in selection.tasks)
for job in jobs:
    scheduler.install(job)
```

`selection.py` owns task defaulting and validation. `definitions.py` owns static
task metadata. `jobs.py` owns `ScheduledJob` construction.

## Verification

- Focused automation service tests.
- Architecture guard keeping selection and job mechanics out of
  `AutomationService`.
- Isolated service dogfood with a fake scheduler.
- Full pytest, Ruff, and diff hygiene.
