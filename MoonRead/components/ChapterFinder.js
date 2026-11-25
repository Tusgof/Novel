"use client";

import { useId, useState } from "react";
import { Search, X } from "lucide-react";
import { filterChapters } from "../lib/chapter-search";
import { chapterNumber } from "../lib/chapter-number";

export default function ChapterFinder({ chapters, renderRows }) {
  const [query, setQuery] = useState("");
  const [recent, setRecent] = useState(false);
  const [range, setRange] = useState("");
  const inputId = useId();
  const ranges = [...new Set(chapters.map((chapter) => Math.floor((chapterNumber(chapter) - 1) / 50) * 50 + 1))];
  const visible = range && !query.trim() ? chapters.filter((chapter) => chapterNumber(chapter) >= +range && chapterNumber(chapter) < +range + 50) : chapters;
  const matches = filterChapters(visible, query);
  const filtered = recent ? [...matches].reverse() : matches;

  return (
    <>
      <div className="toc-tools">
        <div className="searchbox toc-search">
          <span className="ic"><Search size={17} /></span>
          <input id={inputId} type="search" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="เลขตอนหรือชื่อตอน" aria-label="ค้นหาตอน" />
          {query ? <button type="button" className="ic clear" aria-label="ล้างคำค้นตอน" onClick={() => { setQuery(""); document.getElementById(inputId)?.focus(); }}><X size={16} /></button> : null}
        </div>
        <select aria-label="เรียงตอน" className="toc-select" value={recent ? "recent" : "first"} onChange={(e) => setRecent(e.target.value === "recent")}>
          <option value="first">ตอนแรกก่อน</option>
          <option value="recent">ตอนล่าสุดก่อน</option>
        </select>
        {ranges.length > 1 ? <select aria-label="ช่วงตอน" className="toc-select" value={query.trim() ? "" : range} onChange={(e) => { setQuery(""); setRange(e.target.value); }}>
          <option value="">ทุกช่วงตอน</option>
          {ranges.map((first) => <option key={first} value={first}>{first}–{Math.min(first + 49, chapterNumber(chapters.at(-1)))}</option>)}
        </select> : null}
      </div>
      <p role="status" className="muted-line">{filtered.length ? `แสดง ${filtered.length} ตอน` : "ไม่พบตอนที่ค้นหา ลองพิมพ์เลขตอนหรือคำในชื่อตอน"}</p>
      {renderRows(filtered)}
    </>
  );
}
