"use client";

import Link from "next/link";
import { Heart, Bookmark, BookOpen, History as HistoryIcon, BookmarkX } from "lucide-react";
import { useReaderStore } from "../lib/reader-store";
import { getBookTitlePair } from "../lib/book-titles";
import { BookCard, ResumeCard, EmptyState } from "./BookGrid";
import { chapterNumber, episodeLabel } from "../lib/chapter-number";
import { bookmarkDestination } from "../lib/bookmark-links";

export function ShelfView({ books }) {
  const store = useReaderStore();
  const favBooks = books.filter((b) => store.isFavorite(b.slug));
  const marked = books
    .map((b) => ({ book: b, marks: store.bookmarksFor(b.slug) }))
    .filter((x) => x.marks.length);

  const nothing = !favBooks.length && !marked.length;

  return (
    <main className="page shell" id="main-content" tabIndex={-1}>
      <div className="section-head shelf-heading"><h1>ชั้นหนังสือ</h1><a className="more" href="#chapter-bookmarks">ไปที่ที่คั่นตอน</a></div>
      <section className="section" style={{ marginTop: 24 }}>
        <div className="section-head"><h2><Heart size={20} /> รายการโปรด</h2></div>
        {!store.ready ? <p className="muted-line" role="status">กำลังโหลดรายการโปรด…</p> : favBooks.length ? (
          <div className="book-grid">{favBooks.map((b) => <BookCard key={b.slug} book={b} />)}</div>
        ) : (
          <p className="muted-line">แตะรูปหัวใจบนปกนิยายเพื่อบันทึกเรื่องโปรดไว้ที่นี่</p>
        )}
      </section>

      <section className="section" id="chapter-bookmarks">
        <div className="section-head"><h2><Bookmark size={20} /> ที่คั่นตอน</h2></div>
        {!store.ready ? <p className="muted-line" role="status">กำลังโหลดที่คั่นตอน…</p> : marked.length ? marked.map(({ book, marks }) => {
            const { title } = getBookTitlePair(book);
            const progress = store.getProgress(book.slug);

          return (
            <div key={book.slug} className="mark-group">
              <div className="mark-group-head"><BookOpen size={16} /> {title}</div>
              <div className="toc-list">
                {marks.map((m) => {
                  const bookmark = bookmarkDestination(m, progress);
                  return (
                  <div key={m.id} className="ch-row">
                    <Link className="chapter-link" href={bookmark.href} prefetch={false}>
                    <span className="num">{String(chapterNumber(m)).padStart(3, "0")}</span>
                     <span className="ct"><small>{episodeLabel(m)} · {bookmark.label}</small><strong>{m.title}</strong></span>
                    <span className="cm" />
                    </Link>
                    <button className="ch-star on" type="button" aria-label={`นำที่คั่น ${episodeLabel(m)} ออก`}
                      onClick={() => store.toggleBookmark(book.slug, m)}>
                      <BookmarkX size={16} />
                    </button>
                  </div>
                  );
                })}
              </div>
            </div>
          );
        }) : <p className="muted-line">ยังไม่มีตอนที่คั่นไว้</p>}
      </section>

      {store.ready && nothing ? (
        <EmptyState art="cat-sleeping" title="ชั้นหนังสือยังว่างอยู่">บันทึกเรื่องโปรดและคั่นตอนที่ชอบ แล้วทุกอย่างจะมารวมกันที่นี่</EmptyState>
      ) : null}
    </main>
  );
}

export function HistoryView({ books }) {
  const store = useReaderStore();
  const items = store.history()
    .map((h) => ({ h, book: books.find((b) => b.slug === h.slug) }))
    .filter((x) => x.book);

  return (
    <main className="page shell" id="main-content" tabIndex={-1}>
      <section className="section" style={{ marginTop: 24 }}>
        <div className="section-head"><h1><HistoryIcon size={20} /> ประวัติการอ่าน</h1></div>
        {!store.ready ? <p className="muted-line" role="status">กำลังโหลดประวัติการอ่าน…</p> : items.length ? (
          <div className="history-grid">
            {items.map(({ h, book }) => <ResumeCard key={h.slug} book={book} entry={h} />)}
          </div>
        ) : (
          <EmptyState art="cat-sleeping" title="ยังไม่มีประวัติการอ่าน">เริ่มอ่านสักเรื่อง แล้ว MoonRead จะจำไว้ให้ว่าคุณอ่านถึงไหน</EmptyState>
        )}
      </section>
    </main>
  );
}
