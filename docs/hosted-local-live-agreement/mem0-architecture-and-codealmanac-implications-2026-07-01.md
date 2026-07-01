# Mem0 Architecture And CodeAlmanac Interface Implications

Date: 2026-07-01.
Mem0 repo inspected: `/Users/rohan/Desktop/Projects/mem0`, `origin/main`
at `c325bd3b`.

## Mem0 Product Split

Mem0 has four distinct surfaces:

| Surface | Main object | Deployment | User-facing shape |
| --- | --- | --- | --- |
| OSS embedded SDK | `Memory()` | in-process library | app imports memory engine directly |
| Hosted SDK/API | `MemoryClient` | Mem0 Platform | HTTP client to `api.mem0.ai` |
| CLI | `mem0` | Mem0 Platform backend | terminal client over hosted API paths |
| Self-hosted server | REST API + dashboard | Docker stack | API server, dashboard, auth, request logs |

The CLI is not the embedded local memory engine. The CLI backend class is named
`PlatformBackend` and calls hosted-style endpoints such as
`/v3/memories/add/` and `/v3/memories/search/`.

## OSS Memory Engine

`Memory()` is the open-source engine. It is initialized from `MemoryConfig`,
which owns the LLM, embedder, vector store, history DB path, optional reranker,
version, and custom extraction instructions.

Default local storage:

- memory vectors in local Qdrant at `/tmp/qdrant`
- history and recent messages in SQLite at `~/.mem0/history.db`
- extracted entities in a second entity collection in the same vector-store
  family

The `add()` path:

1. Validates one of `user_id`, `agent_id`, or `run_id`.
2. Normalizes messages.
3. Gets recent messages from SQLite for the session scope.
4. Embeds the new message text as a retrieval query.
5. Retrieves nearby existing memories from the vector store.
6. Calls the LLM once with an additive extraction prompt.
7. Parses extracted memory records from JSON.
8. Embeds extracted memory texts.
9. Deduplicates by hash against existing and current-batch memories.
10. Inserts memory vectors and payloads into the vector store.
11. Writes memory history rows to SQLite.
12. Extracts entities, embeds them, and links entity records to memory IDs.
13. Saves recent messages to SQLite.

The current v3 extraction is additive. It adds new memory records and relies on
deduplication/entity linking rather than an old propose-update-delete graph
store workflow.

The `search()` path:

1. Validates filters and query.
2. Lemmatizes the query for BM25/keyword search.
3. Extracts query entities.
4. Embeds the query.
5. Runs semantic vector search.
6. Runs keyword search if the vector store supports it.
7. Computes entity boosts by searching the entity store and boosting linked
   memory IDs.
8. Combines semantic score, normalized BM25 score, and entity boost.
9. Returns memory records with one combined score.

## Graph Meaning

Mem0 no longer requires an external graph database for current graph memory.
The old graph-store integration was removed. Current graph memory is entity
linking:

```text
memory text
  -> extracted entities
  -> entity records
  -> linked_memory_ids
  -> retrieval boost
```

The platform docs call this "native Graph Memory." It is a graph in product
semantics, but not necessarily a Neo4j-style graph database in OSS. It is built
from entity records and memory links.

## Self-Hosted Meaning

Self-hosting Mem0 is not just using `Memory()` locally.

The current self-hosted server includes:

- FastAPI server
- Next.js dashboard
- Postgres with pgvector
- auth tables
- per-user API keys
- request logs
- settings/config override table
- dashboard pages for requests, memories, entities, API keys, configuration,
  settings, and other platform-like surfaces

The self-hosted REST server uses `server_state.py` to create a `Memory` engine
with `Memory.from_config(...)`. The server wraps the engine with auth,
request logging, dashboard support, and REST endpoints.

The OSS REST API paths are not identical to hosted Platform API paths. The OSS
docs say self-hosted uses paths such as `POST /memories` and `POST /search`;
the hosted CLI and hosted client use paths such as `/v3/memories/add/`.

## Platform Difference

The hosted platform sells managed infrastructure and additional product
features:

- no infrastructure setup
- managed scaling/high availability
- hosted dashboard and analytics
- hosted MCP server
- webhooks
- memory export
- custom categories and other advanced features
- graph view gated by plan

The open repo contains the core memory engine, many SDK/client surfaces, the
self-hosted server, and the self-hosted dashboard. It does not contain the
production hosted platform backend or the implementation of
`https://mcp.mem0.ai/mcp`.

## CodeAlmanac Implication

CodeAlmanac is not currently shaped like Mem0.

Mem0 can split `Memory()` and `MemoryClient` because its core product is an
engine that can be embedded or exposed over HTTP. The CLI is a platform client,
not the local engine.

CodeAlmanac's current product is the CLI itself. It initializes, reads, writes,
indexes, runs capture/automation, and owns the local workflow. That makes a
hosted product harder to blend in without producing two execution paths.

The cleanest long-term shape is:

```text
core engine / services
  used by:
    CLI adapter
    hosted API adapter
    future self-hosted server adapter
    optional MCP adapter
```

The CLI should remain the primary local UX, but it should stop being the only
conceptual API. Internally, commands should map to service requests that can
also be called by hosted/server entry points.

For hosted/local coherence, there are three serious options:

1. **Light OSS, hosted automation.** Keep local CLI for repo-local reading and
   manual/lab updates. Hosted owns team automation. Lowest OSS friction, but
   two execution paths.
2. **Self-hosted control plane.** Build an OSS server/dashboard/worker stack
   that hosted also runs. Highest coherence, highest setup cost.
3. **Core engine plus CLI and hosted API adapters.** Keep OSS light now, but
   make all write/update verbs service-level operations rather than CLI-only
   flows. This preserves the option to add self-hosted later.

The near-term recommendation is option 3. It does not require a heavy
self-hosted product now, but it prevents the CLI from becoming a dead-end
surface that hosted must reimplement.

