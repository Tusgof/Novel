"use client";

import { useState } from "react";
import Link from "next/link";
import {
  ArrowRight, BookOpenText, BellRing, Check, Clock3, Search, Bookmark,
} from "lucide-react";
import { useReaderStore } from "../lib/reader-store";
import { Cover, EmptyState } from "./BookGrid";

function chLabel(n) { return `ตอน ${String(n).padStart(3, "0")}`; }

function ChapterRow({ slug, chapter, reading, read }) {
  const store = useReaderStore();
  const starred = store.isBookmarked(slug, chapter.id);
  const disabled = chapter.status !== "available";

  const inner = (
    <>
      <span className={`num${read ? " read" : ""}`}>{read ? <Check size={16} /> : String(chapter.number).padStart(3, "0")}</span>
      <span className="ct"><small>{chLabel(chapter.number)}</small><strong>{disabled ? `${chLabel(chapter.number)} ยังไม่พร้อมอ่าน` : chapter.title}</strong></span>
      <span className="cm"><Clock3 size={13} /> {disabled ? "เร็วๆ นี้" : `${chapter.readingMinutes} น.`}</span>
      {!disabled ? (
        <button className={`ch-star${starred ? " on" : ""}`} type="button" aria-label="คั่นหน้า"
          onClick={(e) => { e.preventDefault(); e.stopPropagation(); store.toggleBookmark(slug, chapter); }}>
          <Bookmark size={16} fill={starred ? "currentColor" : "none"} />
        </button>
      ) : <span />}
    </>
  );

  if (disabled) return <div className="ch-row disabled" aria-disabled="true">{inner}</div>;
  return <Link className={`ch-row${reading ? " reading" : ""}`} href={chapter.href}>{inner}</Link>;
}

export default function BookDetail({ book, chapters }) {
  const store = useReaderStore();
  const [tab, setTab] = useState("toc");
  const [q, setQ] = useState("");

  const available = chapters.filter((c) => c.status === "available");
  const soon = available.length === 0;
  const prog = store.getProgress(book.slug);
  const readUpTo = prog ? available.findIndex((c) => c.id === prog.chapterId) : -1;

  const firstHref = available[0]?.href;
  const latestHref = available.at(-1)?.href;

  const filtered = q
    ? chapters.filter((c) => (c.title || "").toLowerCase().includes(q.toLowerCase()) || String(c.number).includes(q))
    : chapters;
  const marks = store.bookmarksFor(book.slug);

  return (
    <div className="page shell">
      <section className="detail-hero">
        <div className="bg" aria-hidden="true"><Cover book={book} /></div>
        <div className="detail-grid">
          <div className="detail-cover"><Cover book={book} /></div>
          <div className="detail-info">
            <span className="eyebrow gold">{(book.tags || []).join(" · ")}</span>
            <h1>{book.title}</h1>
            <div className="sub">{book.thaiTitle}{book.author && book.author !== "—" ? ` · ${book.author}` : ""}</div>
            <div className="detail-stats">
              <div className="st"><b>{soon ? book.summary?.total ?? chapters.length : available.length}</b><span>{soon ? "ตอน (เร็วๆ นี้)" : "ตอนพร้อมอ่าน"}</span></div>
              {prog ? <div className="st"><b>{prog.percent}%</b><span>อ่านถึง {chLabel(prog.number)}</span></div> : null}
            </div>
            <div className="detail-tags">{(book.tags || []).map((g) => <span className="tag" key={g}>{g}</span>)}</div>
            <div className="detail-actions">
              {soon ? (
                <button className="pill-btn ghost" type="button"><BellRing size={17} /> แจ้งเตือนเมื่อมีตอน</button>
              ) : prog ? (
                <>
                  <Link className="pill-btn primary" href={prog.href}><BookOpenText size={18} /> อ่านต่อ {chLabel(prog.number)}</Link>
                  {firstHref ? <Link className="pill-btn ghost" href={firstHref}>เริ่มใหม่จากตอนแรก</Link> : null}
                </>
              ) : (
                <>
                  {firstHref ? <Link className="pill-btn primary" href={firstHref}><BookOpenText size={18} /> เริ่มอ่าน</Link> : null}
                  {latestHref ? <Link className="pill-btn ghost" href={latestHref}>อ่านตอนล่าสุด</Link> : null}
                </>
              )}
            </div>
          </div>
        </div>
      </section>

      {soon ? (
        <EmptyState art="cat-sleeping" title="กำลังเตรียมแปล">
          เรื่องนี้ยังอยู่ระหว่างการแปลและตรวจไฟล์ กดแจ้งเตือนไว้ แล้วเจ้าเหมียวจะส่งข่าวให้เมื่อตอนแรกพร้อมอ่าน
        </EmptyState>
      ) : (
        <>
          <div className="tabs">
            <button className={`tab${tab === "toc" ? " on" : ""}`} onClick={() => setTab("toc")}>สารบัญ</button>
            <button className={`tab${tab === "about" ? " on" : ""}`} onClick={() => setTab("about")}>เรื่องย่อ</button>
            <button className={`tab${tab === "marks" ? " on" : ""}`} onClick={() => setTab("marks")}>ที่คั่น{marks.length ? ` (${marks.length})` : ""}</button>
          </div>

          {tab === "toc" && (
            <div className="section" style={{ marginTop: 20 }}>
              <div className="toc-tools">
                <div className="searchbox" style={{ minWidth: 0, flex: 1 }}>
                  <span className="ic"><Search size={17} /></span>
                  <input value={q} onChange={(e) => setQ(e.target.value)} placeholder="ค้นหาตอน เช่น ชื่อตอน หรือเลขตอน" aria-label="ค้นหาตอน" />
                </div>
              </div>
              <div className="toc-list">
                {filtered.map((c) => (
                  <ChapterRow key={c.id} slug={book.slug} chapter={c}
                    reading={prog && prog.chapterId === c.id}
                    read={readUpTo >= 0 && c.status === "available" && available.findIndex((a) => a.id === c.id) < readUpTo} />
                ))}
                {!filtered.length ? <EmptyState art="cat-sleeping" title="ไม่พบตอนที่ค้นหา">ลองพิมพ์เลขตอน หรือคำในชื่อตอนดูนะ</EmptyState> : null}
              </div>
            </div>
          )}

          {tab === "about" && (
            <div className="section about" style={{ marginTop: 20 }}>
              <p>{book.synopsis}</p>
            </div>
          )}

          {tab === "marks" && (
            <div className="section" style={{ marginTop: 20 }}>
              {marks.length ? (
                <div className="toc-list">
                  {marks.map((m) => {
                    const c = chapters.find((x) => x.id === m.id) || m;
                    return <ChapterRow key={m.id} slug={book.slug} chapter={{ ...c, status: "available" }} reading={prog && prog.chapterId === m.id} read={false} />;
                  })}
                </div>
              ) : (
                <EmptyState art="cat-sleeping" title="ยังไม่มีที่คั่น">แตะไอคอนคั่นหน้าข้างตอนใดก็ได้ เพื่อบันทึกไว้กลับมาอ่านภายหลัง</EmptyState>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}
