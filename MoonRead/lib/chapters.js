import fs from "node:fs";
import path from "node:path";

const generatedRoot = path.join(process.cwd(), "content", "generated");
const generatedChapterRoot = path.join(generatedRoot, "chapters");
const generatedBooksRoot = path.join(generatedRoot, "books");
const manifestPath = path.join(generatedRoot, "manifest.json");
const libraryPath = path.join(generatedRoot, "library.json");

export const defaultBookSlug = "deep-sea-embers";

export function getManifest() {
  if (!fs.existsSync(manifestPath)) {
    return {
      generatedAt: null,
      targetRange: "ch001-ch050",
      novel: {
        slug: "deep-sea-embers",
        title: "Deep Sea Embers",
        thaiTitle: "เถ้าถ่านแห่งทะเลลึก",
        author: "远瞳 (Yuan Tong)",
        synopsis: "ยังไม่มี manifest — รัน npm run generate:chapters ก่อน build",
        tags: [],
      },
      summary: { total: 50, available: 0, missing: 50, rejected: 0, skipped: 0 },
      chapters: [],
    };
  }

  return JSON.parse(fs.readFileSync(manifestPath, "utf8"));
}

export function getLibraryManifest() {
  if (!fs.existsSync(libraryPath)) {
    const manifest = getManifest();
    return {
      generatedAt: manifest.generatedAt,
      reader: manifest.reader,
      summary: {
        books: 1,
        chapters: manifest.summary.total,
        available: manifest.summary.available,
        missing: manifest.summary.missing,
        rejected: manifest.summary.rejected,
      },
      books: [
        {
          slug: manifest.novel.slug,
          title: manifest.novel.title,
          thaiTitle: manifest.novel.thaiTitle,
          synopsis: manifest.novel.synopsis,
          tags: manifest.novel.tags,
          cover: manifest.novel.cover || "/images/deep-sea-embers-cover.png",
          href: "/book",
          chaptersHref: "/chapters",
          targetRange: manifest.targetRange,
          summary: manifest.summary,
          latestChapter: manifest.chapters.filter((chapter) => chapter.status === "available").at(-1) || null,
          firstChapter: manifest.chapters.find((chapter) => chapter.status === "available") || null,
        },
      ],
    };
  }

  return JSON.parse(fs.readFileSync(libraryPath, "utf8"));
}

export function getBookManifest(slug = defaultBookSlug) {
  if (slug === defaultBookSlug) return getManifest();

  const bookManifestPath = path.join(generatedBooksRoot, slug, "manifest.json");
  if (!fs.existsSync(bookManifestPath)) return null;
  return JSON.parse(fs.readFileSync(bookManifestPath, "utf8"));
}

export function getBooks() {
  return getLibraryManifest().books;
}

export function getChapters() {
  return getManifest().chapters;
}

export function getBookChapters(slug = defaultBookSlug) {
  return getBookManifest(slug)?.chapters || [];
}

export function getAvailableChapters() {
  return getChapters().filter((chapter) => chapter.status === "available");
}

export function getAvailableBookChapters(slug = defaultBookSlug) {
  return getBookChapters(slug).filter((chapter) => chapter.status === "available");
}

export function getChapter(id) {
  return getChapters().find((chapter) => chapter.id === id);
}

export function getBookChapter(slug, id) {
  return getBookChapters(slug).find((chapter) => chapter.id === id);
}

export function getChapterMarkdown(id) {
  const chapter = getChapter(id);
  if (!chapter || chapter.status !== "available") return null;

  const chapterPath = path.join(generatedChapterRoot, `${id}.md`);
  if (!fs.existsSync(chapterPath)) return null;
  return fs.readFileSync(chapterPath, "utf8");
}

export function getBookChapterMarkdown(slug, id) {
  if (slug === defaultBookSlug) return getChapterMarkdown(id);

  const chapter = getBookChapter(slug, id);
  if (!chapter || chapter.status !== "available") return null;

  const chapterPath = path.join(generatedBooksRoot, slug, "chapters", `${id}.md`);
  if (!fs.existsSync(chapterPath)) return null;
  return fs.readFileSync(chapterPath, "utf8");
}

export function getChapterNeighbors(id) {
  const available = getAvailableChapters();
  const index = available.findIndex((chapter) => chapter.id === id);
  return {
    previous: index > 0 ? available[index - 1] : null,
    next: index >= 0 && index < available.length - 1 ? available[index + 1] : null,
  };
}

export function getBookChapterNeighbors(slug, id) {
  const available = getAvailableBookChapters(slug);
  const index = available.findIndex((chapter) => chapter.id === id);
  return {
    previous: index > 0 ? available[index - 1] : null,
    next: index >= 0 && index < available.length - 1 ? available[index + 1] : null,
  };
}

export function markdownToBlocks(markdown) {
  const normalized = markdown.replace(/\r\n/g, "\n").trim();
  const lines = normalized.split("\n");
  const blocks = [];
  let paragraph = [];

  function flushParagraph() {
    if (paragraph.length === 0) return;
    const text = paragraph.join("\n").trim();
    if (text) {
      blocks.push({ type: "paragraph", text });
    }
    paragraph = [];
  }

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) {
      flushParagraph();
      continue;
    }

    if (trimmed.startsWith("# ")) {
      flushParagraph();
      blocks.push({ type: "title", text: trimmed.replace(/^#\s+/, "") });
      continue;
    }

    if (trimmed.startsWith("## ")) {
      flushParagraph();
      blocks.push({ type: "heading", text: trimmed.replace(/^##\s+/, "") });
      continue;
    }

    paragraph.push(trimmed);
  }

  flushParagraph();
  return blocks;
}
