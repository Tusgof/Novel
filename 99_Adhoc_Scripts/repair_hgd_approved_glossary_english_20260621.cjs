const fs = require("fs");
const path = require("path");

const ROOT = "D:\\Fogust\\Workspace\\Novel";
const HGD = path.join(ROOT, "Horror Game Developers");
const GLOSSARY = path.join(HGD, "01_Glossary");

function walk(dir, predicate, out = []) {
  if (!fs.existsSync(dir)) return out;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(full, predicate, out);
    else if (predicate(full)) out.push(full);
  }
  return out;
}

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function parseFrontmatter(text) {
  text = text.replace(/^\uFEFF/, "");
  const match = text.match(/^---\r?\n([\s\S]*?)\r?\n---/);
  if (!match) return {};
  const result = {};
  for (const line of match[1].split(/\r?\n/)) {
    const colon = line.indexOf(":");
    if (colon < 0) continue;
    const key = line.slice(0, colon).trim();
    const value = line.slice(colon + 1).trim();
    result[key] = value;
  }
  return result;
}

function cleanScalar(value) {
  return String(value || "")
    .trim()
    .replace(/^['"]|['"]$/g, "")
    .trim();
}

function parseAliases(raw) {
  if (!raw || raw === "[]") return [];
  const bracket = raw.match(/^\[(.*)\]$/);
  if (!bracket) return [];
  return bracket[1]
    .split(",")
    .map((part) => cleanScalar(part))
    .filter(Boolean);
}

function usableThaiTerm(value) {
  const thai = cleanScalar(value);
  if (!thai || thai.includes("?")) return "";
  if (!/[ก-๙]/.test(thai)) return "";
  return thai;
}

function loadTerms() {
  const terms = [];
  for (const file of walk(GLOSSARY, (target) => target.endsWith(".md"))) {
    const frontmatter = parseFrontmatter(fs.readFileSync(file, "utf8"));
    if (frontmatter.status !== "approved") continue;
    const thai = usableThaiTerm(frontmatter.thai_term);
    if (!thai) continue;
    const originals = [cleanScalar(frontmatter.original_term), ...parseAliases(frontmatter.aliases)]
      .filter(Boolean)
      .filter((term) => term !== thai)
      .filter((term) => /[A-Za-z]/.test(term))
      .filter((term) => !thai.includes(term));
    for (const term of originals) {
      terms.push({ term, thai, source: path.basename(file) });
    }
  }
  const seen = new Set();
  return terms
    .sort((a, b) => b.term.length - a.term.length)
    .filter(({ term, thai }) => {
      const key = `${term}\u0000${thai}`;
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
}

function repairText(text, terms) {
  let next = text;
  const hits = [];
  for (const { term, thai, source } of terms) {
    const escaped = escapeRegExp(term);
    const before = next;

    next = next.replace(new RegExp(`\\(${escaped}\\)`, "g"), "");
    next = next.replace(new RegExp(`\\s*\\(${escaped}\\)\\]`, "g"), "]");
    next = next.replace(new RegExp(`\\s*\\(${escaped}\\]`, "g"), "]");
    next = next.replace(new RegExp(`\\[${escaped}\\]`, "g"), `[${thai}]`);
    next = next.replace(new RegExp(`\\*\\*\\[${escaped}\\]\\*\\*`, "g"), `**[${thai}]**`);

    // UI/list labels often appear as a bare approved term on its own line.
    next = next.replace(new RegExp(`(^|\\n)(${escaped})(?=\\r?\\n|$)`, "g"), `$1${thai}`);

    // Avoid broad prose rewriting, but replace approved multi-word terms when already emphasized as UI text.
    next = next.replace(new RegExp(`\\*\\*${escaped}\\*\\*`, "g"), `**${thai}**`);

    // Product text should use approved glossary Thai. This is intentionally broad for approved terms only.
    next = next.replace(new RegExp(`(?<![A-Za-z])${escaped}(?![A-Za-z])`, "g"), thai);

    if (next !== before) hits.push(`${term} -> ${thai} (${source})`);
  }

  next = next
    .replace(/สำนักงานกิจการผิดปกติ\s*\(สำนักงาน of กิจการผิดปกติ\s*-\s*BUA\)/g, "สำนักงานกิจการผิดปกติ (BUA)")
    .replace(/สำนักงานกิจการผิดปกติ\s*\(The สำนักงาน of กิจการผิดปกติ\s*-\s*BUA\)/g, "สำนักงานกิจการผิดปกติ (BUA)");

  next = next
    .replace(/([ก-๙A-Za-z0-9]) {2,}([ก-๙A-Za-z0-9])/g, "$1 $2")
    .replace(/ {2,}([,.;:!?])/g, "$1")
    .replace(/ +\]/g, "]")
    .replace(/\[ +/g, "[")
    .replace(/ +\)/g, ")")
    .replace(/\( +/g, "(");
  return { text: next, hits };
}

const terms = loadTerms();
const targets = [
  ...walk(path.join(HGD, "05_Output"), (target) => target.endsWith(".md")),
  ...walk(path.join(HGD, "04_Work"), (target) => target.endsWith(".formatted.json")),
];

let changed = 0;
const changedTerms = new Set();

for (const target of targets) {
  const raw = fs.readFileSync(target, "utf8");
  let next = raw;
  let hits = [];

  if (target.endsWith(".formatted.json")) {
    try {
      const payload = JSON.parse(raw);
      if (typeof payload.text === "string") {
        const repaired = repairText(payload.text, terms);
        if (repaired.text !== payload.text) {
          payload.text = repaired.text;
          next = `${JSON.stringify(payload, null, 2)}\n`;
          hits = repaired.hits;
        }
      }
    } catch {
      const repaired = repairText(raw, terms);
      next = repaired.text;
      hits = repaired.hits;
    }
  } else {
    const repaired = repairText(raw, terms);
    next = repaired.text;
    hits = repaired.hits;
  }

  if (next !== raw) {
    fs.writeFileSync(target, next, "utf8");
    changed += 1;
    hits.forEach((hit) => changedTerms.add(hit));
    console.log(`updated ${path.relative(ROOT, target)}`);
  }
}

console.log(`updated files: ${changed}`);
console.log("terms:");
for (const hit of [...changedTerms].sort()) console.log(`- ${hit}`);
