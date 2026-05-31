import { describe, expect, it } from "vitest";

import {
  GitHubSourceError,
  parseGitHubRemote,
  resolveGitHubSource,
  type CommandRunner,
} from "../src/ingest/github.js";
import type { SourceRef } from "../src/ingest/source-ref.js";

const ref: SourceRef = {
  raw: "github:pr:123",
  provider: "github",
  kind: "pr",
  id: "123",
};

const issueUrlRef: SourceRef = {
  raw: "https://github.com/other/project/issues/11",
  provider: "github",
  kind: "issue",
  id: "11",
  repo: {
    owner: "other",
    repo: "project",
  },
};

describe("parseGitHubRemote", () => {
  it("parses HTTPS GitHub remotes", () => {
    expect(parseGitHubRemote("https://github.com/owner/repo.git")).toEqual({
      owner: "owner",
      repo: "repo",
    });
    expect(parseGitHubRemote("https://github.com/owner/repo")).toEqual({
      owner: "owner",
      repo: "repo",
    });
  });

  it("parses SSH GitHub remotes", () => {
    expect(parseGitHubRemote("git@github.com:owner/repo.git")).toEqual({
      owner: "owner",
      repo: "repo",
    });
    expect(parseGitHubRemote("ssh://git@github.com/owner/repo.git")).toEqual({
      owner: "owner",
      repo: "repo",
    });
  });

  it("rejects non-GitHub remotes", () => {
    expect(parseGitHubRemote("https://gitlab.com/owner/repo.git")).toBeNull();
    expect(parseGitHubRemote("not-a-url")).toBeNull();
  });
});

