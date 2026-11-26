"use client";

import { useEffect, useId, useRef, useSyncExternalStore } from "react";
import { Search, X } from "lucide-react";
import { filterChapters } from "../lib/chapter-search";
import { chapterNumber, withNumberGaps } from "../lib/chapter-number";

const stateEvent = "moonread:toc-state";
const getSearch = () => window.location.search;
const emptySearch = () => "";
const clientReady = () => true;
const serverReady = () => false;
function subscribe(listener) {
  window.addEventListener(stateEvent, listener);
  window.addEventListener("popstate", listener);
  return () => { window.removeEventListener(stateEvent, listener); window.removeEventListener("popstate", listener); };
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

export default function ChapterFinder({ chapters: entries, renderRows }) {
  const search = useSyncExternalStore(subscribe, getSearch, emptySearch);
  const ready = useSyncExternalStore(subscribe, clientReady, serverReady);
  const params = new URLSearchParams(search);
  const query = params.get("chapter") || "";
  const recent = params.get("order") === "recent";
  const range = params.get("range");
  const chapters = withNumberGaps(entries);
  const inputId = useId();
  const centered = useRef(false);
  const ranges = [...new Set(chapters.map((chapter) => Math.floor((chapterNumber(chapter) - 1) / 50) * 50 + 1))];
  const selectedRange = ranges.length > 1 ? range ?? String(recent ? ranges.at(-1) : ranges[0]) : "";
  const visible = selectedRange && !query.trim() ? chapters.filter((chapter) => chapterNumber(chapter) >= +selectedRange && chapterNumber(chapter) < +selectedRange + 50) : chapters;
  const matches = filterChapters(visible, query);
  const filtered = recent ? [...matches].reverse() : matches;

  useEffect(() => {
    const href = window.history.state?.moonreadTocFocus;
    if (!href) return;
    const focus = () => {
      for (const link of document.querySelectorAll(".toc-list a[href]")) {
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
    if (centered.current || !window.location.hash.startsWith("#chapter-") || search !== window.location.search) return;
    const target = document.getElementById(window.location.hash.slice(1));
    if (!target) return;
    centered.current = true;
    target.focus({ preventScroll: true });
    target.scrollIntoView({ block: "center", behavior: "instant" });
  }, [search]);

  return (
    <div data-chapter-finder onClickCapture={(event) => {
      const href = event.target.closest?.(".toc-list a[href]")?.getAttribute("href");
      if (href) window.history.replaceState({ ...window.history.state, moonreadTocFocus: href }, "");
    }}>
      <div className="toc-tools">
        <div className="searchbox toc-search">
          <span className="ic"><Search size={17} /></span>
          <input id={inputId} type="search" disabled={!ready} value={query} onChange={(e) => update({ chapter: e.target.value })} onKeyDown={(e) => { if (e.key === "Enter" && !e.nativeEvent.isComposing && query.trim() && filtered.length === 1 && filtered[0].status === "available") e.target.closest("[data-chapter-finder]").querySelector(".toc-list a[href]")?.click(); }} placeholder={ready ? "เลขตอนหรือชื่อตอน" : "กำลังเปิดการค้นหาตอน…"} aria-label="ค้นหาตอน" />
          {query ? <button type="button" className="ic clear" aria-label="ล้างคำค้นตอน" onClick={() => { update({ chapter: "" }); document.getElementById(inputId)?.focus(); }}><X size={16} /></button> : null}
        </div>
        <select aria-label="เรียงตอน" className="toc-select" disabled={!ready} value={recent ? "recent" : "first"} onChange={(e) => update({ order: e.target.value === "recent" ? "recent" : null })}>
          <option value="first">ตอนแรกก่อน</option>
          <option value="recent">ตอนล่าสุดก่อน</option>
        </select>
        {ranges.length > 1 ? <select aria-label="ช่วงตอน" className="toc-select" disabled={!ready} value={query.trim() ? "" : selectedRange} onChange={(e) => update({ chapter: "", range: e.target.value })}>
          <option value="">ทุกช่วงตอน</option>
          {ranges.map((first) => <option key={first} value={first}>{first}–{Math.min(first + 49, chapterNumber(chapters.at(-1)))}</option>)}
        </select> : null}
      </div>
      <p role="status" className="muted-line">{!ready ? "เปิดตอนที่แสดงได้เลย เครื่องมือค้นหากำลังโหลด…" : filtered.length ? `แสดง ${filtered.length} จาก ${chapters.length} ตอน` : "ไม่พบตอนที่ค้นหา ลองพิมพ์เลขตอนหรือคำในชื่อตอน"}</p>
      {renderRows(filtered)}
    </div>
  );
}
