"use client";

import { useEffect, useId, useRef, useSyncExternalStore } from "react";
import { Search, X } from "lucide-react";
import { filterChapters } from "../lib/chapter-search";
import { chapterNumber, withNumberGaps } from "../lib/chapter-number";

const stateEvent = "moonread:toc-state";
const getSearch = () => window.location.search;
const getHash = () => window.location.hash;
const emptyHash = () => "";
const clientReady = () => true;
const serverReady = () => false;
const chapterLinks = ".toc-list a.ch-row[href], .toc-list .chapter-link[href]";
function subscribe(listener) {
  window.addEventListener(stateEvent, listener);
  window.addEventListener("popstate", listener);
  window.addEventListener("hashchange", listener);
  return () => { window.removeEventListener(stateEvent, listener); window.removeEventListener("popstate", listener); window.removeEventListener("hashchange", listener); };
}
function update(patch) {
  const url = new URL(window.location.href);
  for (const [key, value] of Object.entries(patch)) {
    if (value === null || (value === "" && key !== "range")) url.searchParams.delete(key);
    else url.searchParams.set(key, value);
  }
  window.history.replaceState(window.history.state, "", url);
  window.dispatchEvent(new Event(stateEvent));
}

export default function ChapterFinder({ chapters: entries, initialSearch, renderRows }) {
  const search = useSyncExternalStore(subscribe, getSearch, () => initialSearch);
  const hash = useSyncExternalStore(subscribe, getHash, emptyHash);
  const ready = useSyncExternalStore(subscribe, clientReady, serverReady);
  const params = new URLSearchParams(search);
  const query = params.get("chapter") || "";
  const recent = params.get("order") === "recent";
  const range = params.get("range");
  const chapters = withNumberGaps(entries);
  const inputId = useId();
  const field = useRef(null);
  const previousQuery = useRef(new URLSearchParams(initialSearch).get("chapter") || "");
  const centered = useRef(false);
  const ranges = [...new Set(chapters.map((chapter) => Math.floor((chapterNumber(chapter) - 1) / 50) * 50 + 1))];
  const selectedRange = ranges.length > 1 ? (range === "" || ranges.includes(Number(range)) ? range : String(recent ? ranges.at(-1) : ranges[0])) : "";
  const visible = selectedRange && !query.trim() ? chapters.filter((chapter) => chapterNumber(chapter) >= +selectedRange && chapterNumber(chapter) < +selectedRange + 50) : chapters;
  const matches = filterChapters(visible, query);
  const filtered = recent ? [...matches].reverse() : matches;

  useEffect(() => {
    if (!ready) return;
    if (previousQuery.current !== query && field.current.value !== query) field.current.value = query;
    else if (previousQuery.current === query && field.current.value !== query) update({ chapter: field.current.value });
    previousQuery.current = query;
  }, [query, ready]);

  useEffect(() => {
    const href = window.history.state?.moonreadTocFocus;
    if (!href) return;
    const focus = () => {
      for (const link of document.querySelectorAll(chapterLinks)) {
        if (link.getAttribute("href") === href && window.history.state?.moonreadTocFocus === href) {
          link.focus({ preventScroll: true });
          window.history.replaceState({ ...window.history.state, moonreadTocFocus: null }, "");
          break;
        }
      }
    };
    focus();
    window.addEventListener("pageshow", focus);
    return () => window.removeEventListener("pageshow", focus);
  }, [search]);

  useEffect(() => {
    if (centered.current || !hash.startsWith("#chapter-") || search !== window.location.search) return;
    const target = document.getElementById(hash.slice(1));
    if (!target) return;
    centered.current = true;
    target.focus({ preventScroll: true });
    target.scrollIntoView({ block: "center", behavior: "instant" });
  }, [hash, search]);

  return (
    <div data-chapter-finder onClickCapture={(event) => {
      const href = event.target.closest?.(chapterLinks)?.getAttribute("href");
      if (href) window.history.replaceState({ ...window.history.state, moonreadTocFocus: href }, "");
    }}>
      <div className="toc-tools" id="chapter-results">
        <form className="searchbox toc-search" action="#chapter-results" method="get" role="search" aria-label="ค้นหาในสารบัญ" onSubmit={(event) => {
          if (!ready || field.current.value !== query) return;
          event.preventDefault();
          if (query.trim() && filtered.length === 1 && filtered[0].status === "available") event.currentTarget.closest("[data-chapter-finder]").querySelector(chapterLinks)?.click();
        }}>
          {recent ? <input type="hidden" name="order" value="recent" /> : null}
          {range !== null ? <input type="hidden" name="range" value={range} /> : null}
          <input ref={field} id={inputId} type="search" name="chapter" defaultValue={new URLSearchParams(initialSearch).get("chapter") || ""} onChange={(e) => update({ chapter: e.target.value })} placeholder="เลขตอนหรือชื่อตอน" aria-label="ค้นหาตอน" />
          <button type="submit" className="ic clear" aria-label="แสดงผลการค้นหาตอน"><Search size={17} /></button>
          {ready && query ? <button type="button" className="ic clear" aria-label="ล้างคำค้นตอน" onClick={() => { field.current.value = ""; update({ chapter: "" }); field.current.focus(); }}><X size={16} /></button> : null}
        </form>
        <select aria-label="เรียงตอน" className="toc-select" disabled={!ready} value={recent ? "recent" : "first"} onChange={(e) => update({ order: e.target.value === "recent" ? "recent" : null })}>
          <option value="first">ตอนแรกก่อน</option>
          <option value="recent">ตอนล่าสุดก่อน</option>
        </select>
        {ranges.length > 1 ? <select aria-label="ช่วงตอน" className="toc-select" disabled={!ready} value={query.trim() ? "" : selectedRange} onChange={(e) => update({ chapter: "", range: e.target.value })}>
          <option value="">ทุกช่วงตอน</option>
          {ranges.map((first) => <option key={first} value={first}>{first}–{Math.min(first + 49, chapterNumber(chapters.at(-1)))}</option>)}
        </select> : null}
      </div>
      <p role="status" className="muted-line">{filtered.length ? `แสดง ${filtered.length} จาก ${chapters.length} ตอน` : "ไม่พบตอนที่ค้นหา ลองพิมพ์เลขตอนหรือคำในชื่อตอน"}</p>
      {renderRows(filtered, hash.startsWith("#chapter-") ? hash.slice(9) : null)}
    </div>
  );
}
