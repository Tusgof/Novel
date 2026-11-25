import { arabicDigits, chapterNumber } from "./chapter-number";

const NUMERIC_QUERY = /^(?:(?:บทที่|ตอน(?:ที่)?|chapter)\s*)?0*(\d+)$/i;

// Shared TOC filter: a numeric-only query matches the episode number itself
// (so "005", "0005" and "5" all select episode 5), while text queries keep the
// existing case-insensitive title substring and number substring matching.
export function filterChapters(chapters, query) {
  const raw = typeof query === "string" ? arabicDigits(query.trim()) : "";
  if (!raw) return chapters;
  const number = raw.match(NUMERIC_QUERY);
  if (number) {
    const target = Number(number[1]);
    return chapters.filter((chapter) => chapterNumber(chapter) === target);
  }
  const needle = raw.toLowerCase();
  return chapters.filter((chapter) => {
    const title = arabicDigits(chapter.title || "").toLowerCase();
    return title.includes(needle);
  });
}
