# Slice 99: Source Target Fallback

## Scope

Structured page `sources:` are already part of the Python read model, but the
parser only reads type-specific address fields such as `path:` for file sources
and `url:` for web sources. Some lifecycle tests and prompt-shaped outputs use
generic `target:` instead. Those pages keep a `PageSource` row but lose the
target address, so `sources[type=file]` does not feed file-aware retrieval.

This slice makes `target:` a generic fallback for every source type while
preserving type-specific fields as the preferred authoring contract.

## Out Of Scope

- No legacy string-source migration.
- No public migration command.
- No new source type.
- No replacement of current `path:` / `url:` guidance.

## Design

`src/codealmanac/services/wiki/frontmatter.py` remains the normalization
boundary for page frontmatter. It parses raw YAML into `PageSource` values. The
type-specific fields continue to win when present, and `target:` is checked only
after the type-specific fields are absent.

This follows the service-boundary shape from Cosmic Python: "The service layer
will become the main way into our app" in
`docs/reference/cosmic-python/chapter_04_service_layer.md`. Here the page parser
is the boundary between raw frontmatter and the rest of the read model; search,
show, health, and viewer code should not know alternate source spellings.

## File Changes

- `src/codealmanac/services/wiki/frontmatter.py`
  - Add a module-level source target field map.
  - Read type-specific fields first, then generic `target:`.
- `tests/test_wiki_parsing.py`
  - Prove generic `target:` parses for file sources.
  - Prove type-specific fields beat generic `target:`.
- `tests/test_read_model.py`
  - Prove a file source using `target:` projects into `show.sources` and
    `search --mentions`.
- Steering docs
  - Record the current contract in the live agreement, idea evolution, ownership
    map, and next-agent brief.

## Verification

- Focused pytest for parsing and read-model behavior.
- Focused ruff on touched code/tests.
- Full `uv run pytest`.
- Full `uv run ruff check .`.
- `git diff --check`.
- Dogfood an isolated repo with a page using `sources[type=file].target` and
  prove `codealmanac show --json` and `codealmanac search --mentions` see it.
