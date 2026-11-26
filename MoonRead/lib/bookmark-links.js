export function shouldReviewBookmark(bookmark, progress) {
  if (!progress) return false;
  if (progress.chapterId !== bookmark.id) return true;
  const marked = bookmark.position;
  const saved = progress.position;
  if (!saved) return Boolean(marked || progress.percent > 0);
  return marked?.block !== saved.block || marked?.fraction !== saved.fraction;
}

export function bookmarkDestination(bookmark, progress) {
  const review = shouldReviewBookmark(bookmark, progress);
  return {
    href: `${bookmark.href}?${review ? "review" : "bookmark"}=1`,
    label: review ? "อ่านทวน · เก็บจุดอ่านเดิม" : "อ่านจากที่คั่น",
  };
}
