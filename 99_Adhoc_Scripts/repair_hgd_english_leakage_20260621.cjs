const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const HGD = path.join(ROOT, "Horror Game Developers");

const replacements = [
  ["'ทวิสเต็ดแมน' (Twisted Man)", "ชายบิดเบี้ยว"],
  ["‘ทวิสเต็ดแมน’ (Twisted Man)", "ชายบิดเบี้ยว"],
  ["ทวิสเต็ดแมน (Twisted Man)", "ชายบิดเบี้ยว"],
  ["ทวิสเต็ดแมน", "ชายบิดเบี้ยว"],
  ["ชายผู้บิดเบี้ยว (Twisted Man)", "ชายบิดเบี้ยว"],
  ["ชายบิดเบี้ยว (Twisted Man)", "ชายบิดเบี้ยว"],
  ["ชายผู้บิดเบี้ยว", "ชายบิดเบี้ยว"],
  [" (Twisted Man)", ""],
  ["(Twisted Man)", ""],
  ["'อโนมาลี' (Anomaly)", "ความผิดปกติ"],
  ["‘อโนมาลี’ (Anomaly)", "ความผิดปกติ"],
  ["อโนมาลี (Anomaly)", "ความผิดปกติ"],
  ["อโนมาลี", "ความผิดปกติ"],
  ["ความผิดปกติ (Anomaly)", "ความผิดปกติ"],
  ["ความผิดปกติ (anomaly)", "ความผิดปกติ"],
  ["ความผิดปกติ (Anomalies)", "ความผิดปกติ"],
  ["ความผิดปกติ (anomalies)", "ความผิดปกติ"],
  ["สิ่งผิดปกติ (Anomaly)", "สิ่งผิดปกติ"],
  ["สิ่งผิดปกติ (anomaly)", "สิ่งผิดปกติ"],
  ["สิ่งผิดปกติ (Anomalies)", "สิ่งผิดปกติ"],
  ["สิ่งผิดปกติ (anomalies)", "สิ่งผิดปกติ"],
  ["Squad Leader (หัวหน้าหน่วย)", "หัวหน้ากลุ่ม"],
  ["Squad Leader", "หัวหน้ากลุ่ม"],
  ["ระบบผู้พัฒนาเกม (Game Developer System)", "ระบบนักพัฒนาเกม"],
  ["ระบบนักพัฒนาเกม (Game Developer System)", "ระบบนักพัฒนาเกม"],
  ["สถานการณ์ (Scenario)", "สถานการณ์"],
  ["สถานการณ์ที่ซ่อนอยู่ (Hidden Scenario)", "สถานการณ์ที่ซ่อนอยู่"],
  ["ตัวตลก (Jester)", "ตัวตลก"],
  ["กิลด์ครอนฟอล (Crownfall Guild)", "กิลด์คราวน์ฟอลล์"],
  ["กิลด์คราวน์ฟอลล์ (Crownfall Guild)", "กิลด์คราวน์ฟอลล์"],
];

function repairText(input) {
  let output = input;
  for (const [from, to] of replacements) {
    output = output.split(from).join(to);
  }
  return output;
}

function walk(dir, predicate, acc = []) {
  if (!fs.existsSync(dir)) return acc;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      walk(full, predicate, acc);
    } else if (predicate(full)) {
      acc.push(full);
    }
  }
  return acc;
}

function writeIfChanged(file, updated, changed) {
  const original = fs.readFileSync(file, "utf8");
  if (original !== updated) {
    fs.writeFileSync(file, updated, "utf8");
    changed.push(file);
  }
}

const changed = [];

for (const file of walk(path.join(HGD, "05_Output"), (name) => name.endsWith(".md"))) {
  writeIfChanged(file, repairText(fs.readFileSync(file, "utf8")), changed);
}

for (const file of walk(path.join(HGD, "04_Work"), (name) => name.endsWith(".formatted.json"))) {
  const data = JSON.parse(fs.readFileSync(file, "utf8").replace(/^\uFEFF/, ""));
  const key = Object.prototype.hasOwnProperty.call(data, "formatted_text")
    ? "formatted_text"
    : Object.prototype.hasOwnProperty.call(data, "text")
      ? "text"
      : null;
  if (!key) continue;
  const original = String(data[key]);
  const updated = repairText(original);
  if (updated !== original) {
    data[key] = updated;
    fs.writeFileSync(file, `${JSON.stringify(data, null, 2)}\n`, "utf8");
    changed.push(file);
  }
}

for (const file of changed) {
  console.log(file);
}
console.log(`changed_files=${changed.length}`);
