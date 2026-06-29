# CodeAlmanac Notes For Cosmic Python

Source: https://github.com/cosmicpython/book

Converted from vendored commit: `d4522c44ed89eb320ad9eed2525d2af3b149bd3f`

License in source repo: `Creative Commons CC-By-ND`

This directory contains Markdown-only reference copies of Architecture Patterns with Python by Harry Percival and Bob Gregory. The Markdown files are mechanical format conversions from the upstream AsciiDoc files. Do not rewrite, abridge, rearrange, or edit the book text here. Put CodeAlmanac-specific interpretation in this file, repo docs, or `.almanac/` pages.

## Use During Python Coding

Before non-trivial Python implementation, read the chapters that match the shape being changed:

| Task | Read |
|---|---|
| Persistence boundary, SQLite stores, fake stores | `chapter_02_repository.md` |
| Product verbs, CLI-to-service boundary | `chapter_04_service_layer.md` |
| Test shape and fast service tests | `chapter_05_high_gear_low_gear.md` |
| Transaction boundaries and atomic writes | `chapter_06_uow.md` |
| Message/event workflows | `chapter_08_events_and_message_bus.md` |
| Command objects and run requests | `chapter_10_commands.md` |
| Composition root and dependency wiring | `chapter_13_dependency_injection.md` |
| Package layout comparison | `appendix_project_structure.md` |

## Useful Lines

- Chapter 2 argues for a domain model with "no dependencies whatsoever."
- Chapter 4 says the service layer defines "the use cases of our system."
- Chapter 6 describes Unit of Work as an abstraction over "atomic operations."
- Chapter 13 uses a bootstrap/composition root so entrypoints stop doing setup.

## Translation To CodeAlmanac

CodeAlmanac does not need to copy the book's exact folders. The useful transfer is the dependency rule:

```text
cli
  -> app
    -> workflows
      -> services
        -> stores
        -> ports
          -> integrations
```

For this repo:

- Repository pattern maps to `store.py`, `*_store.py`, and store fakes.
- Service layer maps to `services/*/service.py`.
- Unit of Work maps to explicit SQLite transaction ownership inside services and workflows.
- Bootstrap maps to `src/codealmanac/app.py`.
- Adapters map to `integrations/*`, implementing ports defined by services.

When a future plan quotes the book, keep quotes short and cite the local chapter path.
