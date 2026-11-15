import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import test from "node:test";

const appRoot = fileURLToPath(new URL("..", import.meta.url));
const temporaryRoot = path.join(os.tmpdir(), "opencode");
fs.mkdirSync(temporaryRoot, { recursive: true });

function fixture(t) {
  const root = fs.mkdtempSync(path.join(temporaryRoot, "moonread-generation-"));
  const app = path.join(root, "MoonRead");
  fs.mkdirSync(path.join(app, "scripts"), { recursive: true });
  fs.mkdirSync(path.join(root, "00_Config"));
  fs.copyFileSync(path.join(appRoot, "scripts/generate-chapters.mjs"), path.join(app, "scripts/generate-chapters.mjs"));
  fs.symlinkSync(path.join(appRoot, "node_modules"), path.join(app, "node_modules"), process.platform === "win32" ? "junction" : "dir");
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const book = (slug, legacyDefault = false) => ({ slug, folder: slug, output_dir: "05_Output",
    reader: { enabled: true, legacy_default: legacyDefault, first_chapter: 1, last_chapter: 3,
      lean_retranslated_through: 2, code_chapters: ["ch002"], title: slug, tags: [] } });
  const registry = { novels: [book("old", true)] };
  const source = (slug, id, text = `# บทที่ ${Number(id.slice(2))}: ทดสอบ\n\n${Array(20).fill("นี่คือเนื้อเรื่องทดสอบสำหรับตรวจหน้าอ่านโดยไม่เรียกโมเดล").join("\n\n")}`) => {
    const directory = path.join(root, slug, "05_Output", id);
    fs.mkdirSync(directory, { recursive: true });
    fs.writeFileSync(path.join(directory, `${id}.md`), text);
  };
  for (const id of ["ch001", "ch002", "ch003"]) source("old", id);
  const run = (scope = "") => {
    fs.writeFileSync(path.join(root, "00_Config/novel_registry.json"), JSON.stringify(registry));
    return spawnSync(process.execPath, ["scripts/generate-chapters.mjs"], {
      cwd: app, encoding: "utf8", env: { ...process.env, SENTINEL_NOVEL: scope },
    });
  };
  const manifest = (slug) => JSON.parse(fs.readFileSync(path.join(app, "content/generated/books", slug, "manifest.json"), "utf8"));
  const snapshot = (relative) => fs.readFileSync(path.join(app, "content/generated", relative));
  const writeSnapshot = (relative, bytes) => fs.writeFileSync(path.join(app, "content/generated", relative), bytes);
  const addNewBook = () => {
    registry.novels.push(book("new"));
    for (const id of ["ch001", "ch002", "ch003"]) source("new", id);
  };
  assert.equal(run().status, 0);
  return { run, registry, source, manifest, snapshot, writeSnapshot, addNewBook };
}

test("Code labels override only explicit IDs; historical Lean/Pipe labels survive", (t) => {
  const f = fixture(t);
  assert.deepEqual(f.manifest("old").chapters.map((chapter) => chapter.translator), ["[Lean]", "[Code]", "[Pipe]"]);
});

test("scoped generation preserves an old snapshot even when unrelated local source is bad", (t) => {
  const f = fixture(t);
  const paths = ["books/old/manifest.json", "books/old/chapters/ch001.md", "manifest.json", "chapters/ch001.md"];
  const before = paths.map((name) => f.snapshot(name));
  f.source("old", "ch001", "invalid old local work, not part of this publication");
  f.addNewBook();
  assert.equal(f.run("new").status, 0);
  for (const [index, name] of paths.entries()) assert.deepEqual(f.snapshot(name), before[index], name);
  assert.equal(f.manifest("new").summary.available, 3);
});

test("the selected novel is still validated; invalid new content is not grandfathered", (t) => {
  const f = fixture(t);
  f.addNewBook();
  f.source("new", "ch001", "invalid new source");
  assert.equal(f.run("new").status, 0);
  assert.equal(f.manifest("new").summary.rejected, 1);
  assert.equal(f.manifest("new").chapters[0].status, "rejected");
});

test("unknown/disabled scopes fail before the existing snapshot is cleaned", (t) => {
  const f = fixture(t);
  const before = f.snapshot("books/old/manifest.json");
  assert.notEqual(f.run("unknown").status, 0);
  assert.deepEqual(f.snapshot("books/old/manifest.json"), before);
  f.addNewBook();
  f.registry.novels[1].reader.enabled = false;
  assert.notEqual(f.run("new").status, 0);
  assert.deepEqual(f.snapshot("books/old/manifest.json"), before);
});

test("unrelated registry range drift cannot masquerade as an unchanged snapshot", (t) => {
  const f = fixture(t);
  f.addNewBook();
  const before = f.snapshot("books/old/manifest.json");
  f.registry.novels[0].reader.last_chapter = 4;
  assert.notEqual(f.run("new").status, 0);
  assert.deepEqual(f.snapshot("books/old/manifest.json"), before);
});

test("scoped generation preserves a legacy CRLF root manifest byte-for-byte", (t) => {
  const f = fixture(t);
  const rootManifestText = f.snapshot("manifest.json").toString("utf8");
  f.writeSnapshot("manifest.json", rootManifestText.replace(/\n/g, "\r\n"));
  const before = f.snapshot("manifest.json");
  f.addNewBook();
  assert.equal(f.run("new").status, 0);
  assert.deepEqual(f.snapshot("manifest.json"), before);
});

test("a mutated legacy root manifest is rejected before cleanup", (t) => {
  const f = fixture(t);
  const rootManifest = JSON.parse(f.snapshot("manifest.json").toString("utf8"));
  rootManifest.targetRange = "ch001-ch004";
  f.writeSnapshot("manifest.json", `${JSON.stringify(rootManifest, null, 2)}\n`);
  const rootBefore = f.snapshot("manifest.json");
  const bookBefore = f.snapshot("books/old/manifest.json");
  f.addNewBook();
  assert.notEqual(f.run("new").status, 0);
  assert.deepEqual(f.snapshot("manifest.json"), rootBefore);
  assert.deepEqual(f.snapshot("books/old/manifest.json"), bookBefore);
});
