# Hand-Rolled Inventory

## Path And Layout Resolution

**What is custom:** `src/wiki/locations.ts`, `src/paths.ts`, and
`src/wiki/topics/paths.ts` hand-roll wiki layout resolution.

**Assessment:** Keep custom, but consolidate. This is product-specific and not
a generic path problem a library would solve. The risk is not lack of a library;
the risk is a weak boundary.

**Recommendation:** replace helper composition with a `WikiLayout` object.

## Markdown Frontmatter Parsing

**What is custom:** `src/wiki/indexer/frontmatter.ts` parses a controlled set of
frontmatter fields after `js-yaml` parses YAML.

**Assessment:** Keep. The parser is small and domain-specific. The branch added
`page_id` cleanly.

**Risk:** Health and snapshots now need the same page identity semantics. The
frontmatter parser is shared, but page planning is not.

## Page Discovery And Slug Planning

**What is custom:** the indexer, job snapshots, and health each scan markdown
files and derive slugs.

**Assessment:** Simplify. This is the highest-value extraction candidate from
this branch.

**Recommendation:** create one page-discovery module that returns page root,
relative path, display path, parsed frontmatter, canonical slug, archive state,
and collision status.

## Topic DAG Storage

**What is custom:** topic YAML loading/writing, parent edges, cycle checks, and
SQLite projection.

**Assessment:** Keep custom. Topic DAG semantics are core product behavior.

**Risk:** read-path and mutation-path resolution now differ during migration.
That distinction should become explicit API names.

## Viewer Rendering

**What is custom:** `viewer/app.js` is hand-written browser UI and routing.

**Assessment:** Keep for now. The viewer is small, dependency-free, and tests
pin important strings. The main risk is stale product language in route names,
not rendering machinery.
