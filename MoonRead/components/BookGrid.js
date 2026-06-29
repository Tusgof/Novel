"use client";

import Link from "next/link";
import Image from "next/image";
import { BookOpen, Sparkles, Heart, Clock3 } from "lucide-react";
import { useReaderStore } from "../lib/reader-store";
import { getBookTitlePair } from "../lib/book-titles";

function isLogo(cover) { return !cover || cover.includes("logo"); }

export function Cover({ book }) {
  const { title } = getBookTitlePair(book);

  if (isLogo(book.cover)) {
    return (
      <div className="cover-fallback" style={{ background: `linear-gradient(155deg, ${book.accent || "#1d2740"}, #0d1320)` }}>
        <Image src="/icon.svg" alt="" width={52} height={52} />
        <span className="ft">{title}</span>
      </div>
    );
  }
  return <Image src={book.cover} alt="" fill sizes="(max-width: 860px) 45vw, 200px" />;
}

export function ProgressBar({ percent }) {
  return <div className="progress"><i style={{ width: `${Math.max(3, percent)}%` }} /></div>;
}

export function BookCard({ book }) {
  const store = useReaderStore();
  const fav = store.isFavorite(book.slug);
  const prog = store.getProgress(book.slug);
  const available = book.summary?.available ?? 0;
  const { title, thaiTitle } = getBookTitlePair(book);

  return (
    <Link className="book-card" href={book.href}>
      <div className="cover">
        <Cover book={book} />
        <button
          className={`fav${fav ? " on" : ""}`}
          type="button"
          aria-label={fav ? "นำออกจากรายการโปรด" : "เพิ่มในรายการโปรด"}
          onClick={(e) => { e.preventDefault(); e.stopPropagation(); store.toggleFavorite(book.slug); }}
        >
          <Heart size={17} fill={fav ? "currentColor" : "none"} />
        </button>
      </div>
      <div className="info">
        <div className="t">{title}</div>
        {thaiTitle ? <div className="th">{thaiTitle}</div> : null}
        <div className="meta">
          <span><BookOpen size={13} /> {available} ตอน</span>
          {book.tags?.[0] ? <span><Sparkles size={13} /> {book.tags[0]}</span> : null}
        </div>
        {prog ? <div style={{ marginTop: 8 }}><ProgressBar percent={prog.percent} /></div> : null}
      </div>
    </Link>
  );
}

function timeAgo(ts) {
  const m = Math.round((Date.now() - ts) / 60000);
  if (m < 1) return "เมื่อสักครู่";
  if (m < 60) return `${m} นาทีที่แล้ว`;
  const h = Math.round(m / 60);
  if (h < 24) return `${h} ชม.ที่แล้ว`;
  return `${Math.round(h / 24)} วันที่แล้ว`;
}

export function ResumeCard({ book, entry }) {
  const { title } = getBookTitlePair(book);

  return (
    <Link className="resume" href={entry.href}>
      <div className="thumb"><Cover book={book} /></div>
      <div className="meta">
        <div className="t">{title}</div>
        <div className="c">ตอน {String(entry.number).padStart(3, "0")} · {entry.title}</div>
        <div className="spacer" />
        <ProgressBar percent={entry.percent} />
        <div className="progress-row"><span>{entry.percent}%</span><span><Clock3 size={12} /> {timeAgo(entry.updatedAt)}</span></div>
      </div>
    </Link>
  );
}

export function EmptyState({ art = "cat-sleeping", title, children }) {
  return (
    <div className="empty">
      <Image src={`/images/${art}.png`} alt="" width={200} height={200} />
      <h3>{title}</h3>
      <p>{children}</p>
    </div>
  );
}
