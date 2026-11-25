import { notFound } from "next/navigation";
import BookChapterReader, { bookChapterMetadata } from "../../../components/BookChapterReader";
import { getAvailableBookChapters } from "../../../lib/chapters";
import { shortReaderBooks } from "../../../lib/chapter-routes";

export const dynamicParams = false;

export function generateStaticParams() {
  return Object.entries(shortReaderBooks).flatMap(([readerAlias, slug]) =>
    getAvailableBookChapters(slug).map(({ number }) => ({ readerAlias, chapterNumber: String(number) }))
  );
}

async function resolveChapter(params) {
  const { readerAlias, chapterNumber } = await params;
  if (!Object.hasOwn(shortReaderBooks, readerAlias) || !/^[1-9]\d*$/.test(chapterNumber)) notFound();
  const slug = shortReaderBooks[readerAlias];
  const chapter = getAvailableBookChapters(slug).find(({ number }) => String(number) === chapterNumber);
  if (!chapter) notFound();
  return { slug, chapterId: chapter.id };
}

export async function generateMetadata({ params }) {
  const { slug, chapterId } = await resolveChapter(params);
  return bookChapterMetadata(slug, chapterId);
}

export default async function ReadShortChapterPage({ params }) {
  const { slug, chapterId } = await resolveChapter(params);
  return <BookChapterReader bookSlug={slug} chapterId={chapterId} />;
}
