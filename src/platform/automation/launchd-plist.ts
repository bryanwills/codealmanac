export interface LaunchdPlistDefinition {
  label: string;
  programArguments: string[];
  intervalSeconds: number;
  environmentVariables: Record<string, string>;
  stdoutPath: string;
  stderrPath: string;
  workingDirectory?: string;
}

export function renderLaunchdPlist(args: LaunchdPlistDefinition): string {
  const programArguments = args.programArguments
    .map((arg) => `    <string>${escapeXml(arg)}</string>`)
    .join("\n");
  const environmentVariables = Object.entries(args.environmentVariables)
    .map(
      ([key, value]) =>
        `    <key>${escapeXml(key)}</key>\n    <string>${escapeXml(value)}</string>`,
    )
    .join("\n");
  return `<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>${escapeXml(args.label)}</string>
  <key>ProgramArguments</key>
  <array>
${programArguments}
  </array>
  <key>StartInterval</key>
  <integer>${args.intervalSeconds}</integer>
${args.workingDirectory !== undefined
    ? `  <key>WorkingDirectory</key>\n  <string>${escapeXml(args.workingDirectory)}</string>\n`
    : ""}  <key>EnvironmentVariables</key>
  <dict>
${environmentVariables}
  </dict>
  <key>RunAtLoad</key>
  <true/>
  <key>StandardOutPath</key>
  <string>${escapeXml(args.stdoutPath)}</string>
  <key>StandardErrorPath</key>
  <string>${escapeXml(args.stderrPath)}</string>
</dict>
</plist>
`;
}

export function readLaunchdStartInterval(contents: string): number | null {
  const value = contents.match(
    /<key>StartInterval<\/key>\s*<integer>(\d+)<\/integer>/,
  )?.[1];
  return value === undefined ? null : Number(value);
}

export function readLaunchdProgramArguments(contents: string): string[] {
  return [...contents.matchAll(/<string>([^<]*)<\/string>/g)]
    .map((match) => unescapeXml(match[1] ?? ""));
}

function escapeXml(value: string): string {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&apos;");
}

function unescapeXml(value: string): string {
  return value
    .replaceAll("&apos;", "'")
    .replaceAll("&quot;", '"')
    .replaceAll("&gt;", ">")
    .replaceAll("&lt;", "<")
    .replaceAll("&amp;", "&");
}
