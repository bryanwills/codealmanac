# Agent Guide Inline Citations Plan

## Goal

Tell coding agents to cite CodeAlmanac pages inline when Almanac knowledge
contributes to a final answer.

## Scope

- Add the agreed citation guidance to the canonical installed agent guide.
- Verify that both Codex and Claude receive the guidance.

## Out Of Scope

- Changing instruction installation mechanics or destinations.
- Changing Almanac page citation syntax or wiki authoring rules.

## Files

- Modify: `src/codealmanac/services/setup/agent-guide.md`
- Modify: `tests/test_setup_service.py`

## Verification

```bash
uv run pytest tests/test_setup_service.py -k 'codex_block or claude_guide'
uv run ruff check tests/test_setup_service.py
```
