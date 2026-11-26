import { getBookChapter, getBookChapterMarkdown, getBookChapterNeighbors, getBooks, markdownToBlocks, readerChapter } from "../../../../lib/chapters";

export async function GET(_request, { params }) {
  const { bookSlug, chapterId } = await params;
  if (!/^ch\d+$/.test(chapterId) || !getBooks().some((book) => book.slug === bookSlug)) return new Response(null, { status: 404 });
  const chapter = getBookChapter(bookSlug, chapterId);
  const markdown = chapter && getBookChapterMarkdown(bookSlug, chapterId);
  if (!markdown) return new Response(null, { status: 404 });
  const { previous, next } = getBookChapterNeighbors(bookSlug, chapterId);
  return Response.json({ chapter: readerChapter(chapter), neighbors: { previous: readerChapter(previous), next: readerChapter(next) }, blocks: markdownToBlocks(markdown) });
}
