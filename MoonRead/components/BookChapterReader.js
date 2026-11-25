import { notFound, permanentRedirect } from "next/navigation";
import ReaderShell from "./ReaderShell";
import { getAvailableBookChapters, getBookChapter, getBookChapterMarkdown, getBookChapterNeighbors, getBookManifest, markdownToBlocks } from "../lib/chapters";
import { shortChapterHref } from "../lib/chapter-routes";

export function bookChapterMetadata(bookSlug, chapterId) {
  const chapter = getBookChapter(bookSlug, chapterId);
  const book = getBookManifest(bookSlug);
  return {
    title: chapter && book ? `${chapter.title} | ${book.novel.title} | MoonRead` : "MoonRead",
  };
}

export default function BookChapterReader({ bookSlug, chapterId, redirectToShort = false }) {
  const bookManifest = getBookManifest(bookSlug);
  const chapter = getBookChapter(bookSlug, chapterId);
  const markdown = getBookChapterMarkdown(bookSlug, chapterId);
  if (!bookManifest || !chapter || !markdown) notFound();

  const shortHref = redirectToShort && shortChapterHref(bookSlug, chapter);
  if (shortHref) permanentRedirect(shortHref);

  return (
    <ReaderShell
      chapter={chapter}
      neighbors={getBookChapterNeighbors(bookSlug, chapterId)}
      chapters={getAvailableBookChapters(bookSlug)}
      blocks={markdownToBlocks(markdown)}
      book={{ ...bookManifest.novel, chaptersHref: bookManifest.chaptersHref }}
    />
  );
}
