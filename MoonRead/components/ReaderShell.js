"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import {
  AlignLeft, BookOpen, Bookmark, ChevronLeft, ChevronRight, List, Menu,
  Moon, Search, Settings2, Sun, Type, X, ArrowRight,
} from "lucide-react";
import { useReaderStore, defaultReader } from "../lib/reader-store";

const readingFonts = [
  { id: "sarabun", label: "Sarabun", note: "สมดุล อ่านสบาย ใช้งานได้ยาว", var: "var(--reader-font-sarabun)" },
  { id: "plex", label: "IBM Plex Sans Thai", note: "คม ชัด เป็นระเบียบ", var: "var(--reader-font-ui)" },
  { id: "serif", label: "Noto Serif Thai", note: "อารมณ์นิยาย คล้ายหนังสือเล่ม", var: "var(--reader-font-serif)" },
  { id: "maitree", label: "Maitree", note: "นุ่ม อ่านต่อเนื่องดี", var: "var(--reader-font-maitree)" },
];
const readingThemes = [
  { id: "paper", label: "กระดาษ", icon: Sun },
  { id: "sepia", label: "ซีเปีย", icon: BookOpen },
  { id: "night", label: "กลางคืน", icon: Moon },
];
function fontVarFor(id) { return (readingFonts.find((f) => f.id === id) || readingFonts[0]).var; }
function chapterLabel(c) { return `ตอน ${String(c.number).padStart(3, "0")}`; }

