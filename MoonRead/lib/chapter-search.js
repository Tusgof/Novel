const NUMERIC_QUERY = /^\d+$/;

// Shared TOC filter: a numeric-only query matches the episode number itself
// (so "005", "0005" and "5" all select episode 5), while text queries keep the
// existing case-insensitive title substring and number substring matching.
export function filterChapters(chapters, query) {
  const raw = typeof query === "string" ? query.trim() : "";
  if (!raw) return chapters;
  if (NUMERIC_QUERY.test(raw)) {
    const target = Number(raw);
    return chapters.filter((chapter) => Number(chapter.number) === target);
  }
  const needle = raw.toLowerCase();
  return chapters.filter((chapter) => {
    const title = (chapter.title || "").toLowerCase();
    return title.includes(needle) || String(chapter.number).includes(needle);
  });
}
