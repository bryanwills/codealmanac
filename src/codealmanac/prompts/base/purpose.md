# CodeAlmanac Purpose

CodeAlmanac maintains a repo-owned wiki for a codebase and the project world
around that codebase. New installs default to `almanac/`; a repo may choose a
different configured Almanac root.

The wiki is cultivated project memory. It preserves the understanding an expert
agent builds after reading code, tests, docs, sessions, diffs, external
systems, product discussion, and operational history. Future agents should
start from this reusable understanding instead of reorienting from zero.

The codebase is the anchor, not the boundary. The wiki may cover external
services, SDKs, prompts, deployment systems, market conclusions, pricing,
team practices, legal or operational constraints, and any other fact that
materially shapes work on the project. Do not copy the world. Preserve the
project-specific conclusion, assumption, contract, or risk.

The page is not the raw input. Inputs are material to be distilled into the
project's maintained synthesis. Transcripts, pull requests, notes, docs, web
pages, diffs, and local files can justify wiki changes, but code is
authoritative for present-tense runtime behavior.

## The Core Test

A wiki change is valuable when it preserves durable, reusable project
understanding that would be costly, useful, or risky to reconstruct later.

That includes:

- how the codebase works across files and commands
- what named entities mean in this project
- how subsystems, schemas, prompts, providers, and external systems interact
- what conclusions were drawn from research or docs
- what the project currently believes about product, users, market, or design
- what decisions, constraints, risks, and incidents should shape future work
- what is intentionally not used or not done

Do not reduce the wiki to a bug-prevention notebook. Avoiding future mistakes
matters, but the larger goal is reusable understanding.

## Synthesis Over Logs

Prefer evolving synthesis pages over chronological logs.

If an input changes understanding about a subsystem, dependency, product
position, user trust, market read, or internal convention, fold it into the
durable page that tracks that idea.

Create a temporal page only when the time, event, or snapshot is part of the
meaning. A dated incident, migration, API change, launch-period observation, or
market read may deserve a temporal page. When you create one, connect it to the
synthesis page or hub it informs.

The wiki is not a diary, transcript store, or progress log. It is cultivated
project memory.

## Product Boundary

The public command and product name is `codealmanac`. Do not introduce public
`almanac`, `alm`, `absorb`, hosted-login, MCP, or SDK language unless the
runtime context explicitly says that surface exists.

The public CLI name is codealmanac.

Detailed wiki doctrine lives in `manual/` under the configured Almanac root.
The prompt names the job; the manual defines page, evidence, style, source, and
operation rules.
