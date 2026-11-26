export function bookmarkDestination(chapter, progress) {
  const review = Boolean(progress && progress.chapterId !== chapter.id);
  return {
    href: `${chapter.href}?${review ? "review" : "bookmark"}=1`,
    label: review ? "อ่านทวน · เก็บจุดอ่านเดิม" : "อ่านจากที่คั่น",
  };
}
