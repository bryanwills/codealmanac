export type IngestSource = GitHubIngestSource | WebIngestSource;

export interface GitHubIngestSource {
  kind: "github.pr" | "github.issue";
  raw: string;
  repo: string;
  url: string;
  number: string;
}

export interface WebIngestSource {
  kind: "web.url";
  raw: string;
  url: string;
}
