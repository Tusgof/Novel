import { notFound } from "next/navigation";
import Link from "next/link";
import { CheckCircle2, Clock3, Lock, XCircle } from "lucide-react";
import AppHeader from "../../../../components/AppHeader";
import BottomNav from "../../../../components/BottomNav";
import SiteFooter from "../../../../components/SiteFooter";
import { defaultBookSlug, getBookManifest, getBooks } from "../../../../lib/chapters";

function icon(status) {
  if (status === "available") return <CheckCircle2 size={18} />;
  if (status === "rejected") return <XCircle size={18} />;
  return <Lock size={18} />;
}

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

      <main className="page shell">
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

        <div className="toc-list" style={{ marginTop: 20 }}>
          {manifest.chapters.map((chapter) => {
            const disabled = chapter.status !== "available";
            const label = `ตอน ${String(chapter.number).padStart(3, "0")}`;
            const inner = (
              <>
                <span className="num">{String(chapter.number).padStart(3, "0")}</span>
                <span className="ct">
                  <small>{label}</small>
                  <strong>{disabled ? `${label} ยังไม่พร้อมอ่าน` : chapter.title}</strong>
                </span>
                <span className="cm">
                  <Clock3 size={13} />
                  {disabled ? (chapter.status === "rejected" ? "รอตรวจไฟล์" : "เร็วๆ นี้") : `${chapter.readingMinutes} น.`}
                </span>
                <span className={`ch-state ${chapter.status}`}>{icon(chapter.status)}</span>
              </>
            );

            return disabled ? (
              <div className="ch-row disabled" key={chapter.id} aria-disabled="true">{inner}</div>
            ) : (
              <Link className="ch-row" href={chapter.href} key={chapter.id}>{inner}</Link>
            );
          })}
        </div>
      </main>

      <SiteFooter />
      <BottomNav />
    </>
  );
}
