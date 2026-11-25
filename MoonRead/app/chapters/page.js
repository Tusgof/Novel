import AppHeader from "../../components/AppHeader";
import ChapterList from "../../components/ChapterList";
import BottomNav from "../../components/BottomNav";
import SiteFooter from "../../components/SiteFooter";
import { getManifest } from "../../lib/chapters";

export const metadata = { title: "สารบัญ | MoonRead" };

export default function ChaptersPage() {
  const manifest = getManifest();
  const { novel, summary, chapters } = manifest;

  return (
    <>
      <AppHeader />
      <main className="page shell" id="main-content" tabIndex={-1}>
        <section className="page-title">
          <span className="eyebrow gold">สารบัญ</span>
          <h1>สารบัญ {novel.title}</h1>
          <p>รวม {summary.available} ตอนที่พร้อมอ่าน — ตอนที่ยังไม่พร้อมจะแสดงเป็นรายการปิดไว้จนกว่าจะเข้าคลัง</p>
        </section>

        <ChapterList chapters={chapters} slug={novel.slug} />
      </main>
      <SiteFooter />
      <BottomNav />
    </>
  );
}
