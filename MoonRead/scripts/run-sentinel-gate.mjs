import { spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptRoot = path.dirname(fileURLToPath(import.meta.url));
const appRoot = path.resolve(scriptRoot, "..");
const workspaceRoot = path.resolve(appRoot, "..");
const sentinelScript = path.join(workspaceRoot, "Deep Sea Embers", "scripts", "sentinel_quality_report.py");

if (!fs.existsSync(sentinelScript)) {
  console.error(`Sentinel script not found: ${sentinelScript}`);
  process.exit(1);
}

const failOn = process.env.SENTINEL_FAIL_ON || "major";
const scope = process.env.SENTINEL_SCOPE || "moonread-generated";
const chapters = process.env.SENTINEL_CHAPTERS;
const novel = process.env.SENTINEL_NOVEL;

const args = [
  sentinelScript,
  "--scope",
  scope,
  "--fail-on",
  failOn,
  "--skip-advisory-english",
];
if (chapters) {
  args.push("--chapters", chapters);
}
if (novel) {
  args.push("--novel", novel);
}

const candidates = [];
if (process.env.PYTHON) {
  candidates.push({ command: process.env.PYTHON, args });
}
candidates.push({ command: "python", args });
candidates.push({ command: "py", args: ["-3", ...args] });

let lastError = "";
for (const candidate of candidates) {
  const result = spawnSync(candidate.command, candidate.args, {
    cwd: workspaceRoot,
    encoding: "utf8",
    stdio: ["ignore", "pipe", "pipe"],
    windowsHide: true,
  });
  if (result.error) {
    lastError = `${candidate.command}: ${result.error.message}`;
    continue;
  }
  if (result.stdout) {
    process.stdout.write(result.stdout);
  }
  if (result.stderr) {
    process.stderr.write(result.stderr);
  }
  process.exit(result.status ?? 1);
}

console.error(`Unable to run Sentinel gate. Last error: ${lastError || "no Python launcher found"}`);
process.exit(1);
