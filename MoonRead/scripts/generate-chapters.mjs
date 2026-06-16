import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import iconv from "iconv-lite";

const scriptRoot = path.dirname(fileURLToPath(import.meta.url));
const appRoot = path.resolve(scriptRoot, "..");
const workspaceRoot = path.resolve(appRoot, "..");
const generatedRoot = path.join(appRoot, "content", "generated");
const generatedBooksRoot = path.join(generatedRoot, "books");

const books = [
  {
    slug: "deep-sea-embers",
    sourceRoot: path.resolve(
      process.env.DSE_READER_SOURCE_ROOT || path.join(workspaceRoot, "Deep Sea Embers", "05_Output")
    ),
    firstChapter: Number(process.env.DSE_READER_FIRST_CHAPTER || "1"),
    lastChapter: Number(process.env.DSE_READER_LAST_CHAPTER || "80"),
    legacyDefault: true,
    novel: {
      slug: "deep-sea-embers",
      title: "Deep Sea Embers",
      thaiTitle: "เถ้าถ่านแห่งทะเลลึก",
      author: "远瞳 (Yuan Tong)",
      synopsis:
        "เมื่อครูมัธยมธรรมดาตื่นขึ้นมาพบว่าตัวเองติดอยู่ในอพาร์ตเมนต์ที่ถูกหมอกปริศนาห่อหุ้ม ประตูห้องเดียวที่เปิดได้กลับนำเขาไปสู่ดาดฟ้าเรือผีตำนานแห่ง \"ทะเลไร้ขอบเขต\" ในร่างของกัปตันดันแคน แอบโนมาร์ ผู้เป็นที่หวาดกลัวของทุกคน เขาต้องเรียนรู้ที่จะเป็นกัปตันเรือผีท่ามกลางโลกที่เต็มไปด้วยเทพเจ้า หมอกลึกลับ และพรมแดนความจริงที่กำลังจะพังทลาย",
      tags: ["แฟนตาซี", "ลึกลับ", "เดินเรือ", "ผจญภัย"],
      cover: "/images/deep-sea-embers-cover.png",
    },
  },
  {
    slug: "horror-game-developer",
    sourceRoot: path.resolve(
      process.env.HGD_READER_SOURCE_ROOT || path.join(workspaceRoot, "Horror Game Developers", "05_Output")
    ),
    firstChapter: Number(process.env.HGD_READER_FIRST_CHAPTER || "1"),
    lastChapter: Number(process.env.HGD_READER_LAST_CHAPTER || "80"),
    novel: {
      slug: "horror-game-developer",
      title: "นักพัฒนาเกมสยองขวัญ",
      thaiTitle: "นักพัฒนาเกมสยองขวัญ",
      author: "CKtalon",
      synopsis:
        "เซ็ธ ธอร์น โปรแกรมเมอร์เกมสุดซวยที่กลัวผีแต่ดันทำเกมสยองขวัญ วันหนึ่งระบบปริศนาบังคับให้เขาเข้าไปในฉากสยองที่เป็นของจริง ต้องเอาชีวิตรอดจากโอเปร่าผีสิง นักดนตรีไร้ดวงตา และผู้เล่นคนอื่นที่ดูจะรู้กฎเกมดีกว่าเขา ภายใต้หน้ากากตัวตลกที่เขาเลือกมาโดยไม่รู้ว่ามันจะเปลี่ยนชะตาของเขาไปตลอดกาล",
      tags: ["สยองขวัญ", "เกม", "ระบบ", "เอาชีวิตรอด"],
      cover: "/images/horror-game-developer-cover.png",
    },
  },
];

