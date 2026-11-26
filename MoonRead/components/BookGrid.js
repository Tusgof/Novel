"use client";

import Link from "next/link";
import Image from "next/image";
import { useId } from "react";
import { BookOpen, Sparkles, Heart, Clock3, Hourglass, Swords } from "lucide-react";
import { useReaderStore } from "../lib/reader-store";
import { getBookTitlePair } from "../lib/book-titles";
import { episodeLabel } from "../lib/chapter-number";
import { bookSynopsis } from "../lib/book-synopsis";

function isLogo(cover) { return !cover || cover.includes("logo"); }
const coverMarks = { "one-hit-kill-swordmaster": Swords, "ten-day-ultimatum": Hourglass };

export function Cover({ book, sizes = "(max-width: 860px) 45vw, 220px", priority = false }) {
  const { title, thaiTitle } = getBookTitlePair(book);

  if (isLogo(book.cover)) {
    const Icon = coverMarks[book.slug];
    return (
      <div className="cover-fallback" aria-hidden="true" data-series={book.slug}>
        {Icon ? <Icon size={44} strokeWidth={1.5} /> : <Image src="/icon.svg" alt="" width={52} height={52} />}
        <span className="ft">{thaiTitle || title}</span>
      </div>
    );
  }
  return <Image src={book.cover} alt="" fill sizes={sizes} fetchPriority={priority ? "high" : undefined} loading={priority ? "eager" : "lazy"} />;
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
  const synopsis = bookSynopsis(book);
  const headingId = useId();

  return (
    <article className="book-card">
      <a href={book.href} aria-labelledby={headingId}>
      <div className="cover">
        <Cover book={book} />
      </div>
      <div className="info">
        <h3 className="t" id={headingId}>{thaiTitle || title}</h3>
        {thaiTitle ? <div className="th" lang="en">{title}</div> : null}
        <div className="meta">
          <span><BookOpen size={13} /> {available} ตอน</span>
          {book.tags?.[0] ? <span><Sparkles size={13} /> {book.tags[0]}</span> : null}
        </div>
        {synopsis ? <p className="synopsis-preview">{synopsis}</p> : null}
        {prog ? <div style={{ marginTop: 8 }}><ProgressBar percent={prog.percent} /></div> : null}
      </div>
      </a>
      <button className={`fav${fav ? " on" : ""}`} type="button" aria-label={`รายการโปรด: ${title}`} aria-pressed={fav} onClick={() => store.toggleFavorite(book.slug)}>
        <Heart size={19} fill={fav ? "currentColor" : "none"} />
      </button>
    </article>
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
    <Link prefetch={false} className="resume" href={entry.href}>
      <div className="thumb"><Cover book={book} sizes="64px" /></div>
      <div className="meta">
        <div className="t">{title}</div>
        <div className="c">{episodeLabel(entry)} · {entry.title}</div>
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
