"use client";

import { useEffect, useRef, useState } from "react";
import { useSearchParams } from "next/navigation";
import { LibraryBig, History, ChevronDown, ChevronRight, Search, ArrowDownWideNarrow, SlidersHorizontal, X } from "lucide-react";
import Link from "next/link";
import Image from "next/image";
import { useReaderStore } from "../lib/reader-store";
import { BookCard, ResumeCard, EmptyState } from "./BookGrid";
import { bookSynopsis } from "../lib/book-synopsis";

const SORTS = [
  { id: "curated", label: "ลำดับแนะนำ" },
  { id: "chapters", label: "ตอนเยอะสุด" },
  { id: "title", label: "ชื่อ ก-ฮ / A-Z" },
];

function closeTitle(query, title) {
  const words = (value) => value.toLowerCase().match(/[a-z0-9]+/g) || [];
  const tokens = words(query);
  const choices = words(title);
  if (!tokens.length || !/^[a-z0-9\s-]+$/i.test(query)) return false;
  let corrections = 0;
  return tokens.every((token) => choices.some((word) => word.startsWith(token)) || (
    token.length >= 4 && ++corrections === 1 && choices.some((word) => {
      if (Math.abs(word.length - token.length) > 1) return false;
      let i = 0;
      while (i < token.length && word[i] === token[i]) i++;
      const a = token.slice(i), b = word.slice(i);
      if (a.length === b.length) return a.slice(1) === b.slice(1) || (a[0] === b[1] && a[1] === b[0] && a.slice(2) === b.slice(2));
      return a.length > b.length ? a.slice(1) === b : b.slice(1) === a;
    })
  ));
}

function Hero({ query, setQuery }) {
  const field = useRef(null);
  const previousQuery = useRef(query);
  const [initialValue] = useState(query);

  useEffect(() => {
    if (previousQuery.current !== query && field.current.value !== query) field.current.value = query;
    previousQuery.current = query;
  }, [query]);

  return (
    <section className="hero">
      <Image className="hero-cat" src="/images/cat-walking.png" alt="" width={440} height={440} sizes="(max-width: 560px) 52vw, 440px" />
      <div className="hero-body">
        <span className="eyebrow">MoonRead</span>
        <h1>คลังนิยายแปลไทย</h1>
        <p>หาเรื่องที่อยากอ่าน แล้วกลับมาต่อได้จากที่ค้างไว้</p>
        <form className="hero-search" action="/#catalog" method="get" role="search" aria-label="ค้นหาในคลังนิยาย">
          <div className="searchbox">
            <span className="ic"><Search size={20} /></span>
            <input ref={field} type="search" name="q" defaultValue={initialValue} onChange={(e) => setQuery(e.target.value)} placeholder="ชื่อเรื่อง ผู้แต่ง หรือหมวด" aria-label="ค้นหานิยาย" />
            <button type="submit" className="ic clear" aria-label="ไปยังผลการค้นหา"><ChevronRight size={19} /></button>
            {query ? <button type="button" className="ic clear" onClick={() => { field.current.value = ""; setQuery(""); field.current.focus(); }} aria-label="ล้างคำค้น"><X size={16} /></button> : null}
          </div>
        </form>
      </div>
    </section>
  );
}

