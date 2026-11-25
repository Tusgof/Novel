import AppHeader from "../components/AppHeader";
import BottomNav from "../components/BottomNav";
import SiteFooter from "../components/SiteFooter";
import Discover from "../components/Discover";
import { getLibraryManifest } from "../lib/chapters";

export default async function HomePage({ searchParams }) {
  const { q } = await searchParams;
  const library = getLibraryManifest();
  const books = library.books;
  const genres = [...new Set(books.flatMap((b) => b.tags || []))];

  return (
    <>
      <AppHeader />
      <Discover books={books} genres={genres} initialQuery={typeof q === "string" ? q : ""} />
      <SiteFooter />
      <BottomNav />
    </>
  );
}
