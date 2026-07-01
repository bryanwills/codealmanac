# Slice 122: CLI Wiki Render Boundaries

## Scope

Keep wiki CLI output unchanged while splitting the wiki render edge by output
family.

## Out of scope

- No parser flag changes.
- No dispatch request changes.
- No service/workflow behavior changes.
- No hosted command surface.

## Design

Cosmic Python chapter 4 says the service layer handles workflows and use cases
while interfacing code adapts the outside world. The CLI render edge is
interfacing code: it turns typed service results into text or JSON. It should
not become a second service layer, and it should not group unrelated output
families just because they all belong to the wiki command surface.

The sibling Almanac CLI keeps hosted renderers split by noun. CodeAlmanac's
local equivalent is:

```python
cli.render.root        # public facade imported by dispatchers
  -> cli.render.wiki   # wiki-render facade only
      -> search.py     # search and reindex output
      -> pages.py      # show/page output
      -> topics.py     # topic list/show/mutation output
      -> health.py     # health report output
      -> tagging.py    # tag/untag output
```

`cli/render/wiki.py` remains an import-compatible facade. New rendering logic
belongs in the command-family module that owns the displayed result.

## Verification

- Focused CLI, topic mutation, and architecture tests.
- Architecture guard keeping service model imports and `render_*` definitions
  out of `cli/render/wiki.py`.
- Isolated public CLI dogfood for init, list, search, show, topics, health,
  tag/untag, and reindex.
