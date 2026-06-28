import AppHeader from "../../components/AppHeader";
import BottomNav from "../../components/BottomNav";
import SiteFooter from "../../components/SiteFooter";
import BookDetail from "../../components/BookDetail";
import { getManifest } from "../../lib/chapters";

export default function BookPage() {
  const manifest = getManifest();
  const { novel, summary, chapters } = manifest;
  const book = {
    slug: novel.slug,
    title: novel.title,
    thaiTitle: novel.thaiTitle,
    author: novel.author,
    tags: novel.tags,
    cover: novel.cover || "/images/deep-sea-embers-cover.png",
    synopsis: novel.synopsis,
    summary,
    href: "/book",
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
