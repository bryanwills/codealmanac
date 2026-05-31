import { execFile } from "node:child_process";
import { promisify } from "node:util";

import type { GitHubSource } from "./source.js";
import type { SourceRef } from "./source-ref.js";

const execFileAsync = promisify(execFile);
const GITHUB_SOURCE_MATERIAL_LIMIT = 60_000;

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
  runCommand?: CommandRunner;
}): Promise<GitHubSource> {
  const runCommand = args.runCommand ?? defaultCommandRunner;
  const repo = args.ref.repo ?? await resolveRepoFromRemote(runCommand, args.cwd);
  if (repo === null) throw githubRemoteError();

  try {
    await runCommand("gh", ["--version"], { cwd: args.cwd });
  } catch {
    throw ghMissingError(args.ref.raw);
  }

  try {
    await runCommand("gh", ["auth", "status"], { cwd: args.cwd });
  } catch {
    throw ghAuthError(args.ref.raw);
  }

  const repoName = `${repo.owner}/${repo.repo}`;
  const sourceKind = args.ref.kind === "pr" ? "pull" : "issues";
  const material = await fetchGitHubMaterial({
    kind: args.ref.kind,
    number: args.ref.id,
    repo: repoName,
    cwd: args.cwd,
    runCommand,
  });
  return {
    kind: args.ref.kind === "pr" ? "github.pr" : "github.issue",
    raw: args.ref.raw,
    repo: repoName,
    url: `https://github.com/${repoName}/${sourceKind}/${args.ref.id}`,
    number: args.ref.id,
    material,
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
    maxBuffer: GITHUB_SOURCE_MATERIAL_LIMIT * 2,
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

async function fetchGitHubMaterial(args: {
  kind: "pr" | "issue";
  number: string;
  repo: string;
  cwd: string;
  runCommand: CommandRunner;
}): Promise<string | undefined> {
  const commandArgs =
    args.kind === "pr"
      ? [
          "pr",
          "view",
          args.number,
          "--repo",
          args.repo,
          "--json",
          "title,body,url,author,baseRefName,headRefName,mergedAt,files,reviews,comments,closingIssuesReferences",
        ]
      : [
          "issue",
          "view",
          args.number,
          "--repo",
          args.repo,
          "--json",
          "title,body,url,author,state,comments,labels,assignees,closedAt",
        ];

  try {
    const result = await args.runCommand("gh", commandArgs, { cwd: args.cwd });
    return truncateMaterial(result.stdout.trim());
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    throw new GitHubSourceError(
      `Could not fetch GitHub ${args.kind === "pr" ? "PR" : "issue"} #${args.number}.`,
      [
        "Check that GitHub CLI can read this source:",
        "",
        `  gh ${args.kind === "pr" ? "pr" : "issue"} view ${args.number} --repo ${args.repo}`,
        "",
        `Underlying error: ${message}`,
      ].join("\n"),
    );
  }
}

function truncateMaterial(material: string): string | undefined {
  if (material.length === 0) return undefined;
  if (material.length <= GITHUB_SOURCE_MATERIAL_LIMIT) return material;
  return `${material.slice(0, GITHUB_SOURCE_MATERIAL_LIMIT)}\n\n[GitHub source material truncated at ${GITHUB_SOURCE_MATERIAL_LIMIT} characters. Use gh for follow-up.]`;
}

function ghMissingError(ref: string): GitHubSourceError {
  return new GitHubSourceError(
    "GitHub ingest needs the GitHub CLI (`gh`).",
    [
      "Install and authenticate it:",
      "",
      "  1. Install GitHub CLI:",
      "     https://cli.github.com/",
      "",
      "  2. Sign in:",
      "     gh auth login",
      "",
      "  3. Try again:",
      `     almanac ingest ${ref}`,
    ].join("\n"),
  );
}

function ghAuthError(ref: string): GitHubSourceError {
  return new GitHubSourceError(
    "GitHub CLI is installed, but not authenticated.",
    [
      "Sign in with:",
      "",
      "  gh auth login",
      "",
      "Then try again:",
      `  almanac ingest ${ref}`,
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