function blockClass(block) {
  if (block.type === "title") return "reader-title";
  if (block.type === "heading") return "reader-heading";
  if (/^[“"']/.test(block.text)) return "reader-paragraph dialogue";
  if (/^\(.+\)$/.test(block.text)) return "reader-paragraph aside";
  return "reader-paragraph";
}
function renderInline(text) {
  const parts = [];
  const pattern = /(\*\*([^*]+)\*\*|\*([^*]+)\*)/g;
  let last = 0, m;
  while ((m = pattern.exec(text)) !== null) {
    if (m.index > last) parts.push(text.slice(last, m.index));
    if (m[2]) parts.push(<strong key={`s${m.index}`}>{m[2]}</strong>);
    else if (m[3]) parts.push(<em key={`e${m.index}`}>{m[3]}</em>);
    last = pattern.lastIndex;
  }
  if (last < text.length) parts.push(text.slice(last));
  return parts;
}

export default function ReaderShell({ chapter, neighbors, chapters, blocks, book }) {
  const store = useReaderStore();
  const router = useRouter();
  const slug = book?.slug || "deep-sea-embers";

  const [settings, setSettings] = useState(() => ({ ...defaultReader, ...store.getReader() }));
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [tocOpen, setTocOpen] = useState(false);
  const [tocQuery, setTocQuery] = useState("");
  const [hiddenChrome, setHiddenChrome] = useState(false);
  const [progress, setProgress] = useState(0);
  const [, setBookmarkVersion] = useState(0);
  const [countdown, setCountdown] = useState(null);
  const countRef = useRef(null);
  const canceled = useRef(false);
  const lastSave = useRef(0);

  useEffect(() => {
    queueMicrotask(() => setCountdown(null));
    canceled.current = false;
    clearInterval(countRef.current);
    window.scrollTo(0, 0);
  }, [slug, chapter.id]);

  function update(patch) {
    setSettings((s) => ({ ...s, ...patch }));
    store.setReader(patch);
  }

  function startCountdown() {
    if (!neighbors.next) return;
    let n = 5; setCountdown(n);
    countRef.current = setInterval(() => {
      n -= 1; setCountdown(n);
      if (n <= 0) { clearInterval(countRef.current); router.push(neighbors.next.href); }
    }, 1000);
  }
  function cancelCountdown() { clearInterval(countRef.current); setCountdown(null); canceled.current = true; }

  useEffect(() => {
    let lastY = window.scrollY;
    const onScroll = () => {
      const max = document.documentElement.scrollHeight - window.innerHeight;
      const pct = max > 0 ? Math.min(100, Math.max(0, (window.scrollY / max) * 100)) : 0;
      setProgress(pct);
      setHiddenChrome(window.scrollY > 180 && window.scrollY > lastY);
      lastY = window.scrollY;
      const now = Date.now();
      if (now - lastSave.current > 900) {
        lastSave.current = now;
        store.setProgress(slug, { chapterId: chapter.id, number: chapter.number, title: chapter.title, href: chapter.href, percent: Math.round(pct) });
      }
      if (settings.autoAdvance && neighbors.next && pct >= 99 && countdown === null && !canceled.current) startCountdown();
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
    return () => window.removeEventListener("scroll", onScroll);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [slug, chapter.id, settings.autoAdvance, countdown]);

  useEffect(() => () => clearInterval(countRef.current), []);

  function toggleBookmark() { store.toggleBookmark(slug, chapter); setBookmarkVersion((v) => v + 1); }

  const readerStyle = {
    "--reader-font-family": fontVarFor(settings.fontFamily),
    "--reader-font-size": `${settings.fontSize}px`,
    "--reader-line-height": settings.lineHeight,
    "--reader-width": `${settings.width}px`,
    "--reader-paragraph-spacing": `${settings.paragraphSpacing}em`,
  };
  const sheetNight = settings.theme === "night" ? " night" : "";
  const bookmarked = store.isBookmarked(slug, chapter.id);
  const tocFiltered = tocQuery
    ? chapters.filter((c) => (c.title || "").toLowerCase().includes(tocQuery.toLowerCase()) || String(c.number).includes(tocQuery))
    : chapters;

  return (
    <main className={`reader-page theme-${settings.theme}`} style={readerStyle}>
      <div className={`reader-topbar${hiddenChrome ? " hidden" : ""}`}>
        <Link href={book?.chaptersHref || "/chapters"} className="icon-button" aria-label="กลับไปสารบัญ"><ChevronLeft size={20} /></Link>
        <div className="reader-top-title">
          <strong>{chapter.title}</strong>
          <span>{`${book?.title || "MoonRead"} · ${Math.round(progress)}%`}</span>
        </div>
        <div className="reader-top-actions">
          <button className="icon-button" type="button" onClick={toggleBookmark} aria-label="คั่นหน้า"><Bookmark size={19} fill={bookmarked ? "currentColor" : "none"} color={bookmarked ? "var(--gold)" : undefined} /></button>
          <button className="icon-button" type="button" onClick={() => setTocOpen(true)} aria-label="เปิดสารบัญ"><List size={20} /></button>
          <button className="icon-button" type="button" onClick={() => setSettingsOpen(true)} aria-label="ตั้งค่าการอ่าน"><Settings2 size={20} /></button>
        </div>
        <span className="progress-line" style={{ transform: `scaleX(${progress / 100})` }} />
      </div>

      <section className="reader-head">
        <span className="reader-kicker">{chapterLabel(chapter)}</span>
        <h1>{chapter.title}</h1>
        <div className="reader-meta">
          <span><BookOpen size={14} /> {book?.title || "MoonRead"}</span>
          <span><Type size={14} /> ~{chapter.readingMinutes} นาที</span>
        </div>
      </section>

      <article className="reader-article">
        {blocks.map((block, i) => {
          if (block.type === "title") return <h2 className={blockClass(block)} key={i}>{block.text}</h2>;
          if (block.type === "heading") return <h3 className={blockClass(block)} key={i}>{block.text}</h3>;
          return <p className={blockClass(block)} key={i}>{renderInline(block.text)}</p>;
        })}
      </article>

      <div className="reader-end">
        {neighbors.next ? (
          <div className="next-card">
            <div className="ring" style={{ "--deg": `${(countdown !== null ? (5 - countdown) / 5 : 0) * 360}deg` }}>
              <i>{countdown !== null ? countdown : "▸"}</i>
            </div>
            <div className="nx">
              <small>{countdown !== null ? "กำลังไปต่อ…" : "ตอนถัดไป"}</small>
              <strong>{chapterLabel(neighbors.next)} · {neighbors.next.title}</strong>
            </div>
            {countdown !== null
              ? <button className="pill-btn ghost" type="button" onClick={cancelCountdown}>ยกเลิก</button>
              : <Link className="pill-btn primary" href={neighbors.next.href}>อ่านต่อ <ArrowRight size={17} /></Link>}
          </div>
        ) : (
          <div className="next-card"><div className="nx"><small>จบเท่าที่มีในตอนนี้</small><strong>ขอบคุณที่อ่านกับ MoonRead 🌙</strong></div></div>
        )}
      </div>

      <nav className="reader-bottom-nav" aria-label="Chapter navigation">
        {neighbors.previous ? (
          <Link href={neighbors.previous.href}><ChevronLeft size={20} /><span><small>{chapterLabel(neighbors.previous)}</small><strong>{neighbors.previous.title}</strong></span></Link>
        ) : <span className="nav-placeholder" />}
        {neighbors.next ? (
          <Link className="next" href={neighbors.next.href}><span><small>{chapterLabel(neighbors.next)}</small><strong>{neighbors.next.title}</strong></span><ChevronRight size={20} /></Link>
        ) : <span className="nav-placeholder" />}
      </nav>

      <div className="reader-fabs">
        <button className="fab" type="button" onClick={() => setTocOpen(true)} aria-label="สารบัญ"><List size={22} /></button>
        <button className="fab acc" type="button" onClick={() => setSettingsOpen(true)} aria-label="ตั้งค่าการอ่าน"><Type size={22} /></button>
      </div>

      {tocOpen ? (
        <div className="scrim" onClick={() => setTocOpen(false)}>
          <aside className={`sheet${sheetNight}`} onClick={(e) => e.stopPropagation()} aria-label="สารบัญตอน">
            <div className="sheet-head">
              <div><strong>สารบัญ</strong><span>{book?.title || "MoonRead"}</span></div>
              <button className="icon-button" type="button" onClick={() => setTocOpen(false)} aria-label="ปิดสารบัญ"><X size={20} /></button>
            </div>
            <div className="searchbox"><span className="ic"><Search size={17} /></span>
              <input value={tocQuery} onChange={(e) => setTocQuery(e.target.value)} placeholder="กระโดดไปตอน…" aria-label="ค้นหาตอน" /></div>
            <div className="toc-list sheet-toc">
              {tocFiltered.map((item) => (
                <Link key={item.id} className={`ch-row${item.id === chapter.id ? " reading" : ""}`} href={item.href} onClick={() => setTocOpen(false)}>
                  <span className="num">{String(item.number).padStart(3, "0")}</span>
                  <span className="ct"><small>{chapterLabel(item)}</small><strong>{item.title}</strong></span>
                  <span className="cm">{store.isBookmarked(slug, item.id) ? <Bookmark size={14} fill="currentColor" color="var(--gold)" /> : null}</span>
                </Link>
              ))}
            </div>
          </aside>
        </div>
      ) : null}

      {settingsOpen ? (
        <div className="scrim" onClick={() => setSettingsOpen(false)}>
          <aside className={`sheet${sheetNight}`} onClick={(e) => e.stopPropagation()} aria-label="ตั้งค่าการอ่าน">
            <div className="sheet-head">
              <div><strong>ตั้งค่าการอ่าน</strong><span>ปรับให้สบายตาสำหรับการอ่านยาว</span></div>
              <button className="icon-button" type="button" onClick={() => setSettingsOpen(false)} aria-label="ปิดการตั้งค่า"><X size={20} /></button>
            </div>

            <div className="seg theme-seg">
              {readingThemes.map((t) => { const Ic = t.icon; return (
                <button key={t.id} type="button" className={settings.theme === t.id ? "on" : ""} onClick={() => update({ theme: t.id })}><Ic size={17} /> {t.label}</button>
              ); })}
            </div>

            <div className="field">
              <label><span><Type size={16} /> ขนาดตัวอักษร</span><span className="v">{settings.fontSize}px</span></label>
              <input type="range" min="18" max="28" value={settings.fontSize} onChange={(e) => update({ fontSize: Number(e.target.value) })} />
            </div>
            <div className="field">
              <label><span><AlignLeft size={16} /> ระยะบรรทัด</span><span className="v">{Number(settings.lineHeight).toFixed(2)}</span></label>
              <input type="range" min="1.6" max="2.4" step="0.05" value={settings.lineHeight} onChange={(e) => update({ lineHeight: Number(e.target.value) })} />
            </div>
            <div className="field">
              <label><span><Menu size={16} /> ความกว้างหน้าอ่าน</span><span className="v">{settings.width}px</span></label>
              <input type="range" min="600" max="900" step="20" value={settings.width} onChange={(e) => update({ width: Number(e.target.value) })} />
            </div>
            <div className="field">
              <label><span><AlignLeft size={16} /> ระยะย่อหน้า</span><span className="v">{Number(settings.paragraphSpacing).toFixed(1)}em</span></label>
              <input type="range" min="0.8" max="1.8" step="0.1" value={settings.paragraphSpacing} onChange={(e) => update({ paragraphSpacing: Number(e.target.value) })} />
            </div>

            <div className="font-picker-label"><Type size={16} /> ฟอนต์สำหรับอ่าน</div>
            <div className="font-options">
              {readingFonts.map((f) => (
                <button key={f.id} type="button" className={`font-option${settings.fontFamily === f.id ? " selected" : ""}`} style={{ fontFamily: f.var }} onClick={() => update({ fontFamily: f.id })}>
                  <span className="font-option-label">{f.label}</span>
                  <span className="font-option-note">{f.note}</span>
                </button>
              ))}
            </div>

            <div className="toggle-row">
              <div><div className="tt">เลื่อนตอนถัดไปอัตโนมัติ</div><div className="td">เมื่ออ่านจบตอน จะนับถอยหลังไปต่อให้เอง</div></div>
              <button type="button" className={`switch${settings.autoAdvance ? " on" : ""}`} aria-pressed={settings.autoAdvance} aria-label="เลื่อนตอนถัดไปอัตโนมัติ" onClick={() => update({ autoAdvance: !settings.autoAdvance })}><i /></button>
            </div>
          </aside>
        </div>
      ) : null}
    </main>
  );
}
