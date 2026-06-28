import { notFound } from "next/navigation";
import AppHeader from "../../../components/AppHeader";
import BottomNav from "../../../components/BottomNav";
import SiteFooter from "../../../components/SiteFooter";
import BookDetail from "../../../components/BookDetail";
import { defaultBookSlug, getBookManifest, getBooks } from "../../../lib/chapters";

export function generateStaticParams() {
  return getBooks()
    .filter((book) => book.slug !== defaultBookSlug)
    .map((book) => ({ bookSlug: book.slug }));
}

export async function generateMetadata({ params }) {
  const { bookSlug } = await params;
  const manifest = getBookManifest(bookSlug);
  return { title: manifest ? `${manifest.novel.title} | MoonRead` : "MoonRead" };
}

export default async function MultiBookPage({ params }) {
  const { bookSlug } = await params;
  const manifest = getBookManifest(bookSlug);
  if (!manifest) notFound();

  const { novel, summary, chapters } = manifest;
  const book = {
    slug: novel.slug,
    title: novel.title,
    thaiTitle: novel.thaiTitle,
    author: novel.author,
    tags: novel.tags,
    cover: novel.cover || "/images/moonread-logo.svg",
    synopsis: novel.synopsis,
    summary,
    href: `/books/${novel.slug}`,
  };

  return (
    <>
      <AppHeader />
      <BookDetail book={book} chapters={chapters} />
      <SiteFooter />
      <BottomNav />
    </>
  );
}
