"use client";

import { useState } from "react";
import Link from "next/link";
import {
  BookOpenText, Clock3, Bookmark, Heart,
} from "lucide-react";
import { useReaderStore } from "../lib/reader-store";
import { getBookTitlePair } from "../lib/book-titles";
import { Cover, EmptyState } from "./BookGrid";
import ChapterFinder from "./ChapterFinder";
import { chapterNumber, episodeLabel as chLabel } from "../lib/chapter-number";
import { bookSynopsis } from "../lib/book-synopsis";

function ChapterRow({ slug, chapter, reading, store, review = false }) {
  const starred = store.isBookmarked(slug, chapter.id);
  const disabled = chapter.status !== "available";

  const inner = (
    <>
      <span className="num">{String(chapterNumber(chapter)).padStart(3, "0")}</span>
      <span className="ct"><small>{chLabel(chapter)}{!disabled ? <> · ผู้แปล <span className="translator">{chapter.translator}</span></> : null}</small><strong>{disabled ? `${chLabel(chapter)} ยังไม่พร้อมอ่าน` : chapter.title}</strong></span>
      <span className="cm"><Clock3 size={13} /> {disabled ? "เร็วๆ นี้" : `${chapter.readingMinutes} น.`}</span>
    </>
  );

  if (disabled) return <div className="ch-row disabled" aria-disabled="true">{inner}</div>;
  return (
    <div className={`ch-row${reading ? " reading" : ""}`}>
      <Link className="chapter-link" prefetch={false} aria-current={reading ? "location" : undefined} href={review ? `${chapter.href}?review=1` : chapter.href}>{inner}</Link>
      <button className={`ch-star${starred ? " on" : ""}`} type="button" aria-label={`คั่นหน้า ${chLabel(chapter)}`} aria-pressed={starred} onClick={() => store.toggleBookmark(slug, chapter)}>
        <Bookmark size={16} fill={starred ? "currentColor" : "none"} />
      </button>
    </div>
  );
}

export default function BookDetail({ book, chapters }) {
  const store = useReaderStore();
  const [tab, setTab] = useState("toc");

  const available = chapters.filter((c) => c.status === "available");
  const soon = available.length === 0;
  const saved = store.getProgress(book.slug);
  const prog = saved && available.some((chapter) => chapter.id === saved.chapterId) ? saved : null;

  const firstHref = available[0]?.href;
  const latestHref = available.at(-1)?.href;

  const marks = store.bookmarksFor(book.slug);
  const { title, thaiTitle } = getBookTitlePair(book);
  const favorite = store.isFavorite(book.slug);
  const synopsis = bookSynopsis(book);

  return (
    <main className="page shell" id="main-content" tabIndex={-1}>
      <section className="detail-hero">
        <div className="bg" aria-hidden="true"><Cover book={book} sizes="220px" /></div>
        <div className="detail-grid">
          <div className="detail-cover"><Cover book={book} sizes="(max-width: 860px) 150px, 220px" priority /></div>
          <div className="detail-info">
            <span className="eyebrow gold">{(book.tags || []).join(" · ")}</span>
            <h1>{title}</h1>
            <div className="sub">{thaiTitle}{book.author && book.author !== "—" ? ` · ${book.author}` : ""}</div>
            <div className="detail-stats">
              <div className="st"><b>{soon ? book.summary?.total ?? chapters.length : available.length}</b><span>{soon ? "ตอน (เร็วๆ นี้)" : "ตอนพร้อมอ่าน"}</span></div>
              {prog ? <div className="st"><b>{prog.percent}%</b><span>อ่านถึง {chLabel(prog)}</span></div> : null}
            </div>
            <div className="detail-tags">{(book.tags || []).map((g) => <span className="tag" key={g}>{g}</span>)}</div>
            <div className="detail-actions">
              {soon ? null : prog ? (
                <>
                  <Link className="pill-btn primary" href={prog.href}><BookOpenText size={18} /> อ่านต่อ {chLabel(prog)}</Link>
                  {firstHref ? <Link prefetch={false} className="pill-btn ghost" href={`${firstHref}?start=1`}>เริ่มใหม่จากตอนแรก</Link> : null}
                </>
              ) : (
                <>
                  {firstHref ? <Link className="pill-btn primary" href={firstHref}><BookOpenText size={18} /> เริ่มอ่าน</Link> : null}
                  {latestHref ? <Link className="pill-btn ghost" href={latestHref}>อ่านตอนล่าสุด</Link> : null}
                </>
              )}
              <button className="pill-btn ghost" type="button" aria-pressed={favorite} onClick={() => store.toggleFavorite(book.slug)}><Heart size={17} fill={favorite ? "currentColor" : "none"} /> {favorite ? "บันทึกแล้ว" : "บันทึกเรื่องโปรด"}</button>
            </div>
          </div>
        </div>
      </section>

      {soon ? (
        <EmptyState art="cat-sleeping" title="กำลังเตรียมแปล">
          เรื่องนี้ยังไม่มีตอนที่พร้อมอ่าน
        </EmptyState>
      ) : (
        <>
          <div className="tabs">
            <button className={`tab${tab === "toc" ? " on" : ""}`} aria-pressed={tab === "toc"} onClick={() => setTab("toc")}>สารบัญ</button>
            <button className={`tab${tab === "about" ? " on" : ""}`} aria-pressed={tab === "about"} onClick={() => setTab("about")}>เรื่องย่อ</button>
            <button className={`tab${tab === "marks" ? " on" : ""}`} aria-pressed={tab === "marks"} onClick={() => setTab("marks")}>ที่คั่น{marks.length ? ` (${marks.length})` : ""}</button>
          </div>

          {tab === "toc" && (
            <div className="section" style={{ marginTop: 20 }}>
              <ChapterFinder chapters={chapters} renderRows={(filtered) => (
                <div className="toc-list">{filtered.map((c) => (
                  <ChapterRow key={c.id} slug={book.slug} chapter={c} store={store} reading={prog?.chapterId === c.id} />
                ))}</div>
              )} />
            </div>
          )}

          {tab === "about" && (
            <div className="section about" style={{ marginTop: 20 }}>
              {synopsis ? <p>{synopsis}</p> : <><p>เรื่องนี้ยังไม่มีเรื่องย่อ</p>{firstHref ? <Link className="pill-btn ghost" prefetch={false} href={`${firstHref}?review=1`}>ลองอ่านตอนแรก</Link> : null}</>}
            </div>
          )}

          {tab === "marks" && (
            <div className="section" style={{ marginTop: 20 }}>
              {marks.length ? (
                <div className="toc-list">
                  {marks.map((m) => {
                    const c = chapters.find((x) => x.id === m.id && x.status === "available");
                    return c ? <ChapterRow key={m.id} slug={book.slug} chapter={c} store={store} reading={prog?.chapterId === m.id} review /> : null;
                  })}
                </div>
              ) : (
                <EmptyState art="cat-sleeping" title="ยังไม่มีที่คั่น">แตะไอคอนคั่นหน้าข้างตอนใดก็ได้ เพื่อบันทึกไว้กลับมาอ่านภายหลัง</EmptyState>
              )}
            </div>
          )}
        </>
      )}
    </main>
  );
}