const providerLeakPatterns = [
  /\b(as an ai|i cannot|i can't|here is the translation|translated text)\b/i,
  /\b(openrouter|claude|gemini|qwen|deepseek|provider error|api key)\b/i,
  /^```/m,
];

const hanPattern = /[\u3400-\u9fff\uf900-\ufaff]/;
const badEncodingPattern = /[\ufffd\u0080-\u009f\u20ac]/;
const thaiPattern = /[\u0e00-\u0e7f]/g;
const mojibakeClusterPattern = /\u0e40\u0e18|\u0e40\u0e19|\u0e42\u20ac|[\ufffd\u0080-\u009f]/g;

function chapterId(number) {
  return `ch${String(number).padStart(3, "0")}`;
}

function scoreThaiText(text) {
  const thaiCount = text.match(thaiPattern)?.length || 0;
  const mojibakeCount = text.match(mojibakeClusterPattern)?.length || 0;
  return thaiCount - mojibakeCount * 40;
}

function repairThaiMojibake(text) {
  if (typeof text !== "string") return text;

  let current = text;
  for (let attempt = 0; attempt < 2; attempt += 1) {
    const repaired = iconv.decode(iconv.encode(current, "windows-874"), "utf8");
    if (repaired === current || scoreThaiText(repaired) <= scoreThaiText(current)) {
      break;
    }
    current = repaired;
  }
  return current;
}

function trimTrailingWhitespace(text) {
  return text.replace(/[ \t]+$/gm, "");
}

const hgdThaiTitleMap = new Map([
  ["Prologue", "บทนำ"],  ["Jester", "ตัวตลก"],

  ["The Jester", "ตัวตลก"],
  ["Return of the Jester", "การกลับมาของตัวตลก"],
  ["Mission Complete", "ภารกิจสำเร็จ"],
  ["The world has changed", "โลกเปลี่ยนไปแล้ว"],
  ["Orientation Day", "วันปฐมนิเทศ"],
  ["Exit", "ทางออก"],
  ["Developing Game", "พัฒนาเกม"],
  ["The missing piece", "ชิ้นส่วนที่หายไป"],
  ["Scream", "เสียงกรีดร้อง"],
  ["Quest Completed", "เควสต์สำเร็จ"],
  ["Painting", "ภาพวาด"],
  ["Velora Art Museum", "พิพิธภัณฑ์ศิลปะเวลอรา"],
  ["Live Stream", "ไลฟ์สตรีม"],
  ["The lunatic with the sunglasses", "คนบ้าแว่นกันแดด"],
  ["The game that makes you scream", "เกมที่ทำให้กรีดร้อง"],
  ["Your account has been reinstated", "บัญชีของคุณถูกคืนสถานะแล้ว"],
  ["Masquerade ball", "งานเต้นรำสวมหน้ากาก"],
  ["The perfect piece", "ชิ้นงานสมบูรณ์แบบ"],
  ["Crying", "เสียงร้องไห้"],
  ["Little girl", "เด็กหญิงตัวน้อย"],
  ["Little Girl", "เด็กหญิงตัวน้อย"],
  ["App Update", "อัปเดตแอป"],
  ["Shepherd", "ผู้เลี้ยงแกะ"],
  ["Evolution", "วิวัฒนาการ"],
]);

function translateHgdTitle(title, chapterNumber = null) {
  const match = title.trim().match(/^(?:Chapter|ตอนที่)\s+(\d+)\s+-\s+(.+?)(\s+\[\d+\])?$/);
  if (!match) return title;
  const [, number, englishTitle, suffix = ""] = match;
  const thaiTitle = hgdThaiTitleMap.get(englishTitle.trim()) || englishTitle.trim();
  return `ตอนที่ ${Number(chapterNumber || number)} - ${thaiTitle}${suffix}`;
}

function normalizeBookMarkdown(book, markdown, chapterNumber) {
  if (book.slug !== "horror-game-developer") return markdown;
  const lines = markdown.replace(/^\uFEFF/, "").split(/\r?\n/);
  if (lines[0]?.startsWith("# ")) {
    lines[0] = `# ${translateHgdTitle(lines[0].replace(/^#\s+/, "").trim(), chapterNumber)}`;
  }
  return lines.join("\n");
}

function ensureCleanDirectory(directory) {
  fs.rmSync(directory, { recursive: true, force: true });
  fs.mkdirSync(directory, { recursive: true });
}

