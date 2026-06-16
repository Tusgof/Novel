import SiteFooter from "../../components/SiteFooter";
import SiteHeader from "../../components/SiteHeader";
import ChapterList from "../../components/ChapterList";
import { getManifest } from "../../lib/chapters";

export default function ChaptersPage() {
  const manifest = getManifest();
  const pending = manifest.summary.missing + manifest.summary.rejected;

  return (
    <main className="site-shell">
      <SiteHeader />

      <section className="page-title">
        <span className="eyebrow">สารบัญ</span>
        <h1>สารบัญ {manifest.novel.title}</h1>
        <p>
          รวม {manifest.summary.available} ตอนที่พร้อมอ่าน
          ตอนที่ยังไม่พร้อมจะแสดงเป็นรายการปิดไว้จนกว่าจะเข้าคลัง
        </p>
      </section>

      <section className="status-band toc-band" aria-label="สถานะตอนทั้งหมด">
        <div>
          <strong>{manifest.summary.available}</strong>
          <span>ตอนที่พร้อมอ่าน</span>
        </div>
        <div>
          <strong>{pending}</strong>
          <span>ตอนที่ยังไม่พร้อมอ่าน</span>
        </div>
        <div>
          <strong>{manifest.summary.rejected}</strong>
          <span>ตอนที่ยังไม่เผยแพร่</span>
        </div>
        <div>
          <strong>{manifest.summary.total}</strong>
          <span>จำนวนตอนทั้งหมด</span>
        </div>
      </section>

      <section className="toc-section">
        <ChapterList chapters={manifest.chapters} />
      </section>

      <SiteFooter />
    </main>
  );
}
