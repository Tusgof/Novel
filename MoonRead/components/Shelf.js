"use client";

import Link from "next/link";
import { Heart, Bookmark, BookOpen, History as HistoryIcon, BookmarkX } from "lucide-react";
import { useReaderStore } from "../lib/reader-store";
import { getBookTitlePair } from "../lib/book-titles";
import { BookCard, ResumeCard, EmptyState } from "./BookGrid";

function chLabel(n) { return `ตอน ${String(n).padStart(3, "0")}`; }

export function ShelfView({ books }) {
  const store = useReaderStore();
  const favBooks = books.filter((b) => store.isFavorite(b.slug));
  const marked = books
    .map((b) => ({ book: b, marks: store.bookmarksFor(b.slug) }))
    .filter((x) => x.marks.length);

  const nothing = !favBooks.length && !marked.length;

  return (
    <div className="page shell">
      <section className="section" style={{ marginTop: 24 }}>
        <div className="section-head"><h2><Heart size={20} /> รายการโปรด</h2></div>
        {favBooks.length ? (
          <div className="book-grid">{favBooks.map((b) => <BookCard key={b.slug} book={b} />)}</div>
        ) : (
          <p className="muted-line">แตะรูปหัวใจบนปกนิยายเพื่อบันทึกเรื่องโปรดไว้ที่นี่</p>
        )}
      </section>

      <section className="section">
        <div className="section-head"><h2><Bookmark size={20} /> ที่คั่นตอน</h2></div>
        {marked.length ? marked.map(({ book, marks }) => {
          const { title } = getBookTitlePair(book);

          return (
            <div key={book.slug} className="mark-group">
              <div className="mark-group-head"><BookOpen size={16} /> {title}</div>
              <div className="toc-list">
                {marks.map((m) => (
                  <Link key={m.id} className="ch-row" href={m.href}>
                    <span className="num">{String(m.number).padStart(3, "0")}</span>
                    <span className="ct"><small>{chLabel(m.number)}</small><strong>{m.title}</strong></span>
                    <span className="cm" />
                    <button className="ch-star on" type="button" aria-label="นำที่คั่นออก"
                      onClick={(e) => { e.preventDefault(); e.stopPropagation(); store.toggleBookmark(book.slug, m); }}>
                      <BookmarkX size={16} />
                    </button>
                  </Link>
                ))}
              </div>
            </div>
          );
        }) : <p className="muted-line">ยังไม่มีตอนที่คั่นไว้</p>}
      </section>

      {nothing ? (
        <EmptyState art="cat-sleeping" title="ชั้นหนังสือยังว่างอยู่">บันทึกเรื่องโปรดและคั่นตอนที่ชอบ แล้วทุกอย่างจะมารวมกันที่นี่</EmptyState>
      ) : null}
    </div>
  );
}

export function HistoryView({ books }) {
  const store = useReaderStore();
  const items = store.history()
    .map((h) => ({ h, book: books.find((b) => b.slug === h.slug) }))
    .filter((x) => x.book);

  return (
    <div className="page shell">
      <section className="section" style={{ marginTop: 24 }}>
        <div className="section-head"><h2><HistoryIcon size={20} /> ประวัติการอ่าน</h2></div>
        {items.length ? (
          <div className="history-grid">
            {items.map(({ h, book }) => <ResumeCard key={h.slug} book={book} entry={h} />)}
          </div>
        ) : (
          <EmptyState art="cat-sleeping" title="ยังไม่มีประวัติการอ่าน">เริ่มอ่านสักเรื่อง แล้ว MoonRead จะจำไว้ให้ว่าคุณอ่านถึงไหน</EmptyState>
        )}
      </section>
    </div>
  );
}
