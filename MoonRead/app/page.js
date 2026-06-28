import { Suspense } from "react";
import AppHeader from "../components/AppHeader";
import BottomNav from "../components/BottomNav";
import SiteFooter from "../components/SiteFooter";
import Discover from "../components/Discover";
import { getLibraryManifest } from "../lib/chapters";

export default function HomePage() {
  const library = getLibraryManifest();
  const books = library.books;
  const genres = [...new Set(books.flatMap((b) => b.tags || []))];

  return (
    <>
      <AppHeader />
      <Suspense fallback={<div className="page shell" />}>
        <Discover books={books} genres={genres} />
      </Suspense>
      <SiteFooter />
      <BottomNav />
    </>
  );
}
