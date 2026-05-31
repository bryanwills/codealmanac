import { join } from "node:path";

import { describe, expect, it } from "vitest";

import { renderIngestContext } from "../src/ingest/context.js";
import { resolveIngestInput, type ResolveSourceFn } from "../src/ingest/input.js";

describe("resolveIngestInput", () => {
  it("resolves local paths to operation targets", async () => {
    await expect(resolveIngestInput({
      cwd: "/repo",
      inputs: ["notes.md", "docs"],
    })).resolves.toEqual({
      ok: true,
      value: {
        kind: "path",
        targets: [join("/repo", "notes.md"), join("/repo", "docs")],
        paths: [join("/repo", "notes.md"), join("/repo", "docs")],
      },
    });
  });

  it("resolves source refs through the source resolver", async () => {
    await expect(resolveIngestInput({
      cwd: "/repo",
      inputs: ["github:pr:123"],
      resolveSource: async (ref) => ({
        kind: "github.pr",
        raw: ref.raw,
        repo: "owner/repo",
        url: "https://github.com/owner/repo/pull/123",
        number: "123",
        connector: githubConnector(),
      }),
    })).resolves.toEqual({
      ok: true,
      value: {
        kind: "source",
        targets: ["github:pr:123"],
        sources: [
          {
            kind: "github.pr",
            raw: "github:pr:123",
            repo: "owner/repo",
            url: "https://github.com/owner/repo/pull/123",
            number: "123",
            connector: githubConnector(),
          },
        ],
      },
    });
  });

  it("parses GitHub issue URLs as source refs", async () => {
    await expect(resolveIngestInput({
      cwd: "/repo",
      inputs: ["https://github.com/owner/repo/issues/11"],
      resolveSource: async (ref) => ({
        kind: "github.issue",
        ...githubIssueFacts(ref),
      }),
    })).resolves.toEqual({
      ok: true,
      value: {
        kind: "source",
        targets: ["https://github.com/owner/repo/issues/11"],
        sources: [
          {
            kind: "github.issue",
            raw: "https://github.com/owner/repo/issues/11",
            repo: "owner/repo",
            url: "https://github.com/owner/repo/issues/11",
            number: "11",
            connector: githubConnector(),
          },
        ],
      },
    });
  });

  it("passes arbitrary web URLs through as web sources", async () => {
    await expect(resolveIngestInput({
      cwd: "/repo",
      inputs: ["https://example.com/some/spec"],
    })).resolves.toEqual({
      ok: true,
      value: {
        kind: "source",
        targets: ["https://example.com/some/spec"],
        sources: [
          {
            kind: "web.url",
            raw: "https://example.com/some/spec",
            url: "https://example.com/some/spec",
          },
        ],
      },
    });
  });

  it("rejects mixed source refs and paths", async () => {
    await expect(resolveIngestInput({
      cwd: "/repo",
      inputs: ["github:pr:123", "notes.md"],
    })).resolves.toEqual({
      ok: false,
      message:
        "ingest cannot mix source refs and local paths yet; run separate ingest commands",
    });
  });
});

function githubIssueFacts(ref: Parameters<ResolveSourceFn>[0]) {
  if (ref.provider !== "github") throw new Error("expected GitHub source ref");
  return {
    raw: ref.raw,
    repo: `${ref.repo?.owner}/${ref.repo?.repo}`,
    url: `https://github.com/${ref.repo?.owner}/${ref.repo?.repo}/issues/${ref.id}`,
    number: ref.id,
    connector: githubConnector(),
  };
}

describe("renderIngestContext", () => {
  it("renders GitHub PR source guidance from resolved source facts", () => {
    const context = renderIngestContext({
      kind: "source",
      targets: ["github:pr:123"],
      sources: [
        {
          kind: "github.pr",
          raw: "github:pr:123",
          repo: "owner/repo",
          url: "https://github.com/owner/repo/pull/123",
          number: "123",
          connector: githubConnector(),
        },
      ],
    });

    expect(context).toContain("Input source: github:pr:123");
    expect(context).toContain("Source kind: GitHub pull request");
    expect(context).toContain("Repository: owner/repo");
    expect(context).toContain("Number: 123");
    expect(context).toContain("Connector: Composio github toolkit");
    expect(context).toContain("Account: work");
    expect(context).not.toContain("Resolved GitHub PR source material:");
    expect(context).not.toContain("gh pr view");
    expect(context).toContain("Use the agent source command");
    expect(context).toContain(
      "almanac source github pr 123 --repo owner/repo --account work",
    );
    expect(context).toContain("type: pr");
  });

  it("renders GitHub issue and generic web URL source guidance", () => {
    const context = renderIngestContext({
      kind: "source",
      targets: [
        "https://github.com/owner/repo/issues/11",
        "https://example.com/spec",
      ],
      sources: [
        {
          kind: "github.issue",
          raw: "https://github.com/owner/repo/issues/11",
          repo: "owner/repo",
          url: "https://github.com/owner/repo/issues/11",
          number: "11",
          connector: githubConnector(),
        },
        {
          kind: "web.url",
          raw: "https://example.com/spec",
          url: "https://example.com/spec",
        },
      ],
    });

    expect(context).toContain("Source kind: GitHub issue");
    expect(context).toContain("Number: 11");
    expect(context).toContain("Connector: Composio github toolkit");
    expect(context).toContain("Account: work");
    expect(context).not.toContain("Resolved GitHub issue source material:");
    expect(context).not.toContain("gh issue view");
    expect(context).toContain("Use the agent source command");
    expect(context).toContain(
      "almanac source github issue 11 --repo owner/repo --account work",
    );
    expect(context).toContain("type: web");
    expect(context).toContain("Source kind: web URL");
    expect(context).toContain("URL: https://example.com/spec");
    expect(context).toContain("type: web");
  });
});

function githubConnector() {
  return {
    provider: "composio" as const,
    toolkit: "github" as const,
    account: "work",
    connectedAccountId: "ca_work",
  };
}
