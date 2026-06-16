import Link from "next/link";
import Image from "next/image";
import { ArrowRight, BookOpen, Clock3, Sparkles } from "lucide-react";
import SiteFooter from "../components/SiteFooter";
import SiteHeader from "../components/SiteHeader";
import { getLibraryManifest } from "../lib/chapters";

export default function HomePage() {
  const library = getLibraryManifest();

  return (
    <main className="site-shell">
      <SiteHeader bookCount={library.summary.books} />

      <section className="library-hero has-banner">
        <div className="hero-copy">
          <span className="eyebrow">MoonRead</span>
          <h1>ชั้นนิยาย</h1>
          <p>
            รวมนิยายแปลไทยที่พร้อมอ่าน จัดหน้าให้อ่านยาวได้สบาย
            เลือกเรื่องที่สนใจแล้วเริ่มอ่านได้เลย
          </p>
        </div>
      </section>

      <section className="status-band" aria-label="สถานะคลังนิยาย">
        {library.books.map((book) => (
          <div key={book.slug}>
            <strong>{book.summary.available}</strong>
            <span>{book.title}</span>
          </div>
        ))}
        <div>
          <strong>{library.summary.available}</strong>
          <span>ตอนพร้อมอ่านทั้งหมด</span>
        </div>
        <div>
          <strong>{library.summary.books}</strong>
          <span>เรื่องในคลัง</span>
        </div>
      </section>

      <section className="library-strip">
        <div className="section-heading">
          <span><BookOpen size={18} /> นิยายทั้งหมด</span>
        </div>

        <div className="library-grid">
          {library.books.map((book) => (
            <article className="library-feature" key={book.slug}>
              <div className={`library-cover${!book.cover || book.cover.includes('logo') ? ' logo-cover' : ''}`}>
                <Image src={book.cover || "/images/moonread-logo.svg"} alt="" fill sizes="160px" />
              </div>
              <div className="library-copy">
                <h2>{book.title}</h2>
                {book.thaiTitle && book.thaiTitle !== book.title ? (
                  <p className="library-thai-title">{book.thaiTitle}</p>
                ) : null}
                <p className="library-synopsis">{book.synopsis}</p>
                <div className="library-meta">
                  <span><Sparkles size={16} /> {book.tags.join(" · ")}</span>
                  <span><Clock3 size={16} /> {book.summary.available} ตอนพร้อมอ่าน</span>
                </div>
              </div>
              <div className="library-actions">
                <Link className="primary-action" href={book.href}>
                  หน้านิยาย
                  <ArrowRight size={18} />
                </Link>
                {book.firstChapter ? (
                  <Link className="secondary-action" href={book.firstChapter.href}>
                    เริ่มอ่าน
                  </Link>
                ) : null}
              </div>
            </article>
          ))}
        </div>
      </section>

      <SiteFooter />
    </main>
  );
}
