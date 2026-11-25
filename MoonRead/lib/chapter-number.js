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
