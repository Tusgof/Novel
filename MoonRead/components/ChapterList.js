"use client";

import { Bookmark, CheckCircle2, Clock3, Lock, XCircle } from "lucide-react";
import ChapterFinder from "./ChapterFinder";
import { chapterNumber } from "../lib/chapter-number";
import { useReaderStore } from "../lib/reader-store";

export default function ChapterList({ chapters, slug, initialSearch }) {
  const store = useReaderStore();
  return <ChapterFinder chapters={chapters} initialSearch={initialSearch} renderRows={(filtered) => (
    <div className="toc-list">
      {filtered.map((chapter) => {
        const available = chapter.status === "available";
        const number = String(chapterNumber(chapter)).padStart(3, "0");
        const marked = available && store.isBookmarked(slug, chapter.id);
        const review = marked && store.getProgress(slug)?.chapterId !== chapter.id;
        const Icon = marked ? Bookmark : available ? CheckCircle2 : chapter.status === "rejected" ? XCircle : Lock;
        const inner = <>
          <span className="num">{number}</span>
          <span className="ct"><small>ตอน {number}{available ? <> · ผู้แปล <span className="translator">{chapter.translator}</span></> : null}</small><strong>{available ? chapter.title : `ตอน ${number} ยังไม่พร้อมอ่าน`}</strong></span>
          <span className="cm"><Clock3 size={13} /> {available ? `${chapter.readingMinutes} น.` : chapter.status === "rejected" ? "รอตรวจไฟล์" : "ยังไม่พร้อม"}</span>
          <span className={`ch-state ${chapter.status}`}><Icon size={18} fill={marked ? "currentColor" : "none"} aria-label={marked ? "คั่นไว้" : undefined} role={marked ? "img" : undefined} /></span>
        </>;
        return available ? <a id={`chapter-${chapter.id}`} className="ch-row" href={review ? `${chapter.href}?review=1` : chapter.href} key={chapter.id}>{inner}</a>
          : <div className="ch-row disabled" key={chapter.id} aria-disabled="true" data-gap={chapter.inferredGap || undefined}>{inner}</div>;
      })}
    </div>
  )} />;
}
