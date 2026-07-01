# Slice 111 - Web Source Runtime Boundaries

## Intent

Keep web URL runtime behavior unchanged while splitting the integration by
reason to change. `WebSourceRuntimeAdapter` currently owns source-runtime port
implementation, `httpx` streaming, response/document Pydantic models, content
type classification, Beautiful Soup HTML extraction, normalized text cleanup,
runtime rendering, and unavailable diagnostics in one 303-line file.

Cosmic Python chapter 13 says explicit dependencies are useful because they
avoid an implicit dependency on a specific detail. This slice keeps the
adapter's `httpx.Client` dependency explicit, but moves concrete HTTP,
document parsing, and rendering mechanics behind focused helper modules.

## Scope

- Keep `WebSourceRuntimeAdapter` as the only `SourceRuntimeAdapter`
  implementation for web URL refs.
- Add web runtime modules for typed models, HTTP fetching, document parsing,
  rendering, and unavailable diagnostics.
- Add an architecture test that prevents `adapter.py` from regrowing HTTP
  streaming, Beautiful Soup parsing, Pydantic response models, or rendering
  helpers.
- Preserve all existing public behavior and runtime text.

## Out Of Scope

- No crawler.
- No durable source library.
- No semantic extraction or notability decisions.
- No new supported content types.
- No retry/backoff policy.

## Verification

- Focused web source runtime tests.
- Focused ingest test that uses a web runtime.
- Focused architecture test.
- Service-level dogfood with `httpx.MockTransport`.
- Full pytest, Ruff, and diff check before commit.
