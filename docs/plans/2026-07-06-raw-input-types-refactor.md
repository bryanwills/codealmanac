# Raw Input Types Refactor Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Remove production `Any` annotations from raw input parsing without changing validation behavior.

**Architecture:** Keep Pydantic validators and JSON/YAML/TOML parsers tolerant at the boundary. Type unknown raw values as `object`, narrow them with explicit runtime checks, then return existing typed request/config/wiki models.

**Tech Stack:** Pydantic validators, JSON registry parsing, YAML/frontmatter parsing, existing pytest coverage, ruff.

---

## Scope

In scope:

- Replace production `typing.Any` annotations in raw validators and parsers with
  `object`.
- Add a narrow `RawSource` alias for frontmatter source maps.
- Keep all runtime checks and error messages unchanged.
- Update the refactor worklog.

Out of scope:

- No new validation rules.
- No broad parser rewrites.
- No behavior change for malformed raw input.

## Tasks

### Task 1: Tighten Raw Input Signatures

**Files:**

- Modify: `src/codealmanac/services/wiki/frontmatter.py`
- Modify: `src/codealmanac/services/wiki/topic_models.py`
- Modify: `src/codealmanac/services/topics/requests.py`
- Modify: `src/codealmanac/services/tagging/requests.py`
- Modify: `src/codealmanac/services/config/models.py`
- Modify: `src/codealmanac/services/workspaces/store.py`
- Modify: `src/codealmanac/services/health/sources.py`

Steps:

1. Replace `Any` imports with `object` parameter annotations.
2. Keep Pydantic `mode="before"` validators accepting unknown raw values.
3. Add `type RawSource = dict[object, object]` for parsed frontmatter source maps.
4. Confirm no production `Any` remains:

```bash
rg -n "\bAny\b|dict\[str, Any\]|dict\[Any" src/codealmanac
```

Expected: no output.

### Task 2: Verify

Run:

```bash
uv run pytest tests/test_wiki_parsing.py tests/test_read_model.py tests/test_config_service.py tests/test_topics_mutation.py tests/test_tagging.py tests/test_topics_health.py tests/test_workspace_registry_store.py tests/test_validate.py -q
uv run ruff check src/codealmanac/services/wiki/frontmatter.py src/codealmanac/services/topics/requests.py src/codealmanac/services/tagging/requests.py src/codealmanac/services/wiki/topic_models.py src/codealmanac/services/config/models.py src/codealmanac/services/workspaces/store.py src/codealmanac/services/health/sources.py tests/test_wiki_parsing.py tests/test_read_model.py tests/test_config_service.py tests/test_topics_mutation.py tests/test_tagging.py tests/test_topics_health.py tests/test_workspace_registry_store.py tests/test_validate.py
uv run pytest
uv run ruff check .
git diff --check
```

Expected: all pass.

Commit:

```bash
git add src/codealmanac/services/wiki/frontmatter.py src/codealmanac/services/topics/requests.py src/codealmanac/services/tagging/requests.py src/codealmanac/services/wiki/topic_models.py src/codealmanac/services/config/models.py src/codealmanac/services/workspaces/store.py src/codealmanac/services/health/sources.py docs/plans/2026-07-06-raw-input-types-refactor.md docs/refactor-audit-2026-07-06/worklog.md
git commit -m "refactor: tighten raw input types"
```
