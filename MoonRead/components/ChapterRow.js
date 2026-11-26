import { Bookmark, Clock3 } from "lucide-react";
import { chapterNumber, episodeLabel } from "../lib/chapter-number";

export default function ChapterRow({ slug, chapter, reading, store, bookmark, linkId }) {
  const starred = store.isBookmarked(slug, chapter.id);
  const unavailable = chapter.status !== "available";
  const label = episodeLabel(chapter);
  const inner = (
    <>
      <span className="num">{String(chapterNumber(chapter)).padStart(3, "0")}</span>
      <span className="ct">
        <small>{label}{bookmark ? ` · ${bookmark.label}` : !unavailable ? <> · ผู้แปล <span className="translator">{chapter.translator}</span></> : null}</small>
        <strong>{unavailable ? `${label} ยังไม่พร้อมอ่าน` : chapter.title}</strong>
      </span>
      <span className="cm"><Clock3 size={13} /> {unavailable ? "ยังไม่พร้อม" : `${chapter.readingMinutes} น.`}</span>
    </>
  );

  if (unavailable) return <div className="ch-row disabled" aria-disabled="true" data-gap={chapter.inferredGap || undefined}>{inner}</div>;
  return (
    <div className={`ch-row${reading ? " reading" : ""}`}>
      <a id={linkId} className="chapter-link" aria-current={reading ? "location" : undefined} href={bookmark?.href || chapter.href}>{inner}</a>
      <button className={`ch-star${starred ? " on" : ""}`} type="button" disabled={!store.ready} aria-label={`คั่นหน้า ${label}`} aria-pressed={starred} onClick={() => store.toggleBookmark(slug, chapter)}>
        <Bookmark size={16} fill={starred ? "currentColor" : "none"} aria-hidden="true" />
      </button>
    </div>
  );
}
