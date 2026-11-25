import BookChapterReader, { bookChapterMetadata } from "../../../../../components/BookChapterReader";
import { defaultBookSlug, getAvailableBookChapters, getBooks } from "../../../../../lib/chapters";

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
  return bookChapterMetadata(bookSlug, chapterId);
}

export default async function ReadBookChapterPage({ params }) {
  const { bookSlug, chapterId } = await params;
  return <BookChapterReader bookSlug={bookSlug} chapterId={chapterId} redirectToShort />;
}
