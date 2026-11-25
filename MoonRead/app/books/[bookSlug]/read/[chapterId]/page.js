import { notFound } from "next/navigation";
import ReaderShell from "../../../../../components/ReaderShell";
import {
  defaultBookSlug,
  getAvailableBookChapters,
  getBookChapter,
  getBookChapterMarkdown,
  getBookChapterNeighbors,
  getBookManifest,
  getBooks,
  markdownToBlocks,
} from "../../../../../lib/chapters";

export function generateStaticParams() {
  return getBooks()
    .filter((book) => book.slug !== defaultBookSlug)
    .flatMap((book) =>
      getAvailableBookChapters(book.slug).map((chapter) => ({
        bookSlug: book.slug,
        chapterId: chapter.id,
      }))
    );
}

export async function generateMetadata({ params }) {
  const { bookSlug, chapterId } = await params;
  const chapter = getBookChapter(bookSlug, chapterId);
  const book = getBookManifest(bookSlug);
  return {
    title: chapter && book ? `${chapter.title} | ${book.novel.title} | MoonRead` : "MoonRead",
  };
}

export default async function ReadBookChapterPage({ params }) {
  const { bookSlug, chapterId } = await params;
  const bookManifest = getBookManifest(bookSlug);
  const chapter = getBookChapter(bookSlug, chapterId);
  const markdown = getBookChapterMarkdown(bookSlug, chapterId);

  if (!bookManifest || !chapter || !markdown) {
    notFound();
  }

  return (
    <ReaderShell
      key={`${bookSlug}/${chapter.id}`}
      chapter={chapter}
      neighbors={getBookChapterNeighbors(bookSlug, chapterId)}
      chapters={getAvailableBookChapters(bookSlug).map(({ id, number, title, href }) => ({ id, number, title, href }))}
      blocks={markdownToBlocks(markdown)}
      book={{ slug: bookSlug, title: bookManifest.novel.title, chaptersHref: bookManifest.chaptersHref }}
    />
  );
}
