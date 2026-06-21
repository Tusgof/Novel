const fs = require("fs");
const path = require("path");

const ROOT = "D:\\Fogust\\Workspace\\Novel";

function walk(dir, predicate, out = []) {
  if (!fs.existsSync(dir)) return out;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      walk(full, predicate, out);
    } else if (predicate(full)) {
      out.push(full);
    }
  }
  return out;
}

const files = [
  ...walk(path.join(ROOT, "Deep Sea Embers\\05_Output"), (file) => file.endsWith(".md")),
  ...walk(path.join(ROOT, "Horror Game Developers\\05_Output"), (file) => file.endsWith(".md")),
  ...walk(path.join(ROOT, "Deep Sea Embers\\04_Work"), (file) => file.endsWith(".formatted.json")),
  ...walk(path.join(ROOT, "Horror Game Developers\\04_Work"), (file) => file.endsWith(".formatted.json")),
];

const malformedGateMenu = [
  "**[▶",
  "",
  "**[เกต 0]**",
  "",
  "]**",
  "**[▷",
  "",
  "**[Null Arch]**",
  "",
  "(ประตูโค้งสูญค่า)]**",
  "**[▷",
  "",
  "**[Infinite Path]**",
  "",
  "(เส้นทางไร้สิ้นสุด)]**",
  "**[▷",
  "",
  "**[Silent March]**",
  "",
  "(ขบวนเงียบงัน)]**",
  "**[▷",
  "",
  "**[The Maw of Passage]**",
  "",
  "(ปากเหวแห่งทางผ่าน)]**",
].join("\n");

const repairedGateMenu = [
  "**[▶ เกต 0]**",
  "",
  "**[▷ ประตูโค้งสูญค่า]**",
  "",
  "**[▷ เส้นทางไร้สิ้นสุด]**",
  "",
  "**[▷ ขบวนเงียบงัน]**",
  "",
  "**[▷ ปากเหวแห่งทางผ่าน]**",
].join("\n");

const brokenYesNoChoiceRegex =
  /\*\*\[▶\s*\r?\n\r?\n\*\*\[ใช่\]\*\*\s*\r?\n\r?\n▷\s*\r?\n\r?\n\*\*\[ไม่ใช่\]\*\*\s*\r?\n\r?\n\]\*\*/g;

const repairedYesNoChoice = ["**[▶ ใช่]**", "", "**[▷ ไม่ใช่]**"].join("\n");

const gateMenuRegex =
  /\*\*\[▶\s*\r?\n\r?\n\*\*\[เกต 0\]\*\*\s*\r?\n\r?\n\]\*\*\s*\r?\n\*\*\[▷\s*\r?\n\r?\n\*\*\[Null Arch\]\*\*\s*\r?\n\r?\n\(ประตูโค้งสูญค่า\)\]\*\*\s*\r?\n\*\*\[▷\s*\r?\n\r?\n\*\*\[Infinite Path\]\*\*\s*\r?\n\r?\n\(เส้นทางไร้สิ้นสุด\)\]\*\*\s*\r?\n\*\*\[▷\s*\r?\n\r?\n\*\*\[Silent March\]\*\*\s*\r?\n\r?\n\(ขบวนเงียบงัน\)\]\*\*\s*\r?\n\*\*\[▷\s*\r?\n\r?\n\*\*\[The Maw of Passage\]\*\*\s*\r?\n\r?\n\(ปากเหวแห่งทางผ่าน\)\]\*\*/g;

const replacements = [
  [/เสียง \(term\)/g, "เสียง"],
  [/'สิ่งผิดปกติ' \(Anomaly\)/g, "“สิ่งผิดปกติ”"],
  [/'ปรากฏการณ์ประหลาด' \(Vision\)/g, "“ปรากฏการณ์ประหลาด”"],
  [/\s+\((?:character|entity|rank|system|term)\)/g, ""],
  [gateMenuRegex, repairedGateMenu],
  [brokenYesNoChoiceRegex, repairedYesNoChoice],
  [malformedGateMenu, repairedGateMenu],
  [
    "ดวงตาที่หายไปของเขา *** ไม่มีสิ่งใดรอดพ้นสายตาของผมไปได้",
    "ดวงตาที่หายไปของเขา\n\n***\n\nไม่มีสิ่งใดรอดพ้นสายตาของผมไปได้",
  ],
];

let changed = 0;

for (const target of files) {
  if (!fs.existsSync(target)) continue;
  let text = fs.readFileSync(target, "utf8");
  const before = text;
  let jsonHandled = false;
  if (target.endsWith(".formatted.json")) {
    try {
      const payload = JSON.parse(text);
      if (typeof payload.text === "string") {
        const beforeText = payload.text;
        for (const [pattern, value] of replacements) {
          payload.text = payload.text.replace(pattern, value);
        }
        if (payload.text !== beforeText) {
          text = `${JSON.stringify(payload, null, 2)}\n`;
        }
        jsonHandled = true;
      }
    } catch {
      // Fall back to raw text replacement below.
    }
  }
  if (!jsonHandled) {
    for (const [pattern, value] of replacements) {
      text = text.replace(pattern, value);
    }
  }
  if (text !== before) {
    fs.writeFileSync(target, text, "utf8");
    changed += 1;
    console.log(`updated ${path.relative(ROOT, target)}`);
  }
}

console.log(`updated files: ${changed}`);
