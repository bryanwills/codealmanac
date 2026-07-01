# Firecrawl Local, Self-Hosted, And Hosted Comparison

Date: 2026-06-30.
Repos inspected:

- `https://github.com/firecrawl/firecrawl`
- `https://github.com/firecrawl/cli`
- `https://github.com/firecrawl/firecrawl-mcp-server`

This note compares Firecrawl's OSS, hosted, CLI, and MCP shape as another
model for CodeAlmanac's local/hosted decision.

## Product Shape

Firecrawl's core product is an API for live web context:

```text
search
scrape
interact
crawl
map
agent
parse / extract
monitor
```

The website and GitHub README both frame Firecrawl as an API first. The hosted
quickstart starts with an API key and requests to `https://api.firecrawl.dev`.

## Hosted Versus Open Source

Firecrawl's OSS path is not a lightweight local library in the same way
CodeAlmanac currently is. It is a self-hostable backend service.

The self-hosted guide asks the user to run Docker Compose. The compose stack
includes:

- API container
- Playwright service
- Redis
- RabbitMQ
- Postgres-backed queue service
- optional FoundationDB queue backend
- queue admin UI
- optional OpenAI/Ollama/proxy/SearXNG/Supabase settings

Self-hosted means "run the product infrastructure yourself." It does not mean
"install a CLI and use local files with no service."

Firecrawl also states a product gap between self-hosted and hosted:
self-hosted does not get Fire-engine, the proprietary infrastructure for IP
blocks, robot detection, proxies, rendering, and related reliability work.

## CLI Shape

The Firecrawl CLI is a client to a Firecrawl API backend.

Default:

```text
https://api.firecrawl.dev
```

Self-hosted/local:

```bash
firecrawl --api-url http://localhost:3002 scrape https://example.com
export FIRECRAWL_API_URL=http://localhost:3002
firecrawl scrape https://example.com
```

The CLI skips authentication automatically when `--api-url` points somewhere
other than the default cloud URL. That makes the same CLI usable against hosted
and self-hosted, but only because both are API servers with similar endpoint
shape.

## MCP Shape

Firecrawl has both hosted and local MCP entry points.

Hosted MCP:

```text
https://mcp.firecrawl.dev/v2/mcp
```

Local MCP:

```bash
env FIRECRAWL_API_KEY=fc-YOUR_API_KEY npx -y firecrawl-mcp
```

Self-hosted MCP:

```bash
export FIRECRAWL_API_URL=https://firecrawl.your-domain.com
export FIRECRAWL_API_KEY=...
npx -y firecrawl-mcp
```

The MCP server is still a client. It forwards tool calls to the configured
Firecrawl API URL.

## How Firecrawl Maintains Coherence

Firecrawl keeps one stable client contract:

```text
client / CLI / MCP
  -> Firecrawl API URL
  -> hosted or self-hosted backend
```

That works because the OSS product is the backend API server. The hosted
product is the same product category, operated by Firecrawl and enhanced with
proprietary infra.

The maintenance burden is still real, but it is a familiar one:

```text
shared API contract
shared SDK / CLI / MCP clients
two backend deployments:
  hosted production
  self-hosted OSS stack
```

Firecrawl does not have a separate "light local CLI product" that behaves
fundamentally differently from hosted. Its CLI is not the product engine. Its
CLI is a client.

## Lesson For CodeAlmanac

If CodeAlmanac copies Firecrawl, the OSS artifact would become a self-hosted
control plane:

```text
API server
database
workers
GitHub app / webhook handling
source storage
conversation capture
run ledger
dashboard
delivery policy
```

Then the CLI can be mostly a client:

```text
codealmanac runs
  -> local/self-hosted API URL
  -> hosted API URL
```

That makes hosted and OSS more coherent for maintainers, but it makes OSS much
heavier for users.

The current CodeAlmanac OSS product is different:

```text
install CLI
read/write repo-local wiki files
use local SQLite/index/runtime state
no API server required
no database service required
no account required
```

This is why "local lab plus hosted" feels like two products: it keeps the light
local CLI while adding a hosted control plane. Firecrawl avoids that split by
making OSS itself control-plane-shaped.

## Current Interpretation

There are three coherent options for CodeAlmanac:

1. Keep OSS light and accept that hosted automation is a different execution
   posture.
2. Make OSS heavy/self-hosted so hosted and OSS share the same backend shape.
3. Keep OSS light for read/manual workflows, but make automated writes hosted
   only until there is demand for self-hosting.

Option 2 is easier for product coherence and maintenance. Option 1 is easier
for adoption. Option 3 is the smallest honest paid-product boundary.

