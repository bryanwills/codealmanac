# Serve Opens The Viewer

**Goal:** Make `codealmanac serve` open the local viewer in the default browser
once the HTTP server is ready, while preserving the printed URL and allowing
headless callers to opt out.

## Scope

- Open the viewer by default after Uvicorn has bound its listening socket.
- Add `--no-open` for SSH, containers, and scripted usage.
- Preserve the existing host, port, wiki selection, URL output, server logs,
  clean Ctrl-C shutdown, and startup-failure exit behavior.
- Document and test both default and opt-out behavior.

## Design

Browser launching remains in `cli/dispatch/serve.py`, beside the Uvicorn process
mechanism it accompanies. The command creates a normal `uvicorn.Server` and a
small daemon thread waits for `Server.started` before using Python's standard
`webbrowser` module. This avoids opening a browser for a server that failed to
bind and keeps the read-only viewer application free of desktop side effects.

```python
server = uvicorn.Server(config)
browser.open_when_ready(server, url)  # skipped by --no-open
server.run()
```

No service or application-layer seam is needed: opening a desktop browser is a
single CLI adapter concern, not viewer product logic.

## Files

- `src/codealmanac/cli/parser/wiki.py`: add `--no-open`.
- `src/codealmanac/cli/dispatch/serve.py`: launch the browser after startup.
- `src/codealmanac/cli/syntax/catalog.py`: expose the opt-out in guidance.
- `tests/test_cli.py`: cover parser and runtime behavior.
- `README.md`: describe the new default and opt-out.
- `almanac/architecture/viewer/local-viewer.md` and
  `almanac/reference/cli/public-command-surface.md`: update durable command
  knowledge.

## Verification

- Focused CLI tests for default opening and `--no-open`.
- `uv run pytest`.
- `uv run ruff check .`.

## Read Before Coding

- `MANUAL.md`
- `docs/python-port-live-agreement.md`
- `almanac/architecture/viewer/local-viewer.md`
- `almanac/architecture/cli/adapter-boundary.md`
- `almanac/architecture/cli/terminal-output.md`
- `almanac/reference/cli/public-command-surface.md`
