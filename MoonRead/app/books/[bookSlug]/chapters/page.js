import { notFound } from "next/navigation";
import AppHeader from "../../../../components/AppHeader";
import ChapterList from "../../../../components/ChapterList";
import BottomNav from "../../../../components/BottomNav";
import SiteFooter from "../../../../components/SiteFooter";
import { defaultBookSlug, getBookManifest, getBooks, readerChapter } from "../../../../lib/chapters";

export function generateStaticParams() {
  return getBooks()
    .filter((book) => book.slug !== defaultBookSlug)
    .map((book) => ({ bookSlug: book.slug }));
}

export async function generateMetadata({ params }) {
  const { bookSlug } = await params;
  const manifest = getBookManifest(bookSlug);
  return {
    title: manifest ? `สารบัญ ${manifest.novel.title} | MoonRead` : "MoonRead",
  };
}

export default async function BookChaptersPage({ params }) {
  const { bookSlug } = await params;
  const manifest = getBookManifest(bookSlug);

  if (!manifest) {
    notFound();
  }

  const pending = manifest.summary.missing + manifest.summary.rejected;

  return (
    <>
      <AppHeader />

      <main className="page shell" id="main-content" tabIndex={-1}>
        <section className="page-title">
          <span className="eyebrow gold">สารบัญ</span>
          <h1>สารบัญ {manifest.novel.title}</h1>
          <p>
            รวม {manifest.summary.available} ตอนที่พร้อมอ่าน
            ตอนที่ยังไม่พร้อมจะแสดงเป็นรายการปิดไว้จนกว่าจะเข้าคลัง
          </p>
        </section>

        <section className="status-grid" aria-label="สถานะตอนทั้งหมด">
          <div className="stat-card"><b>{manifest.summary.available}</b><span>ตอนพร้อมอ่าน</span></div>
          <div className="stat-card"><b>{pending}</b><span>ตอนยังไม่พร้อมอ่าน</span></div>
          <div className="stat-card"><b>{manifest.summary.rejected}</b><span>ตอนยังไม่เผยแพร่</span></div>
          <div className="stat-card"><b>{manifest.summary.total}</b><span>จำนวนตอนทั้งหมด</span></div>
        </section>

        <ChapterList chapters={manifest.chapters.map(readerChapter)} slug={bookSlug} />
      </main>

      <SiteFooter />
      <BottomNav />
    </>
  );
}
