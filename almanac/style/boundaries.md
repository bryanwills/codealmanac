---
title: Boundaries
summary: Layers, boundary pressure, decision-vs-mechanism, seams before machinery, symmetry.
topics: [style, architecture]
sources:
  - id: manual
    type: file
    path: MANUAL.md
    note: Boundary and seam-vs-machinery principles.
  - id: app
    type: file
    path: src/codealmanac/app.py
    note: Composition root.
  - id: architecture-tests
    type: file
    path: tests/test_architecture.py
    note: Enforced layer symmetry and module caps.
---

# Boundaries

Code is organized in layers, and imports point one way: `cli → app → workflows → services → integrations / database`. Nothing imports upward, and `src/codealmanac/app.py` is the only place things are wired together [@app]. Each side of a boundary has explicit knowledge rules — the CLI edge must not know persistence, stores must not know rendering, integrations stay behind service-owned ports — and those rules are worth re-deriving whenever the code is touched, not assumed settled.

**Boundary pressure is the primary split signal.** When a module accumulates more than one reason to change, when a caller reaches around a layer, or when a name stops being honest, that pressure means the boundary is wrong — break it down and separate the responsibilities. Smaller files are generally preferred, but responsibility boundaries matter more than line count; something better served by one bigger file stays one file [@manual]. The counterweight: every new tracked file is public surface and future maintenance burden, so a split must earn its file.

**A decision is not a mechanism.** Policy lives in a selection step where it is visible and configurable; it is never an `if` buried inside the machinery it steers [@manual].

**Seams before machinery.** Build seams eagerly — a boundary, a name, a typed contract, a one-value enum. Build machinery lazily — the N implementations, the dispatcher, the config surface. A seam is right when the next feature lands additively against it; if landing a feature means teardown, fix the seam first [@manual].

**Symmetry is a requirement, not an aesthetic.** A reader should be able to guess what any file does, how data flows, and where the next thing goes, from having seen one sibling. The parser/dispatch/render triad per command family is the house example, and layer symmetry is enforced by tests [@architecture-tests]. When a change breaks symmetry, either restore it or change the pattern everywhere — never leave one asymmetric exception.
