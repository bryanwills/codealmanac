# Worklog

## 2026-06-13

Read process guidance:

- `MANUAL.md`
- `.almanac/README.md`
- current CodeAlmanac wiki pages
- current CodeAlmanac prompt modules
- General Almanac prompt modules and manual pages
- General Almanac Empress experiment notes
- Reverie General Almanac workspace

Tooling notes:

- `ga` was not installed on the active shell path.
- `../almanac/package.json` defines `ga` as a bin alias for `dist/launcher.js`.
- The local equivalent used for inspection was:

```bash
node /Users/rohan/Desktop/Projects/almanac/dist/launcher.js
```

Registered General Almanac workspaces:

- `reverie` -> `/Users/rohan/Documents/Almanacs/reverie`
- `empress` -> `/Users/rohan/Desktop/Projects/almanac/data/empress`

Observed wiki health:

- Reverie health: clean across graph, source, legacy, and duplicate checks.
- Empress health: clean graph, but still has legacy `files:` frontmatter and
  unused-source warnings.
- CodeAlmanac health: graph mostly clean, but source hygiene is noisy:
  6 dead refs, 346 unused sources, 29 legacy-frontmatter pages, and
  130 unfixable ambiguous legacy sources.

Notable CodeAlmanac prompt drift:

- `prompts/base/notability.md` ends with an orphan heading:
  `## **type: runtime-view**`.
- That looks like architecture-note residue that became doctrine by accident.

Important comparison result:

- Reverie quality is not mainly from more schema. It comes from a tighter
  article contract, a local conventions guide, clean source/citation discipline,
  and folder pressure that makes page identity visible.
