# Wiki Quality Audit

Date: 2026-06-13

Goal:
Critically audit the wiki guidance and maintenance mechanism for CodeAlmanac by
comparing the current CodeAlmanac wiki, the newer General Almanac / Reverie
workspace, and the General Almanac manual work.

Core questions:

- Why did the newer Reverie wiki produce higher-quality pages?
- Which CodeAlmanac guidance paths let wiki quality degrade?
- What should be preserved from CodeAlmanac's codebase-wiki model?
- What should be imported from General Almanac's manual/conventions model?
- What mechanism improves quality without adding a heavy pipeline?

Non-goals:

- Do not modify production code in this audit.
- Do not replace the markdown wiki model.
- Do not propose schema-heavy orchestration unless a real query or review need
  requires it.

Success criteria:

- The quality difference is stated concretely.
- The target guidance mechanism is small enough for agents to follow.
- The target mechanism includes coverage, review, and maintenance loops.
- The proposal includes a code-wiki-specific wireframe.

Artifacts:

- `worklog.md` records what was inspected.
- `comparison.md` compares Reverie, CodeAlmanac, and General Almanac doctrine.
- `target-mechanism.md` proposes the next guidance architecture.
