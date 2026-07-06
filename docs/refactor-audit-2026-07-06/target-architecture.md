# Target Architecture

## Overall Shape

Keep the current top-level architecture:

```text
cli/server -> app -> workflows -> services -> stores/ports -> integrations
```

This is the right CodeAlmanac translation of Cosmic Python. It keeps entrypoints
thin, services product-oriented, persistence in stores, and outside systems in
integrations.

## What Should Change

### Renderers Should Not Become Toolkits

CLI render modules should render command results. Shared terminal mechanics
belong in a small render-support module with a plain name.

Target feel:

```python
render_setup_result(result)
  -> setup_summary(result)
  -> terminal.card(...)
  -> brand.banner(...)
```

The service still returns facts. The renderer still owns presentation. The
terminal helpers stop hiding inside one command renderer.

### The Composition Root Should Be Scannable

`app.py` should remain the public composition root. The goal is not a DI
container. The goal is to make wiring groups visible:

```python
stores = create_stores(config)
services = create_services(config, stores, adapters)
workflows = create_workflows(services, adapters)
return CodeAlmanac(..., workflows=workflows)
```

If helper extraction makes the graph harder to see, do not do it.

### Architecture Tests Should Guard Rules

Architecture tests should mostly guard:

- import direction;
- forbidden dependencies by layer;
- file-size caps by family;
- renderer-only terminal dependencies;
- stores owning SQL and persistence;
- services owning product verbs;
- integrations staying concrete and edge-local.

Exact-fragment assertions are allowed only when the exact fragment is the
boundary.

### Facades Should Have Jobs

Keep facades that are the service-facing or command-facing boundary. Remove
facades that only preserve stale import paths after all callers have moved.

## What Should Not Change

- Public command behavior.
- Terminal output bytes unless a test is only pinning internal layout.
- Local-only product contract.
- `almanac/` as the repo wiki tree.
- `~/.codealmanac/` as user/runtime state.
- Prompt intelligence over pipeline state machines.
- Service-owned ports and concrete integrations under `integrations/`.
