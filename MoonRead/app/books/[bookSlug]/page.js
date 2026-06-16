import Link from "next/link";
import Image from "next/image";
import { notFound } from "next/navigation";
import { ArrowRight, CheckCircle2, Layers3, PenLine } from "lucide-react";
import SiteFooter from "../../../components/SiteFooter";
import SiteHeader from "../../../components/SiteHeader";
import ChapterList from "../../../components/ChapterList";
import { defaultBookSlug, getBookManifest, getBooks } from "../../../lib/chapters";

export function generateStaticParams() {
  return getBooks()
    .filter((book) => book.slug !== defaultBookSlug)
    .map((book) => ({ bookSlug: book.slug }));
}

export async function generateMetadata({ params }) {
  const { bookSlug } = await params;
  const manifest = getBookManifest(bookSlug);
  return {
    title: manifest ? `${manifest.novel.title} | MoonRead` : "MoonRead",
  };
}

export default async function MultiBookPage({ params }) {
  const { bookSlug } = await params;
  const manifest = getBookManifest(bookSlug);

  if (!manifest) {
    notFound();
  }

  const { novel, summary, chapters } = manifest;
  const available = chapters.filter((chapter) => chapter.status === "available");
  const firstAvailable = available[0];
  const latest = available.at(-1);
  const pending = summary.missing + summary.rejected;

  return (
    <main className="site-shell">
      <SiteHeader />

      <section className="book-hero">
        <div className={`book-cover${!novel.cover || novel.cover.includes('logo') ? ' logo-cover' : ''}`}>
          <Image
            src={novel.cover || "/images/moonread-logo.svg"}
            alt={`${novel.title} cover art`}
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

      <section className="toc-section">
        <div className="section-heading">
          <span>สารบัญ</span>
          <Link href={manifest.chaptersHref}>ดูทั้งหมด</Link>
        </div>
        <ChapterList chapters={chapters.slice(0, 20)} />
      </section>

      <SiteFooter />
    </main>
  );
}
