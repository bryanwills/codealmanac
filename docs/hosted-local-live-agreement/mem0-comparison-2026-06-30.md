# Mem0 Local, Self-Hosted, And Hosted Comparison

Date: 2026-06-30.
Local repo inspected: `/Users/rohan/Desktop/Projects/mem0`.
Local checkout state: `main` at `a623cfaf`, fetched `origin/main` at
`c325bd3b`; the working tree had pre-existing local changes, so this note did
not switch or pull the checkout. Current public docs and selected
`origin/main` files were also checked.

This note compares Mem0's open-source, self-hosted, hosted, CLI, and MCP shape
as inspiration for CodeAlmanac's local/hosted split.

## What Mem0 Is Selling

Mem0 sells "memory infrastructure for agents and apps." The public website
frames the product as persistent context across sessions and agents, with a
simple Add -> Learn -> Retrieve loop.

The website has three visible integration lanes:

- SDK integration
- agent harness / AI-client integration
- plugin / MCP integration

The website's enterprise section sells governance, portability, auditability,
and managed infrastructure. This is a clean fit for Mem0 because its core value
is an API-backed memory store, not a repo-native artifact.

Public source:

- <https://mem0.ai>

## Mem0's Three Product Paths

Mem0 has three paths:

| Path | Setup | What runs | Best for |
| --- | --- | --- | --- |
| Library | `pip install mem0ai` or `npm install mem0ai` | In-process memory engine plus configured vector/history stores | Testing and prototyping |
| Self-hosted server | `cd server && make bootstrap` or Docker Compose | API server, dashboard, auth, request logs, Postgres/pgvector | Teams running their own infrastructure |
| Platform | account/API key on `app.mem0.ai` | Mem0-hosted API, dashboard, scaling, governance, advanced features | Zero-ops production |

The local repo and docs agree on this structure. `README.md` presents Library,
Self-Hosted Server, and Cloud Platform as the three quickstart choices.
`docs/open-source/overview.mdx` says OSS can run either as a library or as a
self-hosted server with dashboard, per-user API keys, and request audit log.

Local sources:

- `/Users/rohan/Desktop/Projects/mem0/README.md`
- `/Users/rohan/Desktop/Projects/mem0/docs/open-source/overview.mdx`
- `/Users/rohan/Desktop/Projects/mem0/server/README.md`

Public sources:

- <https://docs.mem0.ai/open-source/overview>
- <https://docs.mem0.ai/platform/platform-vs-oss>

## Is Mem0 Heavy Or Light?

Mem0 is both, but the paths are explicitly different.

The library path is light. A developer can install a package and instantiate
`Memory()`. That is the local embedded engine. It still needs an LLM/embedder
and some storage config, but it does not require a separate hosted account or
full server stack.

The Python package also includes `MemoryClient`. That is not the same thing as
`Memory()`. `MemoryClient` is an HTTP client for the Mem0 API, defaults to
`https://api.mem0.ai`, requires a Mem0 API key, and posts to hosted/API paths
such as `/v3/memories/add/`.

Concrete split:

```python
# local embedded OSS engine
from mem0 import Memory
m = Memory()
m.add(messages, user_id="alex")

# hosted/API client
from mem0 import MemoryClient
client = MemoryClient(api_key="...")
client.add(messages, user_id="alex")
```

The self-hosted server path is heavy. It asks the user to run a service stack:

- FastAPI API server
- dashboard
- auth and per-user API keys
- request audit log
- Postgres with pgvector through Docker Compose
- LLM and embedder credentials

The public self-hosted docs say the reference path needs Docker Compose, an
LLM/embedder API key, and free ports for API/dashboard. The local
`server/docker-compose.yaml` confirms the stack has `mem0`, `postgres`, and
`mem0-dashboard` services.

Local sources:

- `/Users/rohan/Desktop/Projects/mem0/server/docker-compose.yaml`
- `/Users/rohan/Desktop/Projects/mem0/server/main.py`
- `origin/main:mem0/memory/main.py`
- `origin/main:mem0/client/main.py`
- `origin/main:docs/open-source/python-quickstart.mdx`

Public source:

- <https://docs.mem0.ai/open-source/setup>

## How Mem0 Makes Hosted And Local Coherent

Mem0's coherence comes from one conceptual memory API:

```text
add memory
search memories
list memories
update memory
delete memory
entities
events
```

The user can call that memory API through different surfaces:

- Python SDK
- TypeScript SDK
- REST API
- CLI
- hosted MCP
- plugins for agent clients

The underlying deployment differs, but the product verb stays the same:
memory operations over scoped entities such as user, agent, app, and run.

This works because Mem0 does not have a repo-native canonical artifact. Its
canonical state is the memory store. Local and hosted can both pretend to be
"a memory backend" if they expose similar operations.

## CLI Shape

Mem0 has one `mem0` CLI, implemented in both TypeScript and Python from a shared
spec. The docs and local `cli/CLI_SPECIFICATION.md` say both implementations
should have identical commands, options, output modes, and errors.

The CLI is Platform-first. The docs state that it works with the Mem0 Platform
API. Local code names the backend `PlatformBackend`, defaults to
`https://api.mem0.ai`, and uses API paths such as `/v3/memories/add/` and
`/v3/memories/search/`.

