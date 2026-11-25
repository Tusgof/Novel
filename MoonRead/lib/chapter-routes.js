export const shortReaderBooks = {
  gacha: "a-gacha-addicts-fusionpunk-life",
  investing: "investing-in-my-crippled-wife",
};

export function shortChapterHref(slug, chapter) {
  if (chapter?.status !== "available") return null;
  const alias = Object.keys(shortReaderBooks).find((key) => shortReaderBooks[key] === slug);
  return alias ? `/${alias}/${chapter.number}` : null;
}

export function withReaderHref(slug, chapter) {
  const href = shortChapterHref(slug, chapter);
  return href ? { ...chapter, href } : chapter;
}
