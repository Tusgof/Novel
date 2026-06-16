import Link from "next/link";
import Image from "next/image";
import { ArrowRight, CheckCircle2, Layers3, PenLine } from "lucide-react";
import SiteFooter from "../../components/SiteFooter";
import SiteHeader from "../../components/SiteHeader";
import ChapterList from "../../components/ChapterList";
import { getManifest } from "../../lib/chapters";

export default function BookPage() {
  const manifest = getManifest();
  const { novel, summary, chapters } = manifest;
  const available = chapters.filter((chapter) => chapter.status === "available");
  const firstAvailable = available[0];
  const latest = available.at(-1);
  const pending = summary.missing + summary.rejected;

  return (
    <main className="site-shell">
      <SiteHeader />

      <section className="book-hero">
        <div className="book-cover">
          <Image
            src="/images/deep-sea-embers-cover.png"
            alt="Deep Sea Embers cover art"
            fill
            priority
            sizes="(max-width: 860px) 360px, 350px"
          />
        </div>

        <div className="book-info">
          <span className="eyebrow">MoonRead</span>
          <h1>{novel.title}</h1>
          <h2>{novel.thaiTitle}</h2>
          <p>{novel.synopsis}</p>

          <div className="tag-row">
            {novel.tags.map((tag) => (
              <span key={tag}>{tag}</span>
            ))}
          </div>

          <dl className="book-meta">
            <div>
              <dt><PenLine size={16} /> ผู้เขียน</dt>
              <dd>{novel.author}</dd>
            </div>
            <div>
              <dt><Layers3 size={16} /> ตอนในเว็บ</dt>
              <dd>{summary.available} / {summary.total} ตอน</dd>
            </div>
            <div>
              <dt><CheckCircle2 size={16} /> สถานะ</dt>
              <dd>{pending === 0 ? "พร้อมอ่านทุกตอน" : `พร้อมอ่าน ${summary.available} ตอน`}</dd>
            </div>
          </dl>

          <div className="hero-actions">
            {firstAvailable ? (
              <Link className="primary-action" href={firstAvailable.href}>
                เริ่มอ่าน
                <ArrowRight size={18} />
              </Link>
            ) : null}
            {latest ? (
              <Link className="secondary-action" href={latest.href}>
                อ่านตอนล่าสุด
              </Link>
            ) : null}
          </div>
        </div>
      </section>

      <section className="book-layout">
        <div className="book-story">
          <div className="section-heading">
            <span>เรื่องย่อ</span>
          </div>
          <p>{novel.synopsis}</p>
        </div>

        <div className="book-sidecard">
          <strong>สถานะ</strong>
          <span>พร้อมอ่าน {summary.available} ตอน</span>
          {pending > 0 ? <span>กำลังเตรียม {pending} ตอน</span> : null}
          <Link className="quiet-link" href="/chapters">
            ไปที่สารบัญ
            <ArrowRight size={16} />
          </Link>
        </div>
      </section>

      <section className="toc-section">
        <div className="section-heading">
          <span>สารบัญ</span>
          <Link href="/chapters">ดูทั้งหมด</Link>
        </div>
        <ChapterList chapters={chapters.slice(0, 20)} />
      </section>

      <SiteFooter />
    </main>
  );
}