describe("resolveGitHubSource", () => {
  it("uses Error as the base for setup failures", () => {
    expect(new GitHubSourceError("x", "y")).toBeInstanceOf(Error);
  });

  it("builds a GitHub PR source from the current remote", async () => {
    const runCommand = fakeRunner({
      "git remote get-url origin": { stdout: "git@github.com:owner/repo.git\n" },
      "gh --version": { stdout: "gh version 2.0.0\n" },
      "gh auth status": { stdout: "github.com\n" },
    });

    await expect(resolveGitHubSource({ ref, cwd: "/repo", runCommand }))
      .resolves.toEqual({
        kind: "github.pr",
        raw: "github:pr:123",
        repo: "owner/repo",
        url: "https://github.com/owner/repo/pull/123",
        number: "123",
      });
  });

  it("builds a GitHub issue source from a URL repo", async () => {
    const runCommand = fakeRunner({
      "gh --version": { stdout: "gh version 2.0.0\n" },
      "gh auth status": { stdout: "github.com\n" },
    });

    await expect(resolveGitHubSource({ ref: issueUrlRef, cwd: "/repo", runCommand }))
      .resolves.toEqual({
        kind: "github.issue",
        raw: "https://github.com/other/project/issues/11",
        repo: "other/project",
        url: "https://github.com/other/project/issues/11",
        number: "11",
      });
  });

  it("does not require a GitHub remote when a URL contains the repo", async () => {
    const seenCommands: string[] = [];
    const runCommand: CommandRunner = async (command, args) => {
      const key = [command, ...args].join(" ");
      seenCommands.push(key);
      if (key === "gh --version") return { stdout: "gh version 2.0.0\n", stderr: "" };
      if (key === "gh auth status") return { stdout: "github.com\n", stderr: "" };
      throw new Error(`unexpected command: ${key}`);
    };

    await expect(resolveGitHubSource({ ref: issueUrlRef, cwd: "/repo", runCommand }))
      .resolves.toMatchObject({
        kind: "github.issue",
        repo: "other/project",
      });
    expect(seenCommands).not.toContain("git remote get-url origin");
    expect(seenCommands).not.toContain(
      "gh issue view 11 --repo other/project --json title,body,url,author,state,comments,labels,assignees,closedAt",
    );
  });

  it("does not fetch GitHub issue material while resolving identity", async () => {
    const seenCommands: string[] = [];
    const runCommand = fakeRunner({
      "gh --version": { stdout: "gh version 2.0.0\n" },
      "gh auth status": { stdout: "github.com\n" },
    }, seenCommands);

    await expect(resolveGitHubSource({ ref: issueUrlRef, cwd: "/repo", runCommand }))
      .resolves.toMatchObject({
        kind: "github.issue",
        repo: "other/project",
      });
    expect(seenCommands).toEqual(["gh --version", "gh auth status"]);
  });

  it("checks gh before returning URL-resolved issue sources", async () => {
    const runCommand = fakeRunner({
      "git remote get-url origin": { stdout: "git@github.com:owner/repo.git\n" },
      "gh --version": { error: Object.assign(new Error("not found"), { code: "ENOENT" }) },
    });

    await expect(resolveGitHubSource({ ref: issueUrlRef, cwd: "/repo", runCommand }))
      .rejects.toMatchObject({
        message: "GitHub ingest needs the GitHub CLI (`gh`).",
      });
  });

  it("returns a setup error when gh is missing", async () => {
    const runCommand = fakeRunner({
      "git remote get-url origin": { stdout: "https://github.com/owner/repo.git\n" },
      "gh --version": { error: Object.assign(new Error("not found"), { code: "ENOENT" }) },
    });

    await expect(resolveGitHubSource({ ref, cwd: "/repo", runCommand }))
      .rejects.toMatchObject({
        message: "GitHub ingest needs the GitHub CLI (`gh`).",
        fix: [
          "Install and authenticate it:",
          "",
          "  1. Install GitHub CLI:",
          "     https://cli.github.com/",
          "",
          "  2. Sign in:",
          "     gh auth login",
          "",
          "  3. Try again:",
          "     almanac ingest github:pr:123",
        ].join("\n"),
      });
  });

  it("returns an auth error when gh is not authenticated", async () => {
    const runCommand = fakeRunner({
      "git remote get-url origin": { stdout: "https://github.com/owner/repo.git\n" },
      "gh --version": { stdout: "gh version 2.0.0\n" },
      "gh auth status": { error: new Error("not logged in") },
    });

    await expect(resolveGitHubSource({ ref, cwd: "/repo", runCommand }))
      .rejects.toMatchObject({
        message: "GitHub CLI is installed, but not authenticated.",
        fix: [
          "Sign in with:",
          "",
          "  gh auth login",
          "",
          "Then try again:",
          "  almanac ingest github:pr:123",
        ].join("\n"),
      });
  });

  it("returns a clear error for non-GitHub remotes", async () => {
    const runCommand = fakeRunner({
      "git remote get-url origin": { stdout: "https://gitlab.com/owner/repo.git\n" },
    });

    await expect(resolveGitHubSource({ ref, cwd: "/repo", runCommand }))
      .rejects.toMatchObject({
        message: "GitHub source ingest requires a GitHub remote for this repository.",
        fix: [
          "Set an origin remote that points to GitHub, or run this command from a GitHub-backed repo:",
          "",
          "  git remote -v",
        ].join("\n"),
      });
  });

  it("returns a clear error when origin is missing", async () => {
    const runCommand = fakeRunner({
      "git remote get-url origin": { error: new Error("No such remote 'origin'") },
    });

    await expect(resolveGitHubSource({ ref, cwd: "/repo", runCommand }))
      .rejects.toMatchObject({
        message: "GitHub source ingest requires a GitHub remote for this repository.",
        fix: [
          "Set an origin remote that points to GitHub, or run this command from a GitHub-backed repo:",
          "",
          "  git remote -v",
        ].join("\n"),
      });
  });
});

function fakeRunner(
  responses: Record<string, { stdout?: string; stderr?: string; error?: Error }>,
  seenCommands: string[] = [],
): CommandRunner {
  return async (command, args) => {
    const key = [command, ...args].join(" ");
    seenCommands.push(key);
    const response = responses[key];
    if (response === undefined) {
      throw new Error(`unexpected command: ${key}`);
    }
    if (response.error !== undefined) throw response.error;
    return {
      stdout: response.stdout ?? "",
      stderr: response.stderr ?? "",
    };
  };
}