The CLI can point somewhere else through `--base-url`, `MEM0_BASE_URL`, or
`platform.base_url` in `~/.mem0/config.json`. That is a compatibility seam, but
it is not the same thing as a first-class local mode. It assumes the target
server speaks the expected API.

This means `mem0 add` is not equivalent to calling the local embedded
`Memory()` engine. It is a CLI over a Mem0 API backend. By default that backend
is hosted. With `MEM0_BASE_URL`, it can be aimed at a compatible self-hosted
server.

`origin/main` now highlights an agent-native hosted signup path:

```text
mem0 init --agent --agent-caller <agent-name>
```

That command mints a Mem0 Platform API key for an agent without requiring an
email, browser, or dashboard first. The human can claim the account later with
email. This is Mem0's cleanest hosted-onboarding move: the agent starts with
hosted memory by default, and human account ownership follows.

Local sources:

- `/Users/rohan/Desktop/Projects/mem0/cli/README.md`
- `/Users/rohan/Desktop/Projects/mem0/cli/CLI_SPECIFICATION.md`
- `/Users/rohan/Desktop/Projects/mem0/cli/node/src/config.ts`
- `/Users/rohan/Desktop/Projects/mem0/cli/node/src/backend/platform.ts`
- `origin/main:README.md`
- `origin/main:docs/platform/cli.mdx`

Public source:

- <https://docs.mem0.ai/platform/cli>
- <https://mem0.ai/blog/the-easiest-way-to-add-persistent-memory-to-any-ai-agent>

## MCP Shape

Mem0's official current MCP path is hosted. The public docs describe a
cloud-hosted MCP server at:

```text
https://mcp.mem0.ai/mcp
```

The archived `mem0ai/mem0-mcp` repository now points users to the cloud-hosted
MCP server. The current `mem0-plugin/.codex-mcp.json` in the main repo also
registers that hosted MCP URL.

OpenMemory was the local MCP path, but the current local `openmemory/README.md`
says OpenMemory is being sunset and points users to the self-hosted Mem0 server
instead. That means the current official direction is not "one local MCP over
the light library"; it is "hosted MCP for Platform, heavy self-hosted server for
local/team control."

Local sources:

- `/Users/rohan/Desktop/Projects/mem0/mem0-plugin/README.md`
- `/Users/rohan/Desktop/Projects/mem0/mem0-plugin/.codex-mcp.json`
- `/Users/rohan/Desktop/Projects/mem0/openmemory/README.md`

Public sources:

- <https://docs.mem0.ai/platform/mem0-mcp>
- <https://github.com/mem0ai/mem0-mcp>

## Self-Hosting Meaning

For Mem0, self-hosting means running the product service stack. It is not just
"use the library locally."

The self-hosted server has its own API paths and auth model. The public REST
API docs warn that self-hosted OSS does not use the hosted `/v1/` prefix in the
same way as the Platform API. This is an important warning: Mem0 has conceptual
coherence, but local/server/platform compatibility is not perfect.

Public source:

- <https://docs.mem0.ai/open-source/features/rest-api>

## Mem0 Lessons For CodeAlmanac

Mem0 has a useful product ladder:

```text
light local library
  -> heavy self-hosted server
  -> managed platform
```

CodeAlmanac currently has:

```text
light local CLI over repo files
  -> proposed hosted control plane
```

The missing middle is an official heavy self-hosted control plane. We should not
add that by accident. It would mean database, API, dashboard, workers, GitHub
webhooks, source ingestion, auth, and delivery policy. That is closer to
Supabase/PostHog than to the current CLI.

The Mem0-style way to stay coherent would be:

```text
same product verbs
same artifact model
explicit execution posture
different infrastructure
```

For CodeAlmanac, the common verbs are likely:

```text
read wiki
collect sources
run update
inspect runs
deliver wiki diff
configure triggers
```

The hard part is that `deliver wiki diff` has no Mem0 equivalent. Mem0 writes
to its memory store. CodeAlmanac writes to Git. That means hosted/local parity
cannot be only "same API base URL." It also needs a delivery policy model.

## Recommendation From This Comparison

Keep CodeAlmanac OSS light unless there is a concrete self-hosted buyer.

Do not copy Mem0's heavy self-hosted path yet. Copy their explicit posture
ladder:

```text
Reader: local repo wiki reads
Local Lab: local compute and local source capture
Hosted: managed triggers, source collection, workers, delivery, team runs
Future Self-Hosted: only if customers need hosted-like control on their infra
```

The CLI should show posture clearly, especially for commands whose execution
changes by posture:

```text
codealmanac status
codealmanac runs --local
codealmanac runs --hosted
codealmanac agents install --mode hosted
codealmanac agents install --mode local
```

The product should avoid pretending that `runs`, `sync`, or `agents install`
are identical in local and hosted mode. They are product-equivalent but not
infrastructure-equivalent.

## Questions To Carry Forward

1. Should CodeAlmanac ever offer a heavy self-hosted control plane, or should
   "self-hosted" mean "run the light CLI/local lab yourself" for now?
2. Should the CLI have a global active posture, or should commands that can hit
   hosted always require `--hosted` until the user runs `connect`?
3. Should hosted source capture use the same hook installer as local lab, with
   a different destination, or a separate install command?
4. Should hosted `runs` and local `runs` be merged in one view, or kept separate
   because their storage and trust boundaries differ?
5. Should the hosted API try to mimic local CLI services, or should both call a
   shared operation/request model below the CLI edge?
