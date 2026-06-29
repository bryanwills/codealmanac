# Slice 4: Tag And Untag

Date: 2026-06-29

## Scope

Add deterministic page-topic mutation:

- `codealmanac tag <page> <topic> [<topic>...]`
- `codealmanac untag <page> <topic> [<topic>...]`

The command rewrites only page frontmatter. The body must remain byte-for-byte
unchanged. Topics can be ad-hoc; explicit topic metadata commands can come
later.

## Out Of Scope

- no topic create/rename/delete/describe
- no `--stdin`
- no lifecycle/AI work
- no hosted commands

## Architecture

```python
app.tagging.tag(TagPageRequest(...))
app.tagging.untag(UntagPageRequest(...))
```

`tagging` owns the product verb. `pages/index` locate the page file. `wiki`
owns frontmatter rewrite mechanics. CLI renders a short summary only.

Cosmic Python pressure: keep the mutation behind a service method; do not make
CLI a writer and do not let the index store edit markdown.

## Library Choice

Use `ruamel.yaml` for frontmatter YAML mutation because it is a known
round-trip YAML library. Do not use ad-hoc YAML string surgery except for the
frontmatter fence split, which is syntax owned by this project.

## Verification

- body bytes preserved
- comments in frontmatter survive
- CRLF frontmatter stays CRLF
- tag/untag are idempotent
- no-frontmatter page gets frontmatter
- live CLI tag/untag smoke
