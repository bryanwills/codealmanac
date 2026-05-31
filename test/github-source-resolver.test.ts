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
    });

    await expect(resolveGitHubSource({
      ref,
      cwd: "/repo",
      runCommand,
      config: githubConfig(),
    }))
      .resolves.toEqual({
        kind: "github.pr",
        raw: "github:pr:123",
        repo: "owner/repo",
        url: "https://github.com/owner/repo/pull/123",
        number: "123",
        connector: {
          provider: "composio",
          toolkit: "github",
          account: "work",
          connectedAccountId: "ca_work",
        },
      });
  });

  it("builds a GitHub issue source from a URL repo", async () => {
    const runCommand = fakeRunner({});

    await expect(resolveGitHubSource({
      ref: issueUrlRef,
      cwd: "/repo",
      runCommand,
      config: githubConfig(),
    }))
      .resolves.toEqual({
        kind: "github.issue",
        raw: "https://github.com/other/project/issues/11",
        repo: "other/project",
        url: "https://github.com/other/project/issues/11",
        number: "11",
        connector: {
          provider: "composio",
          toolkit: "github",
          account: "work",
          connectedAccountId: "ca_work",
        },
      });
  });

  it("does not require a GitHub remote when a URL contains the repo", async () => {
    const seenCommands: string[] = [];
    const runCommand: CommandRunner = async (command, args) => {
      const key = [command, ...args].join(" ");
      seenCommands.push(key);
      throw new Error(`unexpected command: ${key}`);
    };

    await expect(resolveGitHubSource({
      ref: issueUrlRef,
      cwd: "/repo",
      runCommand,
      config: githubConfig(),
    }))
      .resolves.toMatchObject({
        kind: "github.issue",
        repo: "other/project",
      });
    expect(seenCommands).toEqual([]);
  });

  it("does not fetch GitHub issue material or call gh while resolving identity", async () => {
    const seenCommands: string[] = [];
    const runCommand = fakeRunner({}, seenCommands);

    await expect(resolveGitHubSource({
      ref: issueUrlRef,
      cwd: "/repo",
      runCommand,
      config: githubConfig(),
    }))
      .resolves.toMatchObject({
        kind: "github.issue",
        repo: "other/project",
      });
    expect(seenCommands).toEqual([]);
  });

  it("returns a setup error when no GitHub connector account is configured", async () => {
    const runCommand = fakeRunner({
      "git remote get-url origin": { stdout: "https://github.com/owner/repo.git\n" },
    });

    await expect(resolveGitHubSource({
      ref,
      cwd: "/repo",
      runCommand,
      config: githubConfig({ defaultAccount: null }),
    }))
      .rejects.toMatchObject({
        message: "GitHub ingest needs a connected GitHub account.",
        fix: [
          "Connect GitHub through Composio first:",
          "",
          "  almanac connect github",
          "",
          "Then rerun the ingest command.",
        ].join("\n"),
      });
  });

  it("returns a setup error when the requested account is missing", async () => {
    const runCommand = fakeRunner({
      "git remote get-url origin": { stdout: "https://github.com/owner/repo.git\n" },
    });

    await expect(resolveGitHubSource({
      ref,
      cwd: "/repo",
      account: "personal",
      runCommand,
      config: githubConfig(),
    }))
      .rejects.toMatchObject({
        message: "GitHub connector account 'personal' is not configured.",
        fix: [
          "Connect GitHub through Composio:",
          "",
          "  almanac connect github --account personal",
        ].join("\n"),
      });
  });

  it("returns a setup error when the selected account is not active", async () => {
    const runCommand = fakeRunner({
      "git remote get-url origin": { stdout: "https://github.com/owner/repo.git\n" },
    });

    await expect(resolveGitHubSource({
      ref,
      cwd: "/repo",
      runCommand,
      config: githubConfig({ status: "INITIATED" }),
    }))
      .rejects.toMatchObject({
        message: "GitHub connector account 'work' is INITIATED, not ACTIVE.",
        fix: expect.stringContaining("almanac connect github --account work --wait"),
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

function githubConfig(options: {
  defaultAccount?: string | null;
  status?: string | null;
} = {}) {
  return {
    update_notifier: true,
    auto_commit: true,
    agent: {
      default: "codex" as const,
      models: {
        claude: null,
        codex: null,
        cursor: null,
      },
    },
    automation: {
      capture_since: null,
    },
    connectors: {
      composio: {
        api_key_env: "COMPOSIO_API_KEY",
        user_id: "user_123",
      },
      github: {
        default_account: options.defaultAccount === undefined
          ? "work"
          : options.defaultAccount,
        accounts: {
          work: {
            alias: "work",
            connected_account_id: "ca_work",
            status: options.status ?? "ACTIVE",
          },
        },
      },
    },
  };
}

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
