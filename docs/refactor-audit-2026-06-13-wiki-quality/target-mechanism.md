# Target Mechanism

## Recommendation

Use a two-layer guidance mechanism:

1. A general code-wiki manual installed into each wiki.
2. A wiki-local convention guide that Garden keeps current.

The prompt should not carry the whole doctrine. It should say what to read and
what outcome to produce.

## Code-Wiki Manual Shape

For CodeAlmanac-style repositories, the manual should define these page
families:

- `system`: a named subsystem and its responsibility boundary.
- `runtime-flow`: what happens across files/processes at runtime.
- `contract`: CLI, API, schema, file format, provider, or prompt contract.
- `allocation`: where state, files, generated artifacts, and packages live.
- `decision`: why one architecture exists over alternatives.
- `failure-mode`: how something broke and what invariant prevents recurrence.
- `change-path`: how to safely modify a subsystem.
- `hub`: reading order for a dense neighborhood.

These are editorial families, not required frontmatter.

## Local Convention Guide

Each code wiki should have a maintained page such as:

```text
.almanac/pages/wiki-conventions.md
```

It should record:

- canonical page families used by this wiki;
- hub pages and their neighborhoods;
- naming conventions;
- topic conventions;
- source/citation rules;
- sensitive-data rules;
- known merge/split pressure;
- open editorial questions.

## Operation Flow

The operation prompts can stay small:

```text
run_operation(input):
  read general_manual
  read local_conventions
  inspect relevant wiki pages and sources
  choose page_home:
    update existing anchor
    create new subject page
    split overloaded page
    merge duplicate page
    add or revise hub
    no-op
  write article prose with citations
  update links, topics, and local conventions
  run health and source hygiene checks
```

The key change is that "choose page_home" becomes explicit editorial work before
writing prose.

## Review Loop

Quality review should ask:

- Is this page independently useful without the original session?
- Is it the canonical update home for one durable subject?
- Does the lead define the subject and give the important current facts?
- Are important claims cited near the claim?
- Are source lists evidence, not inspection logs?
- Are conflicts or source gaps visible when they affect interpretation?
- Does this page reduce future retrieval work?
- Does it link to the next pages a future agent should read?

## Coverage Loop

Coverage should be checked by neighborhoods, not only page count.

```text
review_neighborhood(subject):
  anchor = find_anchor(subject)
  expected = [
    system_boundary,
    runtime_flow,
    contracts,
    state_allocation,
    decisions,
    failure_modes,
    change_paths,
  ]
  for each expected page_family:
    mark present, missing, merged_into_anchor, or not_needed
  if readers need order:
    create_or_update_hub(subject)
```

This avoids both extremes: one giant page, or dozens of thin pages.

## First Practical Slice

Do not start by rewriting the whole wiki.

Suggested first slice:

1. Add a code-wiki manual page set or prompt module with the page-family rules.
2. Add `.almanac/pages/wiki-conventions.md` for CodeAlmanac.
3. Garden one dense neighborhood, probably lifecycle/sync or provider harness.
4. Measure before/after with health, source hygiene, page leads, and reader path.

Quality target:

- fewer unused sources;
- clearer canonical homes;
- one hub per dense area;
- no orphan prompt artifacts;
- pages that read as articles, not migrated notes.