export default function Discover({ books, genres, initialQuery }) {
  const store = useReaderStore();
  const params = useSearchParams();
  const urlQuery = params?.get("q") ?? (params ? "" : initialQuery);
  useEffect(() => {
    if (window.location.hash !== "#catalog" || !new URLSearchParams(window.location.search).has("q")) return;
    const focusResults = () => {
      const active = document.activeElement;
      if (active === document.body || active?.id === "catalog" || active?.closest(".appbar-search")) document.getElementById("catalog-title")?.focus({ preventScroll: true });
    };
    const frame = requestAnimationFrame(focusResults);
    window.addEventListener("load", focusResults, { once: true });
    return () => { cancelAnimationFrame(frame); window.removeEventListener("load", focusResults); };
  }, [initialQuery]);
  const [draft, setDraft] = useState(null);
  const query = draft?.base === urlQuery ? draft.text : urlQuery;
  function setQuery(text) {
    setDraft({ base: urlQuery, text });
    const url = new URL(window.location.href);
    if (text) url.searchParams.set("q", text);
    else url.searchParams.delete("q");
    window.history.replaceState(null, "", url.pathname + url.search + url.hash);
  }
  const active = (params?.getAll("genre") || []).filter((g) => genres.includes(g));
  const sort = SORTS.find((option) => option.id === params?.get("sort"))?.id || "curated";
  function setFilters(nextGenres, nextSort) {
    const url = new URL(window.location.href);
    url.searchParams.delete("genre");
    nextGenres.forEach((genre) => url.searchParams.append("genre", genre));
    if (nextSort === "curated") url.searchParams.delete("sort");
    else url.searchParams.set("sort", nextSort);
    window.history.replaceState(null, "", url);
  }
  const toggleGenre = (g) => setFilters(active.includes(g) ? active.filter((x) => x !== g) : [...active, g], sort);

  const q = query.normalize("NFKC").trim().toLowerCase();
  const terms = q.split(/\s+/);
  const list = books.filter((b) => {
      const hay = `${b.title} ${b.thaiTitle || ""} ${b.author || ""} ${(b.tags || []).join(" ")} ${bookSynopsis(b)}`.normalize("NFKC").toLowerCase();
      const matchQ = !q || terms.every((term) => hay.includes(term));
      const matchG = !active.length || active.every((g) => (b.tags || []).includes(g));
      return matchQ && matchG;
  });
  if (sort === "title") list.sort((a, b) => a.title.localeCompare(b.title));
  if (sort === "chapters") list.sort((a, b) => (b.summary?.available || 0) - (a.summary?.available || 0));
  const suggestions = q && !list.length && !active.length ? books.filter((book) => closeTitle(q, book.title)).slice(0, 3) : [];

  const filtering = Boolean(q || active.length);

  const history = store.history()
    .map((h) => ({ h, book: books.find((b) => b.slug === h.slug) }))
    .filter((x) => x.book);
  const filters = (
    <details className="catalog-filters">
      <summary><SlidersHorizontal size={16} /> หมวดและการเรียง{active.length ? ` (${active.length} หมวด)` : ""}<ChevronDown size={15} /></summary>
      <div className="filterbar">
      <div className="chips">
        <button className={`chip${!active.length ? " on" : ""}`} aria-pressed={!active.length} onClick={() => setFilters([], sort)}>ทั้งหมด</button>
        {genres.map((g) => (
          <button key={g} className={`chip${active.includes(g) ? " on" : ""}`} aria-pressed={active.includes(g)} onClick={() => toggleGenre(g)}>{g}</button>
        ))}
      </div>
      <label className="sortsel">
        <ArrowDownWideNarrow size={15} />
        <select value={sort} onChange={(e) => setFilters(active, e.target.value)} aria-label="เรียงลำดับ">
          {SORTS.map((s) => <option key={s.id} value={s.id}>{s.label}</option>)}
        </select>
      </label>
      <button className="pill-btn primary filter-apply" type="button" onClick={(event) => {
        event.currentTarget.closest("details").open = false;
        const results = document.getElementById("catalog-title");
        results.focus({ preventScroll: true });
        results.scrollIntoView({ block: "start" });
      }}>แสดง {list.length} เรื่อง</button>
      </div>
    </details>
  );

  return (
    <main className="page shell" id="main-content" tabIndex={-1}>
      <Hero query={query} setQuery={setQuery} />

      {!filtering && history.length ? (
        <section className="section">
          <div className="section-head">
            <h2><History size={20} /> อ่านต่อจากที่ค้างไว้</h2>
            <Link prefetch={false} className="more" href="/history">ดูทั้งหมด <ChevronRight size={15} /></Link>
          </div>
          <div className="rail">
            {history.slice(0, 6).map(({ h, book }) => <ResumeCard key={h.slug} book={book} entry={h} />)}
          </div>
        </section>
      ) : null}

      <section className={`section${q ? " query-results" : ""}`} id="catalog" tabIndex={-1}>
        <div className="section-head">
          <h2 id="catalog-title" tabIndex={-1} aria-live="polite"><LibraryBig size={20} /> {filtering ? `ผลการค้นหา (${list.length})` : "นิยายทั้งหมด"}</h2>
          {!filtering ? <span className="catalog-count">{list.length} เรื่อง</span> : null}
        </div>

        {!q ? filters : null}

        {list.length ? (
          <div className="book-grid">{list.map((b) => <BookCard key={b.slug} book={b} />)}</div>
        ) : (
          <EmptyState art="cat-sleeping" title="ไม่พบนิยายที่ค้นหา">
            ลองเปลี่ยนคำค้น หรือ <button className="text-button" type="button" onClick={() => { setQuery(""); setFilters([], "curated"); }}>ล้างคำค้นและตัวกรอง</button>
          </EmptyState>
        )}
        {suggestions.length ? <section aria-label="เรื่องที่ชื่อใกล้เคียง"><h3>ลองดูเรื่องที่ชื่อใกล้เคียง</h3><div className="book-grid">{suggestions.map((b) => <BookCard key={b.slug} book={b} />)}</div></section> : null}
        {q ? filters : null}
      </section>
    </main>
  );
}
