// Route IDs are stable; the printed chapter number can differ from the ID in
// the imported source. Never use this number to construct a chapter URL.
const printed = /^(?:บทที่|ตอน(?:ที่)?|chapter)\s*([\d๐-๙]+)\s*(?:[:：–—-]|$)/i;

export function arabicDigits(text) {
  return text.replace(/[๐-๙]/g, (digit) => String(digit.charCodeAt(0) - 0x0e50));
}

export function chapterNumber(chapter) {
  const match = chapter.title?.match(printed);
  return match ? Number(arabicDigits(match[1])) : chapter.number;
}

export function episodeLabel(chapter) {
  return `ตอน ${String(chapterNumber(chapter)).padStart(3, "0")}`;
}

export function withNumberGaps(chapters) {
  const numbered = chapters.map(chapterNumber);
  if (!numbered.every((n, i) => !i || (n > numbered[i - 1] && n - numbered[i - 1] <= 50))) return chapters;
  return chapters.flatMap((chapter, i) => {
    if (!i || numbered[i] === numbered[i - 1] + 1) return [chapter];
    const gaps = [];
    for (let n = numbered[i - 1] + 1; n < numbered[i]; n++) gaps.push({ id: `gap-${n}`, number: n, title: "", status: "missing", inferredGap: true });
    return [...gaps, chapter];
  });
}
