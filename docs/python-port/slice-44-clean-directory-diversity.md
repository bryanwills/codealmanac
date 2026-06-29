# Slice 44 - Clean Directory Diversity

## Scope

Improve bounded directory source runtime when the selected tree has no changed
files, without changing the source product model.

Directory input remains one `SourceRef`. The filesystem runtime still returns
one `SourceRuntime`. Selection remains adapter-local prompt-material policy.

## Shape

```text
Git or Python walk
  -> FilesystemDirectoryCandidate(...)
  -> ranked_directory_candidates(...)
  -> read selected text files
  -> SourceRuntime(content=...)
```

The selector is a pure functional core. It does not call Git, walk the
filesystem, read file bytes, or know about Ingest.

## Behavior

- changed and untracked candidates rank before unchanged candidates
- unchanged selection interleaves directory groups before selecting a second
  file from the same group
- role-bearing files such as `service.py`, `adapter.py`, `app.py`, and
  `main.py` rank ahead of generic source files inside a group
- Git directory runtime metadata reports `selection_policy:
  changed_then_diverse`

## Cosmic Python Note

Chapter 3 shaped this slice. The filesystem adapter first interrogates the
messy filesystem/Git state, then a small pure function decides what material is
worth reading, then the adapter performs file reads for the selected paths.

That keeps the ranking policy easy to test without faking Git or local files,
while the public source-runtime tests still exercise the edge-to-edge behavior.

## Dependency Check

Searched current docs before keeping this local. `identify` and Pygments solve
file type/lexer classification, and tree-sitter solves source parsing. This
slice needs repo-role and directory-group selection for bounded prompt
material. That policy is CodeAlmanac-specific, so adding a runtime dependency
would not remove the core decision.

## Verification

- focused selector/runtime tests:
  `uv run pytest tests/test_filesystem_directory_selection.py tests/test_filesystem_source_runtime.py`
- focused lint:
  `uv run ruff check src/codealmanac/integrations/sources/filesystem tests/test_filesystem_directory_selection.py tests/test_filesystem_source_runtime.py`
- dogfood:
  inspect `src/codealmanac/` through `app.sources.inspect_runtime(...)` and
  confirm changed filesystem files stay first while clean service/workflow
  groups are represented
