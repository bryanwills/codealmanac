# Research Notes

These notes anchor the refactor in external guidance and local repo rules.

## Local Manual

`MANUAL.md` says the unit of work is to evolve the codebase so the feature fits, then build it. It also says naming is architecture and that seams should be built eagerly while machinery is deferred.

For this refactor, that means:

- introduce the package seams that make `trigger`, `source_bundle`, `run`, `delivery`, and `wiki` obvious;
- avoid building extra abstractions if there is still only one implementation;
- remove stale compatibility once callers have moved.

## Cosmic Python

Relevant ideas:

- The service/use-case layer should be the main entrypoint into the app, usable by CLI, HTTP, workers, and tests.
- Web/API handlers should do web work: parse request, call service, return response.
- Unit of Work is useful where multiple SQL writes must commit together.
- Repositories/stores own persistence, not routes.

Local references:

- `docs/reference/cosmic-python/chapter_04_service_layer.md`
- `docs/reference/cosmic-python/chapter_06_uow.md`
- `docs/reference/cosmic-python/chapter_10_commands.md`
- `docs/reference/cosmic-python/chapter_13_dependency_injection.md`

External references checked:

- FastAPI bigger applications: https://fastapi.tiangolo.com/tutorial/bigger-applications/
- Python Packaging `src` layout: https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/
- Cosmic Python service layer: https://www.cosmicpython.com/book/chapter_04_service_layer
- Cosmic Python Unit of Work: https://www.cosmicpython.com/book/chapter_06_uow

## FastAPI Shape

FastAPI's official larger-app guidance keeps routers as separate modules and includes them from the main app. That supports the current hosted direction:

```text
web/
  routes/
  dto/
  deps.py
```

The important part is not the exact folder names. The important part is keeping route handlers thin and not letting router modules own product orchestration.

## Packaging

Both repos already use `src/` layout. Keep it. PyPA documents that `src/` helps avoid importing accidental local files and helps ensure only intended import packages are importable.

## Main Takeaway

Use product domains plus edges:

```text
edges: cli, web, worker
domains: identity, repositories, conversations, runs, wiki, billing
adapters: github, workos, modal, autumn, posthog, git, filesystem
```

Do not keep growing flat `services/*` folders with overlapping nouns.

