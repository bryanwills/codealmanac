export type AbsorbInputSource = GitHubAbsorbInputSource | WebAbsorbInputSource;

export interface GitHubAbsorbInputSource {
  kind: "github.pr" | "github.issue";
  raw: string;
  repo: string;
  url: string;
  number: string;
}

export interface WebAbsorbInputSource {
  kind: "web.url";
  raw: string;
  url: string;
}
