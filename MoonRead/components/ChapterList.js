"use client";

import Link from "next/link";
import { CheckCircle2, Clock3, Lock, XCircle } from "lucide-react";
import ChapterFinder from "./ChapterFinder";
import { chapterNumber } from "../lib/chapter-number";

export default function ChapterList({ chapters }) {
  return <ChapterFinder chapters={chapters} renderRows={(filtered) => (
    <div className="toc-list">
      {filtered.map((chapter) => {
        const available = chapter.status === "available";
        const number = String(chapterNumber(chapter)).padStart(3, "0");
        const Icon = available ? CheckCircle2 : chapter.status === "rejected" ? XCircle : Lock;
        const inner = <>
          <span className="num">{number}</span>
          <span className="ct"><small>ตอน {number}{available ? <> · ผู้แปล <span className="translator">{chapter.translator}</span></> : null}</small><strong>{available ? chapter.title : `ตอน ${number} ยังไม่พร้อมอ่าน`}</strong></span>
          <span className="cm"><Clock3 size={13} /> {available ? `${chapter.readingMinutes} น.` : chapter.status === "rejected" ? "รอตรวจไฟล์" : "ยังไม่พร้อม"}</span>
          <span className={`ch-state ${chapter.status}`}><Icon size={18} /></span>
        </>;
        return available ? <Link className="ch-row" href={chapter.href} key={chapter.id} prefetch={false}>{inner}</Link>
          : <div className="ch-row disabled" key={chapter.id} aria-disabled="true">{inner}</div>;
      })}
    </div>
  )} />;
}
