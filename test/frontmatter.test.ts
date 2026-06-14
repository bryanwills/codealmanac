import { describe, expect, it } from "vitest";

import { firstH1, parseFrontmatter } from "../src/wiki/indexer/frontmatter.js";

describe("parseFrontmatter", () => {
  it("parses a normal frontmatter block", () => {
    const fm = parseFrontmatter(
      `---
title: Checkout Flow
description: Checkout decisions and invariants for future agents.
topics: [checkout, flows]
sources:
  - id: checkout-handler
    type: file
    path: src/checkout/handler.ts
---

# Checkout Flow

Body goes here.
`,
    );
    expect(fm.title).toBe("Checkout Flow");
    expect(fm.description).toBe("Checkout decisions and invariants for future agents.");
    expect(fm.topics).toEqual(["checkout", "flows"]);
    expect(fm.sources).toEqual([
      {
        id: "checkout-handler",
        type: "file",
        path: "src/checkout/handler.ts",
      },
    ]);
    expect(fm.body).toMatch(/^# Checkout Flow/m);
  });

  it("falls back to legacy summary frontmatter as a description", () => {
    const fm = parseFrontmatter(
      `---
title: Legacy Page
summary: Legacy page preview.
---

Body.
`,
    );

    expect(fm.description).toBe("Legacy page preview.");
  });

  it("returns empty fields when frontmatter is absent", () => {
    const fm = parseFrontmatter("# Just a heading\n\nNo frontmatter.\n");
    expect(fm.topics).toEqual([]);
    expect(fm.sources).toEqual([]);
    expect(fm.title).toBeUndefined();
    expect(fm.body).toMatch(/^# Just a heading/);
  });

  it("parses structured sources and ignores source strings", () => {
    const fm = parseFrontmatter(
      `---
title: Absorb
sources:
  - id: absorb-command
    type: file
    path: src/cli/commands/operations.ts
    note: Starts absorb.
  - id: sdk-docs
    type: web
    url: https://example.com/docs
    title: SDK Docs
    retrieved_at: 2026-05-28
    note: External behavior.
  - id: bug-report
    type: issue
    number: 42
    note: User-reported regression.
  - https://legacy.example.com/docs
---

Body.
`,
    );

    expect(fm.sources).toEqual([
      {
        id: "absorb-command",
        type: "file",
        path: "src/cli/commands/operations.ts",
        note: "Starts absorb.",
      },
      {
        id: "sdk-docs",
        type: "web",
        url: "https://example.com/docs",
        title: "SDK Docs",
        retrieved_at: "2026-05-28",
        note: "External behavior.",
      },
      {
        id: "bug-report",
        type: "issue",
        number: "42",
        note: "User-reported regression.",
      },
    ]);
  });

  it("ignores malformed structured sources", () => {
    const fm = parseFrontmatter(
      `---
sources:
  - type: file
    path: src/no-id.ts
  - id: no-path
    type: file
  - id: manual
    type: manual
    note: Human-provided evidence.
---

Body.
`,
    );

    expect(fm.sources).toEqual([
      {
        id: "manual",
        type: "manual",
        note: "Human-provided evidence.",
      },
    ]);
  });

  it("tolerates extra frontmatter fields", () => {
    const fm = parseFrontmatter(
      `---
title: x
topics: [a]
some_future_field: 42
arbitrary:
  nested: value
---

body
`,
    );
    expect(fm.title).toBe("x");
    expect(fm.topics).toEqual(["a"]);
  });

  it("recovers from malformed YAML by returning empty fields", () => {
    // parseFrontmatter writes a warning to stderr on bad YAML. Suppress
    // it for the duration of this test so the test output stays clean.
    const origWrite = process.stderr.write.bind(process.stderr);
    process.stderr.write = ((): boolean => true) as typeof process.stderr.write;
    try {
      const fm = parseFrontmatter(
        `---
title: x
topics: [unclosed
---

body
`,
      );
      // Malformed — we can't extract fields, but the page is still indexable.
      expect(fm.topics).toEqual([]);
    } finally {
      process.stderr.write = origWrite;
    }
  });

  it("ignores a --- that isn't on line 1", () => {
    const fm = parseFrontmatter("# Heading\n\n---\n\nSection break.\n");
    expect(fm.topics).toEqual([]);
    expect(fm.body).toMatch(/Section break/);
  });
});

describe("firstH1", () => {
  it("returns the first H1", () => {
    expect(firstH1("# Hello\n\nbody")).toBe("Hello");
  });

  it("returns undefined when there is no H1", () => {
    expect(firstH1("## Only H2 here")).toBeUndefined();
  });

  it("strips trailing hashes and whitespace", () => {
    expect(firstH1("#   Title   ##")).toBe("Title");
  });
});
