"use client";

import { useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { LibraryBig, History, ChevronRight, Search, ArrowDownWideNarrow, X } from "lucide-react";
import Link from "next/link";
import Image from "next/image";
import { useReaderStore } from "../lib/reader-store";
import { BookCard, ResumeCard, EmptyState } from "./BookGrid";

const SORTS = [
  { id: "popular", label: "ยอดนิยม" },
  { id: "chapters", label: "ตอนเยอะสุด" },
  { id: "title", label: "ชื่อ ก-ฮ / A-Z" },
];

function Hero({ query, setQuery }) {
  return (
    <section className="hero">
      <Image className="hero-cat" src="/images/cat-walking.png" alt="" width={440} height={440} priority />
      <div className="hero-body">
        <span className="eyebrow">MoonRead · ชั้นนิยายแปลไทย</span>
        <h1>ค่ำคืนนี้<br />อ่านอะไรดี?</h1>
        <p>รวมนิยายแปลไทยที่จัดหน้าให้อ่านยาวได้สบายตา เลือกเรื่องโปรด คั่นหน้าไว้ แล้วกลับมาอ่านต่อได้ทุกเมื่อ</p>
        <form className="hero-search" onSubmit={(e) => e.preventDefault()} role="search">
          <div className="searchbox">
            <span className="ic"><Search size={20} /></span>
            <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="ค้นหานิยาย ผู้แต่ง หรือหมวด" aria-label="ค้นหานิยาย" />
            {query ? <button type="button" className="ic clear" onClick={() => setQuery("")} aria-label="ล้างคำค้น"><X size={16} /></button> : null}
          </div>
        </form>
      </div>
    </section>
  );
}

export default function Discover({ books, genres }) {
  const store = useReaderStore();
  const params = useSearchParams();
  const [query, setQuery] = useState(() => params.get("q") || "");
  const [active, setActive] = useState([]);
  const [sort, setSort] = useState("popular");

  const toggleGenre = (g) => setActive((gs) => (gs.includes(g) ? gs.filter((x) => x !== g) : [...gs, g]));

  const q = query.trim().toLowerCase();
  const list = useMemo(() => {
    let out = books.filter((b) => {
      const hay = `${b.title} ${b.thaiTitle || ""} ${b.author || ""} ${(b.tags || []).join(" ")}`.toLowerCase();
      const matchQ = !q || hay.includes(q);
      const matchG = !active.length || active.every((g) => (b.tags || []).includes(g));
      return matchQ && matchG;
    });
    if (sort === "title") out = [...out].sort((a, b) => a.title.localeCompare(b.title));
    if (sort === "chapters") out = [...out].sort((a, b) => (b.summary?.available || 0) - (a.summary?.available || 0));
    return out;
  }, [books, q, active, sort]);

  const filtering = q || active.length;

  const history = store.history()
    .map((h) => ({ h, book: books.find((b) => b.slug === h.slug) }))
    .filter((x) => x.book);

  return (
    <div className="page shell">
      {!filtering ? <Hero query={query} setQuery={setQuery} /> : (
        <div className="standalone-search">
          <div className="searchbox">
            <span className="ic"><Search size={18} /></span>
            <input autoFocus value={query} onChange={(e) => setQuery(e.target.value)} placeholder="ค้นหานิยาย ผู้แต่ง หรือหมวด" aria-label="ค้นหานิยาย" />
            {query ? <button type="button" className="ic clear" onClick={() => setQuery("")} aria-label="ล้างคำค้น"><X size={16} /></button> : null}
          </div>
        </div>
      )}

      {!filtering && history.length ? (
        <section className="section">
          <div className="section-head">
            <h2><History size={20} /> อ่านต่อจากที่ค้างไว้</h2>
            <Link className="more" href="/history">ดูทั้งหมด <ChevronRight size={15} /></Link>
          </div>
          <div className="rail">
            {history.slice(0, 6).map(({ h, book }) => <ResumeCard key={h.slug} book={book} entry={h} />)}
          </div>
        </section>
      ) : null}

      <section className="section">
        <div className="section-head">
          <h2><LibraryBig size={20} /> {filtering ? `ผลการค้นหา (${list.length})` : "นิยายทั้งหมด"}</h2>
        </div>

        <div className="filterbar">
          <div className="chips">
            <button className={`chip${!active.length ? " on" : ""}`} onClick={() => setActive([])}>ทั้งหมด</button>
            {genres.map((g) => (
              <button key={g} className={`chip${active.includes(g) ? " on" : ""}`} onClick={() => toggleGenre(g)}>{g}</button>
            ))}
          </div>
          <label className="sortsel">
            <ArrowDownWideNarrow size={15} />
            <select value={sort} onChange={(e) => setSort(e.target.value)} aria-label="เรียงลำดับ">
              {SORTS.map((s) => <option key={s.id} value={s.id}>{s.label}</option>)}
            </select>
          </label>
        </div>

        {list.length ? (
          <div className="book-grid">{list.map((b) => <BookCard key={b.slug} book={b} />)}</div>
        ) : (
          <EmptyState art="cat-sleeping" title="ไม่พบนิยายที่ค้นหา">
            ลองเปลี่ยนคำค้น หรือล้างตัวกรองหมวดดูนะ — เจ้าเหมียวกำลังงีบรออยู่
          </EmptyState>
        )}
      </section>
    </div>
  );
}
