---
title: Deep Refactor Audit
summary: The deep refactor audit skill is a repo-owned agent workflow for no-code architecture critique that forces feature, dependency, hand-rolled machinery, and accidental-complexity questions before implementation.
topics: [agents, prompt-system, decisions]
sources:
  - id: repo-skill
    type: file
    path: .agents/skills/deep-refactor-audit/SKILL.md
    note: Defines the repo-owned Codex skill body and the audit workflow.
  - id: claude-skill
    type: file
    path: .claude/skills/deep-refactor-audit/SKILL.md
    note: Mirrors the same skill body for Claude skill discovery.
  - id: codex-metadata
    type: file
    path: .agents/skills/deep-refactor-audit/agents/openai.yaml
    note: Provides Codex/OpenAI skill UI metadata that is not copied into the Claude skill directory.
  - id: cleanslate-skill
    type: file
    path: .agents/skills/cleanslate/SKILL.md
    note: Shows that this repo already uses `.agents/skills` for repo-owned reusable skills.
  - id: creation-session
    type: conversation
    path: /Users/rohan/.codex/sessions/2026/06/07/rollout-2026-06-07T18-16-14-019ea4cd-3d5b-7110-a5ed-c9ae7d9caac2.jsonl
    note: Records the user request to add hand-rolled-library scrutiny and install the skill in personal, repo, and Claude locations.
status: active
verified: 2026-06-08
---

# Deep Refactor Audit

The deep refactor audit is a repo-owned agent skill for major architecture audits, refactor audits, smell investigations, boundary critiques, feature simplification reviews, AI-generated cleanup assessments, hand-rolled library reviews, and no-code reports about how a codebase should be reshaped. It is not an implementation workflow: the skill may create notes, diagrams, reports, and plans under `docs/`, but it tells the agent not to edit implementation files during the audit. [@repo-skill]

The skill was created after the user identified unnecessary hand-rolling as a recurring AI failure mode. The durable concern is that an agent may build a custom parser, scheduler, state machine, or other standard piece of machinery without first checking whether a mature library or framework feature already solves the problem. The skill preserves that concern as a first-class audit category rather than a one-off code-review comment. [@creation-session] [@repo-skill]

## Locations

The Codex-facing repo copy lives at [[.agents/skills/deep-refactor-audit/SKILL.md]]. That location follows the repo's existing `.agents/skills` convention, already represented by [[.agents/skills/cleanslate/SKILL.md]]. [@repo-skill] [@cleanslate-skill]

The Claude-facing copy lives at [[.claude/skills/deep-refactor-audit/SKILL.md]] and matches the `.agents` skill body. The Codex/OpenAI UI metadata file, [[.agents/skills/deep-refactor-audit/agents/openai.yaml]], stays only under `.agents` because it describes Codex skill-list metadata rather than Claude skill behavior. [@claude-skill] [@codex-metadata] [@creation-session]

## Audit Contract

The skill starts each audit by setting an explicit goal for the scope under review. The goal asks which architecture, features, boundaries, names, abstractions, dependencies, and workflows should be preserved, simplified, removed, or redesigned. [@repo-skill]

The audit boundary is deliberately no-code. Because the agent is not modifying production files, the skill tells it to take stronger intellectual risks: question feature value, user behavior, dependency choices, naming, and whether entire subsystems should exist. [@repo-skill]

The skill classifies findings as `Keep`, `Simplify`, `Delete candidate`, `Replace with library`, `Redesign`, or `Unknown`. That classification separates legitimate complexity from accidental complexity and makes library replacement an explicit outcome when custom code hand-rolls a solved problem without a strong reason. [@repo-skill]

## Hand-Rolled Machinery

The skill requires an inventory of custom infrastructure for parsing, date/time handling, glob/path matching, CLI parsing, config loading, HTTP clients, retries, schedulers, locks, caches, storage helpers, validation, error formatting, React state, forms, tables, drag/drop, rich text, and data fetching. [@repo-skill]

For each candidate, the audit asks what standard library, framework feature, or popular package already solves the problem; what special constraints might justify owned code; what bugs or maintenance costs the custom version creates; what would be deleted by adopting the existing solution; and whether the final recommendation is to keep custom code, replace it, wrap a library behind a boundary, or research further. [@repo-skill]

This rule connects directly to [[accidental-special-case-architecture]]. Hand-rolled code can be legitimate when a small owned syntax, a security-sensitive boundary, a performance constraint, or a product-specific grammar makes a dependency the worse choice. The audit exists to force and record that justification before the codebase treats the custom machinery as settled architecture. [@repo-skill]

## Artifacts And Review

For substantial audits, the skill creates a dated `docs/refactor-audit-YYYY-MM-DD/` folder with a worklog, source map, smell list, feature questions, hand-rolled inventory, research notes, subagent briefs, reports, target architecture, and refactor roadmap. Small repositories can use fewer files, but the running worklog is mandatory so another agent can resume the audit after context compaction. [@repo-skill]

The skill encourages independent critique through subagents when available. The named roles are boundary critic, feature skeptic, hand-rolled machinery critic, pattern researcher, deletion advocate, target architect, and migration realist; their reports belong under the audit folder's `reports/` directory. [@repo-skill]

The final report must include an executive summary, architecture map, strongest objections, deletion or simplification candidates, hand-rolled machinery recommendations, legitimate complexity worth preserving, accidental complexity likely caused by incremental or AI-generated work, prior art and named patterns considered, target architecture, refactor roadmap, open questions, and the notes or reports written during the audit. [@repo-skill]
