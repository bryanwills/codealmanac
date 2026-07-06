---
title: Types
summary: Pydantic everywhere, enums for closed sets, no dynamic attribute access, parse at the edge.
topics: [style]
sources:
  - id: manual
    type: file
    path: MANUAL.md
    note: Craft rules on typed models and dynamic access.
  - id: base-model
    type: file
    path: src/codealmanac/core/models.py
    note: Shared CodeAlmanacModel base.
---

# Types

All shaped data is a Pydantic model. Services accept typed request objects and return typed results; nothing structured travels as a loose `dict` [@manual]. The shared base is `CodeAlmanacModel` [@base-model]. Closed sets of values are enums (`StrEnum`), never bare strings compared by convention.

No `getattr`, `hasattr`, `setattr`, or any dynamic attribute access — static access only [@manual]. Dict `.get()` on parsed JSON is data access and is fine.

External shapes are parsed once, at the edge, into typed values; nothing downstream touches the raw payload [@manual]. The same rule applies to tool output: if a provider, SDK, or CLI can return structured output, use that contract instead of scraping meaning out of prose with regex. Regex is for syntax we own — frontmatter fences, durations, path normalization — not for durable meaning.

Validation is defense in depth: an invariant worth having is re-checked at every layer that could violate it, including immediately after a write that could break it [@manual].
