import { execFile } from "node:child_process";
import { promisify } from "node:util";

import type { GitHubSource } from "./source.js";
import type { SourceRef } from "./source-ref.js";
import {
  readConfig,
  type GlobalConfig,
  type GitHubConnectorAccountConfig,
} from "../config/index.js";
import {
  connectorStatusLabel,
  isActiveConnectorAccount,
} from "../connectors/status.js";

const execFileAsync = promisify(execFile);

export interface GitHubRepo {
  owner: string;
  repo: string;
}

export type CommandRunner = (
  command: string,
  args: string[],
  options: { cwd: string },
) => Promise<{ stdout: string; stderr: string }>;

export class GitHubSourceError extends Error {
  constructor(message: string, readonly fix: string) {
    super(message);
  }
}

export async function resolveGitHubSource(args: {
  ref: Extract<SourceRef, { provider: "github" }>;
  cwd: string;
  account?: string;
  runCommand?: CommandRunner;
  config?: GlobalConfig;
}): Promise<GitHubSource> {
  const runCommand = args.runCommand ?? defaultCommandRunner;
  const repo = args.ref.repo ?? await resolveRepoFromRemote(runCommand, args.cwd);
  if (repo === null) throw githubRemoteError();
  const account = selectGitHubAccount(
    args.config ?? await readConfig({ cwd: args.cwd }),
    args.account,
  );

  const repoName = `${repo.owner}/${repo.repo}`;
  const sourceKind = args.ref.kind === "pr" ? "pull" : "issues";
  return {
    kind: args.ref.kind === "pr" ? "github.pr" : "github.issue",
    raw: args.ref.raw,
    repo: repoName,
    url: `https://github.com/${repoName}/${sourceKind}/${args.ref.id}`,
    number: args.ref.id,
    connector: {
      provider: "composio",
      toolkit: "github",
      account: account.alias,
      connectedAccountId: account.connected_account_id,
    },
  };
}

export function parseGitHubRemote(remote: string): GitHubRepo | null {
  const normalized = remote.trim();
  const sshMatch = normalized.match(/^git@github\.com:([^/]+)\/(.+?)(?:\.git)?$/);
  if (sshMatch !== null) return repoFromMatch(sshMatch[1], sshMatch[2]);

  try {
    const url = new URL(normalized);
    if (url.hostname !== "github.com") return null;
    const bits = url.pathname.replace(/^\/+/, "").split("/");
    if (bits.length < 2) return null;
    return repoFromMatch(bits[0], bits[1]);
  } catch {
    return null;
  }
}

async function defaultCommandRunner(
  command: string,
  args: string[],
  options: { cwd: string },
): Promise<{ stdout: string; stderr: string }> {
  const result = await execFileAsync(command, args, {
    cwd: options.cwd,
    encoding: "utf8",
  });
  return {
    stdout: result.stdout,
    stderr: result.stderr,
  };
}

function repoFromMatch(owner: string | undefined, rawRepo: string | undefined): GitHubRepo | null {
  if (owner === undefined || rawRepo === undefined) return null;
  const repo = rawRepo.replace(/\.git$/, "");
  if (!isSafeGitHubPart(owner) || !isSafeGitHubPart(repo)) return null;
  return { owner, repo };
}

async function resolveRepoFromRemote(
  runCommand: CommandRunner,
  cwd: string,
): Promise<GitHubRepo | null> {
  try {
    const remote = await runCommand("git", ["remote", "get-url", "origin"], {
      cwd,
    });
    return parseGitHubRemote(remote.stdout.trim());
  } catch {
    return null;
  }
}

function isSafeGitHubPart(part: string): boolean {
  return /^[A-Za-z0-9_.-]+$/.test(part);
}

function selectGitHubAccount(
  config: GlobalConfig,
  requestedAccount: string | undefined,
): GitHubConnectorAccountConfig {
  const alias = requestedAccount ?? config.connectors.github.default_account;
  if (alias === null) throw githubConnectionError();
  const account = config.connectors.github.accounts[alias];
  if (account === undefined) {
    throw new GitHubSourceError(
      `GitHub connector account '${alias}' is not configured.`,
      [
        "Connect GitHub through Composio:",
        "",
        `  almanac connect github --account ${alias}`,
      ].join("\n"),
    );
  }
  if (!isActiveConnectorAccount(account)) {
    throw new GitHubSourceError(
      `GitHub connector account '${alias}' is ${connectorStatusLabel(account.status)}, not ACTIVE.`,
      [
        "Finish connecting GitHub through Composio before ingesting this source:",
        "",
        `  almanac connect github --account ${alias} --wait`,
        "",
        "Or inspect connection state:",
        "",
        "  almanac connect github --status",
      ].join("\n"),
    );
  }
  return account;
}

function githubConnectionError(): GitHubSourceError {
  return new GitHubSourceError(
    "GitHub ingest needs a connected GitHub account.",
    [
      "Connect GitHub through Composio first:",
      "",
      "  almanac connect github",
      "",
      "Then rerun the ingest command.",
    ].join("\n"),
  );
}

function githubRemoteError(): GitHubSourceError {
  return new GitHubSourceError(
    "GitHub source ingest requires a GitHub remote for this repository.",
    [
      "Set an origin remote that points to GitHub, or run this command from a GitHub-backed repo:",
      "",
      "  git remote -v",
    ].join("\n"),
  );
}
