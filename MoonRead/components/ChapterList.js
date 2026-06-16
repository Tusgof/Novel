import Link from "next/link";
import { CheckCircle2, Clock3, Lock, XCircle } from "lucide-react";

function statusIcon(status) {
  if (status === "available") return <CheckCircle2 size={18} />;
  if (status === "rejected") return <XCircle size={18} />;
  return <Lock size={18} />;
}

function statusLabel(chapter) {
  if (chapter.status === "available") return `${chapter.readingMinutes} นาที`;
  if (chapter.status === "rejected") return "รอตรวจไฟล์";
  return "ยังไม่มีตอน";
}

function chapterLabel(chapter) {
  return `ตอน ${String(chapter.number).padStart(3, "0")}`;
}

export default function ChapterList({ chapters, compact = false }) {
  return (
    <div className={compact ? "chapter-list compact" : "chapter-list"}>
      {chapters.map((chapter) => {
        const displayTitle = chapter.status === "available" ? chapter.title : `${chapterLabel(chapter)} ยังไม่พร้อมอ่าน`;
        const row = (
          <>
            <span className={`chapter-state ${chapter.status}`}>{statusIcon(chapter.status)}</span>
            <span className="chapter-main">
              <small>{chapterLabel(chapter)}</small>
              <strong>{displayTitle}</strong>
            </span>
            <span className="chapter-meta">
              <Clock3 size={15} />
              {statusLabel(chapter)}
            </span>
          </>
        );

        if (chapter.status !== "available") {
          return (
            <div className="chapter-row disabled" key={chapter.id} aria-disabled="true">
              {row}
            </div>
          );
        }

        return (
          <Link className="chapter-row" href={chapter.href} key={chapter.id}>
            {row}
          </Link>
        );
      })}
    </div>
  );
}