function titleFromMarkdown(markdown, id) {
  const firstLine = markdown.replace(/^\uFEFF/, "").split(/\r?\n/, 1)[0]?.trim() || "";
  if (firstLine.startsWith("# ")) {
    return firstLine.replace(/^#\s+/, "").trim();
  }
  return `บทที่ ${Number(id.slice(2))}`;
}

function bodyWithoutTitle(markdown) {
  return markdown.replace(/^\uFEFF/, "").split(/\r?\n/).slice(1).join("\n");
}

function validateMarkdown(markdown) {
  const reasons = [];
  const trimmed = markdown.trim();

  if (!trimmed) reasons.push("empty_content");
  if (!/^\uFEFF?#\s+\S+/m.test(markdown)) reasons.push("missing_h1_title");
  if (trimmed.length < 700) reasons.push("too_short");
  if (badEncodingPattern.test(markdown)) reasons.push("bad_encoding_marker");
  if (hanPattern.test(bodyWithoutTitle(markdown))) reasons.push("han_text_detected");

  for (const pattern of providerLeakPatterns) {
    if (pattern.test(markdown)) {
      reasons.push("provider_or_meta_text");
      break;
    }
  }

  return reasons;
}

function sourceRootLabel(sourceRoot) {
  return path.relative(appRoot, sourceRoot).replaceAll("\\", "/") || ".";
}

function chapterHref(book, id) {
  return book.legacyDefault ? `/read/${id}` : `/books/${book.slug}/read/${id}`;
}

function chaptersHref(book) {
  return book.legacyDefault ? "/chapters" : `/books/${book.slug}/chapters`;
}

function bookHref(book) {
  return book.legacyDefault ? "/book" : `/books/${book.slug}`;
}

function buildBookManifest(book) {
  const bookRoot = path.join(generatedBooksRoot, book.slug);
  const generatedChapterRoot = path.join(bookRoot, "chapters");
  fs.mkdirSync(generatedChapterRoot, { recursive: true });

  const chapters = [];
  const included = [];
  const skipped = [];
  const rejected = [];
  const missing = [];

  for (let number = book.firstChapter; number <= book.lastChapter; number += 1) {
    const id = chapterId(number);
    const relativeSource = path.join(id, `${id}.md`);
    const sourcePath = path.join(book.sourceRoot, relativeSource);
    const generatedPath = path.join(generatedChapterRoot, `${id}.md`);

    if (!fs.existsSync(sourcePath)) {
      const entry = {
        id,
        number,
        title: `บทที่ ${number}`,
        status: "missing",
        sourcePath: relativeSource.replaceAll("\\", "/"),
        href: null,
        reason: "source_file_missing",
      };
      chapters.push(entry);
      missing.push(entry);
      continue;
    }

    const sourceMarkdown = fs.readFileSync(sourcePath, "utf8").replace(/\r\n/g, "\n");
    const markdown = normalizeBookMarkdown(book, trimTrailingWhitespace(repairThaiMojibake(sourceMarkdown)), number);
    const validationReasons = validateMarkdown(markdown);
    const title = titleFromMarkdown(markdown, id);
    const charCount = markdown.replace(/\s/g, "").length;
    const readingMinutes = Math.max(1, Math.ceil(charCount / 4500));

    if (validationReasons.length > 0) {
      const entry = {
        id,
        number,
        title,
        status: "rejected",
        sourcePath: relativeSource.replaceAll("\\", "/"),
        href: null,
        reason: validationReasons.join(","),
        charCount,
        readingMinutes,
      };
      chapters.push(entry);
      rejected.push(entry);
      continue;
    }

    fs.writeFileSync(generatedPath, markdown, "utf8");
    const entry = {
      id,
      number,
      title,
      status: "available",
      sourcePath: relativeSource.replaceAll("\\", "/"),
      generatedPath: `content/generated/books/${book.slug}/chapters/${id}.md`,
      href: chapterHref(book, id),
      charCount,
      readingMinutes,
    };
    chapters.push(entry);
    included.push(entry);
  }

  const duplicatedIds = chapters
    .map((chapter) => chapter.id)
    .filter((id, index, ids) => ids.indexOf(id) !== index);

  if (duplicatedIds.length > 0) {
    throw new Error(`Duplicate chapter IDs detected for ${book.slug}: ${[...new Set(duplicatedIds)].join(", ")}`);
  }

  const manifest = {
    generatedAt: new Date().toISOString(),
    sourceRoot: sourceRootLabel(book.sourceRoot),
    targetRange: `${chapterId(book.firstChapter)}-${chapterId(book.lastChapter)}`,
    novel: book.novel,
    href: bookHref(book),
    chaptersHref: chaptersHref(book),
    reader: {
      name: "MoonRead",
      theme: "Stardust",
      colors: {
        navy: "#121926",
        gold: "#EBC05F",
        cream: "#F0F0F0",
      },
    },
    summary: {
      total: chapters.length,
      available: included.length,
      missing: missing.length,
      rejected: rejected.length,
      skipped: skipped.length,
    },
    chapters,
  };

  fs.writeFileSync(path.join(bookRoot, "manifest.json"), `${JSON.stringify(manifest, null, 2)}\n`, "utf8");
  return { manifest, included, missing, rejected, skipped };
}

ensureCleanDirectory(generatedRoot);
fs.mkdirSync(generatedBooksRoot, { recursive: true });

const generated = books.map(buildBookManifest);
const defaultBook = generated.find((entry, index) => books[index].legacyDefault) || generated[0];

fs.cpSync(
  path.join(generatedBooksRoot, defaultBook.manifest.novel.slug, "chapters"),
  path.join(generatedRoot, "chapters"),
  { recursive: true }
);
fs.writeFileSync(path.join(generatedRoot, "manifest.json"), `${JSON.stringify(defaultBook.manifest, null, 2)}\n`, "utf8");

const library = {
  generatedAt: new Date().toISOString(),
  reader: defaultBook.manifest.reader,
  summary: {
    books: generated.length,
    chapters: generated.reduce((total, entry) => total + entry.manifest.summary.total, 0),
    available: generated.reduce((total, entry) => total + entry.manifest.summary.available, 0),
    missing: generated.reduce((total, entry) => total + entry.manifest.summary.missing, 0),
    rejected: generated.reduce((total, entry) => total + entry.manifest.summary.rejected, 0),
  },
  books: generated.map((entry) => ({
    slug: entry.manifest.novel.slug,
    title: entry.manifest.novel.title,
    thaiTitle: entry.manifest.novel.thaiTitle,
    synopsis: entry.manifest.novel.synopsis,
    tags: entry.manifest.novel.tags,
    cover: entry.manifest.novel.cover,
    href: entry.manifest.href,
    chaptersHref: entry.manifest.chaptersHref,
    targetRange: entry.manifest.targetRange,
    summary: entry.manifest.summary,
    latestChapter: entry.manifest.chapters.filter((chapter) => chapter.status === "available").at(-1) || null,
    firstChapter: entry.manifest.chapters.find((chapter) => chapter.status === "available") || null,
  })),
};

fs.writeFileSync(path.join(generatedRoot, "library.json"), `${JSON.stringify(library, null, 2)}\n`, "utf8");

const reportLines = [
  "# Reader Import Report",
  "",
  `Generated at: ${library.generatedAt}`,
  "",
  "## Summary",
  "",
  `- books: ${library.summary.books}`,
  `- available chapters: ${library.summary.available}`,
  `- missing chapters: ${library.summary.missing}`,
  `- rejected chapters: ${library.summary.rejected}`,
  "",
];

for (const entry of generated) {
  reportLines.push(
    `## ${entry.manifest.novel.title}`,
    "",
    `- source root: ${entry.manifest.sourceRoot}`,
    `- target range: ${entry.manifest.targetRange}`,
    `- available: ${entry.included.length}`,
    `- missing: ${entry.missing.length}`,
    `- rejected: ${entry.rejected.length}`,
    "",
    "### Rejected",
    "",
    ...(entry.rejected.length ? entry.rejected.map((chapter) => `- ${chapter.id}: ${chapter.reason}`) : ["- none"]),
    "",
    "### Missing",
    "",
    ...(entry.missing.length ? entry.missing.map((chapter) => `- ${chapter.id}: ${chapter.reason}`) : ["- none"]),
    ""
  );
}

fs.writeFileSync(path.join(generatedRoot, "import-report.md"), reportLines.join("\n"), "utf8");

console.log(
  `Generated reader library: ${library.summary.books} books, ${library.summary.available} available, ${library.summary.missing} missing, ${library.summary.rejected} rejected.`
);
