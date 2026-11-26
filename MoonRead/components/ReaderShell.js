"use client";

import Link from "next/link";
import { useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState, useSyncExternalStore } from "react";
import {
  AlignLeft, BookOpen, Bookmark, ChevronLeft, ChevronRight, List, Menu,
  Moon, Search, Sun, Type, X, ArrowRight,
} from "lucide-react";
import { ReaderStore, useReaderStore } from "../lib/reader-store";
import { filterChapters } from "../lib/chapter-search";
import { chapterNumber, episodeLabel as chapterLabel, withNumberGaps } from "../lib/chapter-number";

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

const FOCUSABLE = "a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex=\"-1\"])";

// Dialog behaviour shared by both reader sheets: focus the first control on
// open, keep Tab/Shift+Tab inside, close on Escape, restore the opener.
function useSheetFocus(open, onClose, openerRef) {
  const sheetRef = useRef(null);
  const closeRef = useRef(onClose);
  useEffect(() => {
    closeRef.current = onClose;
  }, [onClose]);

  useEffect(() => {
    if (!open) return undefined;
    const opener = openerRef.current;
    const sheet = sheetRef.current;
    const focusables = () => (sheet ? [...sheet.querySelectorAll(FOCUSABLE)].filter((el) => el.offsetParent !== null) : []);
    const first = focusables()[0];
    if (first) first.focus();

    const onKeyDown = (event) => {
      if (event.key === "Escape") {
        event.preventDefault();
        event.stopPropagation();
        closeRef.current();
        return;
      }
      if (event.key !== "Tab") return;
      const items = focusables();
      if (!items.length) return;
      const firstItem = items[0];
      const lastItem = items[items.length - 1];
      const active = document.activeElement;
      if (!sheet.contains(active)) {
        event.preventDefault();
        (event.shiftKey ? lastItem : firstItem).focus();
        return;
      }
      if (event.shiftKey && active === firstItem) {
        event.preventDefault();
        lastItem.focus();
      } else if (!event.shiftKey && active === lastItem) {
        event.preventDefault();
        firstItem.focus();
      }
    };

    document.addEventListener("keydown", onKeyDown, true);
    return () => {
      document.removeEventListener("keydown", onKeyDown, true);
      if (opener && typeof opener.focus === "function" && document.contains(opener)) opener.focus({ preventScroll: true });
    };
  }, [open, openerRef]);

  return sheetRef;
}

function blockClass(block) {
  if (block.type === "title") return "reader-title";
  if (block.type === "heading") return "reader-heading";
  if (/^[“"']/.test(block.text)) return "reader-paragraph dialogue";
  if (/^\(.+\)$/.test(block.text)) return "reader-paragraph aside";
  return "reader-paragraph";
}
function renderInline(text) {
  const parts = [];
  const pattern = /\*{4}([^*]+)\*{4}|\*{3}([^*]+)\*{3}|\*\*([^*]+)\*\*|\*([^*]+)\*/g;
  let last = 0, m;
  while ((m = pattern.exec(text)) !== null) {
    if (m.index > last) parts.push(text.slice(last, m.index));
    if (m[1]) parts.push(<strong key={`s${m.index}`}>{m[1]}</strong>);
    else if (m[2]) parts.push(<strong key={`se${m.index}`}><em>{m[2]}</em></strong>);
    else if (m[3]) parts.push(<strong key={`s${m.index}`}>{m[3]}</strong>);
    else if (m[4]) parts.push(<em key={`e${m.index}`}>{m[4]}</em>);
    last = pattern.lastIndex;
  }
  if (last < text.length) parts.push(text.slice(last));
  return parts;
}

function scrollToReadingPosition(top) {
  window.scrollTo({ top, behavior: "instant" });
}

function readingPosition(article, inset) {
  // The content order is stable across viewports and font settings. Find the
  // visible block without laying out the entire chapter on each scroll event.
  const blocks = article.children;
  let lo = 0, hi = blocks.length;
  while (lo < hi) {
    const mid = (lo + hi) >>> 1;
    if (blocks[mid].getBoundingClientRect().bottom <= inset) lo = mid + 1;
    else hi = mid;
  }
  const rect = blocks[lo]?.getBoundingClientRect();
  if (!rect || (lo === 0 && rect.top > inset)) return null;
  return { block: lo, fraction: Math.max(0, inset - rect.top) / Math.max(1, rect.height) };
}

function restorePosition(article, bar, position) {
  const rect = Number.isInteger(position?.block) ? article?.children[position.block]?.getBoundingClientRect() : null;
  if (!rect || !Number.isFinite(position.fraction)) return false;
  scrollToReadingPosition(window.scrollY + rect.top + rect.height * Math.min(1, Math.max(0, position.fraction)) - (bar?.offsetHeight || 0) - 8);
  return true;
}

export default function ReaderShell({ chapter, neighbors, chapters, blocks, book }) {
  const [current, setCurrent] = useState({ chapter, neighbors, blocks });
  const cached = useRef(new Map([[chapter.href, { chapter, neighbors, blocks }]]));
  const activeHref = useRef(chapter.href);

  useEffect(() => {
    const restore = () => {
      const href = window.location.pathname;
      const content = cached.current.get(href);
      if (content && activeHref.current !== href) {
        activeHref.current = href;
        setCurrent(content);
      } else if (!content && chapters.some((item) => item.href === href) && activeHref.current !== href) {
        window.location.reload();
      }
    };
    window.addEventListener("popstate", restore);
    return () => window.removeEventListener("popstate", restore);
  }, [chapters]);

  const changeChapter = useCallback((content, review) => {
    const href = content.chapter.href;
    cached.current.delete(href);
    cached.current.set(href, content);
    if (cached.current.size > 24) cached.current.delete(cached.current.keys().next().value);
    activeHref.current = href;
    window.history.pushState({ moonreadChapter: true }, "", review ? `${href}?review=1` : href);
    scrollToReadingPosition(0);
    setCurrent(content);
  }, []);

  return <ChapterView key={current.chapter.id} {...current} chapters={chapters} book={book} changeChapter={changeChapter} />;
}

const subscribeReady = () => () => {};
const clientReady = () => true;
const serverReady = () => false;

function ChapterView({ chapter, neighbors, chapters, blocks, book, changeChapter }) {
  const store = useReaderStore();
  const controlsReady = useSyncExternalStore(subscribeReady, clientReady, serverReady);
  const slug = book?.slug || "deep-sea-embers";

  const settings = store.getReader();
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [tocOpen, setTocOpen] = useState(false);
  const [tocQuery, setTocQuery] = useState("");
  const [progress, setProgress] = useState(0);
  const [countdown, setCountdown] = useState(null);
  const [atEnd, setAtEnd] = useState(false);
  const [countdownAllowed, setCountdownAllowed] = useState(true);
  const [failure, setFailure] = useState(null);
  const [loadingHref, setLoadingHref] = useState(null);
  const [review, setReview] = useState(false);
  const dialogOpener = useRef(null);
  const tocRef = useSheetFocus(tocOpen, () => setTocOpen(false), dialogOpener);
  const settingsRef = useSheetFocus(settingsOpen, () => setSettingsOpen(false), dialogOpener);
  const topbar = useRef(null);
  const article = useRef(null);
  const heading = useRef(null);
  const endAction = useRef(null);
  const activeChapter = useRef(null);
  const pendingNavigation = useRef(null);
  const flushPosition = useRef(null);
  const leaving = useRef(false);
  const reviewing = useRef(false);
  const layoutAnchor = useRef(null);
  const settingsAnchor = useRef(null);

  useEffect(() => {
    if (!tocOpen || !activeChapter.current) return;
    const row = activeChapter.current;
    const list = row.closest(".sheet-toc");
    if (list) list.scrollTop = row.offsetTop - list.clientHeight / 2 + row.offsetHeight / 2;
  }, [tocOpen]);

  const navigate = useCallback(async (href, { reviewTarget = reviewing.current } = {}) => {
    if (href === chapter.href) return;
    pendingNavigation.current?.abort();
    const controller = new AbortController();
    pendingNavigation.current = controller;
    setFailure(null);
    setLoadingHref(href);
    try {
      if (!navigator.onLine) throw new Error("offline");
      const target = chapters.find((item) => item.href === href);
      const signal = AbortSignal.any([controller.signal, AbortSignal.timeout(7000)]);
      const response = await fetch(target ? `/reader-data/${encodeURIComponent(slug)}/${encodeURIComponent(target.id)}` : href, { method: target ? "GET" : "HEAD", signal });
      if (!response.ok) throw new Error("unavailable");
      if (target) {
        const content = await response.json();
        if (content.chapter?.href !== href || !Array.isArray(content.blocks) || !content.neighbors) throw new Error("incomplete chapter");
        if (!controller.signal.aborted) { flushPosition.current?.(); changeChapter(content, reviewTarget); }
      } else if (!controller.signal.aborted) {
        flushPosition.current?.();
        // Use a document boundary when leaving the reader so browser Back
        // restores the chapter on screen, not an earlier Next router snapshot.
        leaving.current = true;
        window.location.assign(href);
      }
    } catch {
      if (!controller.signal.aborted) setFailure({ href, reviewTarget, title: chapters.find((item) => item.href === href)?.title });
    } finally {
      if (!controller.signal.aborted) setLoadingHref(null);
    }
  }, [chapter.href, chapters, changeChapter, slug]);

  useEffect(() => () => pendingNavigation.current?.abort(), []);

  useEffect(() => {
    function readingKeys(event) {
      if (event.defaultPrevented || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey || tocOpen || settingsOpen) return;
      const active = document.activeElement;
      if (active?.closest('input, select, textarea, [contenteditable], [role="slider"], [role="dialog"]')) return;
      const inset = topbar.current?.getBoundingClientRect().bottom || 0;
      if (event.key === "PageDown" || event.key === "PageUp") {
        const line = parseFloat(getComputedStyle(article.current).lineHeight) || 40;
        const step = Math.max(line, window.innerHeight - inset - 2 * line);
        event.preventDefault();
        scrollToReadingPosition(window.scrollY + (event.key === "PageDown" ? step : -step));
      } else if (event.key === "Tab" && (active === document.body || active === article.current || active === heading.current)) {
        const action = endAction.current;
        const bounds = action?.getBoundingClientRect();
        if (!bounds || bounds.top < inset || bounds.bottom > window.innerHeight) return;
        event.preventDefault();
        action.focus({ preventScroll: true });
      }
    }
    document.addEventListener("keydown", readingKeys);
    return () => document.removeEventListener("keydown", readingKeys);
  }, [settingsOpen, tocOpen]);

  function follow(event, href, reviewTarget = reviewing.current) {
    event.preventDefault();
    cancelCountdown();
    void navigate(href, { reviewTarget });
  }

  function update(patch) {
    if (["fontFamily", "fontSize", "lineHeight", "width", "paragraphSpacing"].some((key) => key in patch && patch[key] !== settings[key])) {
      layoutAnchor.current = settingsAnchor.current || (article.current && window.scrollY > 0 ? readingPosition(article.current, (topbar.current?.offsetHeight || 0) + 8) : null);
    }
    store.setReader(patch);
  }

  useLayoutEffect(() => {
    const anchor = layoutAnchor.current;
    if (!anchor) return;
    layoutAnchor.current = null;
    restorePosition(article.current, topbar.current, anchor);
    let active = true;
    const alignedY = window.scrollY;
    void document.fonts.ready.then(() => {
      if (active && Math.abs(window.scrollY - alignedY) < 12) restorePosition(article.current, topbar.current, anchor);
    });
    return () => { active = false; };
  }, [settings.fontFamily, settings.fontSize, settings.lineHeight, settings.width, settings.paragraphSpacing]);

  useLayoutEffect(() => {
    if (settingsOpen || !settingsAnchor.current) return;
    const anchor = settingsAnchor.current;
    settingsAnchor.current = null;
    restorePosition(article.current, topbar.current, anchor);
    // A browser can adjust the viewport after the modal releases scroll lock.
    // Align again after that layout, without waiting for an arbitrary timer.
    const frame = requestAnimationFrame(() => {
      restorePosition(article.current, topbar.current, anchor);
      flushPosition.current?.();
    });
    return () => cancelAnimationFrame(frame);
  }, [settingsOpen]);

  useLayoutEffect(() => {
    if (!review) return;
    const position = ReaderStore.getBookmark(slug, chapter.id)?.position;
    if (!restorePosition(article.current, topbar.current, position)) scrollToReadingPosition(0);
  }, [chapter.id, review, slug]);

  useEffect(() => {
    const saved = ReaderStore.getChapterPosition(slug, chapter.id);
    const params = new URLSearchParams(window.location.search);
    const restart = params.has("start");
    reviewing.current = params.has("review");
    if (restart) window.history.replaceState(window.history.state, "", chapter.href);
    document.title = book?.title && slug !== "deep-sea-embers" ? `${chapter.title} | ${book.title} | MoonRead` : `${chapter.title} | MoonRead`;
    let ready = false, disposed = false, saveTimer, frame, pending, lastAnchor;
    const inset = () => (topbar.current?.offsetHeight || 0) + 8;
    const flush = () => {
      clearTimeout(saveTimer);
      if (!pending) return;
      if (!reviewing.current) ReaderStore.setProgress(slug, pending);
      pending = undefined;
    };
    const measure = () => {
      if (!ready || leaving.current) return;
      const max = document.documentElement.scrollHeight - window.innerHeight;
      const pct = max > 0 ? Math.min(100, Math.max(0, (window.scrollY / max) * 100)) : 0;
      setProgress(pct);
      const end = max > 0 && max - window.scrollY <= 8;
      setAtEnd(end);
      if (!end) setCountdown(null);
      const position = window.scrollY > 0 && article.current ? readingPosition(article.current, inset()) : null;
      lastAnchor = position;
      pending = { chapterId: chapter.id, number: chapter.number, title: chapter.title, href: chapter.href, percent: Math.round(pct), position };
      clearTimeout(saveTimer);
      saveTimer = setTimeout(flush, 250);
    };
    const onScroll = () => {
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(measure);
    };
    const onPageExit = () => { measure(); flush(); };
    flushPosition.current = onPageExit;
    const onVisibility = () => { if (document.hidden) onPageExit(); };
    const onPageReturn = (event) => { if (event.persisted) leaving.current = false; };
    const onResize = () => {
      if (ready && !leaving.current) { restorePosition(article.current, topbar.current, lastAnchor); onScroll(); }
    };
    // Wait for persisted reader styles and loaded web fonts before measuring.
    frame = requestAnimationFrame(async () => {
      await document.fonts.ready;
      if (disposed) return;
      const position = saved?.position;
      setReview(reviewing.current);
      if (!reviewing.current && !restart && saved?.chapterId === chapter.id && (position || saved.percent > 0)) {
        const max = document.documentElement.scrollHeight - window.innerHeight;
        if (!restorePosition(article.current, topbar.current, position)) scrollToReadingPosition(max * saved.percent / 100);
      } else if (restart || reviewing.current || window.history.state?.moonreadChapter) {
        scrollToReadingPosition(0);
      }
      ready = true;
      measure();
      if (window.history.state?.moonreadChapter) heading.current?.focus({ preventScroll: true });
      window.addEventListener("scroll", onScroll, { passive: true });
      window.addEventListener("resize", onResize);
      window.addEventListener("pagehide", onPageExit);
      window.addEventListener("pageshow", onPageReturn);
      document.addEventListener("visibilitychange", onVisibility);
    });
    return () => {
      disposed = true;
      flushPosition.current = null;
      cancelAnimationFrame(frame);
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onResize);
      window.removeEventListener("pagehide", onPageExit);
      window.removeEventListener("pageshow", onPageReturn);
      document.removeEventListener("visibilitychange", onVisibility);
      flush();
    };
  }, [slug, chapter.id, chapter.number, chapter.title, chapter.href, book?.title]);

  const nextHref = neighbors.next?.href;
  useEffect(() => {
    if (review || !settings.autoAdvance || !nextHref || !atEnd || !countdownAllowed || settingsOpen || tocOpen || document.hidden) return;
    let n = 5;
    const start = setTimeout(() => setCountdown(n), 0);
    const stop = () => {
      clearTimeout(start);
      clearInterval(timer);
      setCountdown(null);
      setCountdownAllowed(false);
    };
    const timer = setInterval(() => {
      if (document.hidden || !navigator.onLine || document.documentElement.scrollHeight - window.innerHeight - window.scrollY > 8) { stop(); return; }
      n -= 1;
      if (n > 0) setCountdown(n);
      else { stop(); void navigate(nextHref); }
    }, 1000);
    const suppressHiddenTab = () => { if (document.hidden) stop(); };
    document.addEventListener("visibilitychange", suppressHiddenTab);
    return () => {
      clearTimeout(start);
      clearInterval(timer);
      document.removeEventListener("visibilitychange", suppressHiddenTab);
    };
  }, [atEnd, countdownAllowed, nextHref, navigate, review, settings.autoAdvance, settingsOpen, tocOpen]);

  function cancelCountdown() { setCountdown(null); setCountdownAllowed(false); }
  function openToc(event) { dialogOpener.current = event.currentTarget; if (atEnd) cancelCountdown(); setTocQuery(""); setTocOpen(true); }
  function openSettings(event) {
    dialogOpener.current = event.currentTarget;
    settingsAnchor.current = article.current && window.scrollY > 0 && !atEnd ? readingPosition(article.current, (topbar.current?.offsetHeight || 0) + 8) : null;
    if (atEnd) cancelCountdown();
    setSettingsOpen(true);
  }
  const shownCountdown = atEnd && countdownAllowed ? countdown : null;

  const readerStyle = {
    "--reader-font-family": fontVarFor(settings.fontFamily),
    "--reader-font-size": `${settings.fontSize}px`,
    "--reader-line-height": settings.lineHeight,
    "--reader-width": `${settings.width}px`,
    "--reader-paragraph-spacing": `${settings.paragraphSpacing}em`,
  };
  const sheetNight = settings.theme === "night" ? " night" : "";
  const bookmarked = store.isBookmarked(slug, chapter.id);
  const resume = store.getProgress(slug);
  const resumeHref = review && chapters.some((item) => item.href === resume?.href) ? resume.href : null;
  const tocFiltered = useMemo(() => filterChapters(withNumberGaps(chapters), tocQuery), [chapters, tocQuery]);
  const nextNumber = neighbors.next && chapterNumber(neighbors.next);
  const missingStart = chapterNumber(chapter) + 1;
  const gap = nextNumber > missingStart && nextNumber - missingStart < 50;
  const missingLabel = nextNumber === missingStart + 1 ? String(missingStart) : `${missingStart}–${nextNumber - 1}`;
  const homeToc = book?.chaptersHref || "/chapters";
  const rangeStart = Math.floor((chapterNumber(chapter) - 1) / 50) * 50 + 1;
  const tocHref = `${homeToc}?range=${rangeStart}#chapter-${chapter.id}`;
  const navigationMessage = loadingHref ? <div className="reader-nav-status" role="status">กำลังเปิดหน้า…</div> : failure ? (
    <div className="reader-nav-status">
      <span role="alert">เปิดหน้าไม่ได้{failure.title ? ` · ${failure.title}` : ""} คุณยังอ่านตอนนี้ต่อได้</span>
      <button type="button" onClick={() => void navigate(failure.href, failure)}>ลองอีกครั้ง</button>
    </div>
  ) : null;

  return (
    <main className={`reader-page theme-${settings.theme}`} data-reader-preparing={!store.ready || undefined} style={readerStyle}>
      <div inert={tocOpen || settingsOpen}>
      <div ref={topbar} className="reader-topbar">
        <Link prefetch={false} href={tocHref} onNavigate={(e) => follow(e, tocHref)} className="icon-button" aria-label="กลับไปสารบัญ"><ChevronLeft size={20} /></Link>
        <div className="reader-top-title">
          <strong>{chapter.title}</strong>
          <div className="reader-top-meta">
            <span className="reader-series-name">{book?.title || "MoonRead"}</span>
            <span className="reader-progress-value" aria-label={`อ่านแล้ว ${Math.round(progress)} เปอร์เซ็นต์`}>{Math.round(progress)}%</span>
          </div>
        </div>
        <div className="reader-top-actions">
          {controlsReady ? <>
            <button className="icon-button" type="button" onClick={() => store.toggleBookmark(slug, chapter, window.scrollY > 0 ? readingPosition(article.current, (topbar.current?.offsetHeight || 0) + 8) : null)} aria-label="คั่นหน้า" aria-pressed={bookmarked}><Bookmark size={19} fill={bookmarked ? "currentColor" : "none"} color={bookmarked ? "var(--gold)" : undefined} /></button>
            <button className="icon-button" type="button" onClick={openToc} aria-label="เปิดสารบัญ"><List size={20} /></button>
            <button className="icon-button settings-trigger" type="button" onClick={openSettings} aria-label="ตั้งค่าการอ่าน"><span aria-hidden="true">Aa</span></button>
          </> : <span className="reader-controls-loading" role="status">กำลังโหลดเครื่องมืออ่าน…</span>}
        </div>
        <span className="progress-line" style={{ transform: `scaleX(${progress / 100})` }} />
        {resumeHref ? <a className="review-toolbar-link" href={resumeHref}>กลับไปอ่านต่อ {chapterLabel(resume)} <ArrowRight size={16} /></a> : null}
        <nav className="reader-stepper" aria-label="เปลี่ยนตอนระหว่างอ่าน">
          {neighbors.previous ? <Link prefetch={false} href={neighbors.previous.href} onNavigate={(e) => follow(e, neighbors.previous.href)}><ChevronLeft size={16} /> ตอนก่อนหน้า</Link> : <span />}
          {neighbors.next ? <Link prefetch={false} className="reader-quick-next" href={neighbors.next.href} onNavigate={(e) => follow(e, neighbors.next.href)}>ตอนถัดไป <ChevronRight size={16} /></Link> : <span />}
        </nav>
        {!tocOpen && navigationMessage ? <div className="reader-retry">{navigationMessage}</div> : null}
      </div>

      <section className="reader-head">
        <span className="reader-kicker">{chapterLabel(chapter)}</span>
        <h1 ref={heading} tabIndex={-1} onKeyDown={(event) => {
          if (event.key !== "Tab" || event.shiftKey || event.altKey || event.ctrlKey || event.metaKey) return;
          const action = endAction.current?.getBoundingClientRect();
          if (action && action.top >= topbar.current?.getBoundingClientRect().bottom && action.bottom <= window.innerHeight) return;
          const firstTool = topbar.current?.querySelector("a[href]");
          if (!firstTool) return;
          // A new chapter announces its heading first. Keep the next keyboard
          // stop at the top instead of scrolling past the entire passage.
          event.preventDefault();
          firstTool.focus({ preventScroll: true });
        }}>{chapter.title}</h1>
        {review ? <p className="reader-review">โหมดอ่านทวน · ไม่เปลี่ยนตำแหน่งอ่านค้างไว้</p> : null}
        <div className="reader-meta">
          <span><BookOpen size={14} /> {book?.title || "MoonRead"}</span>
          <span><Type size={14} /> ~{chapter.readingMinutes} นาที</span>
          <span>ผู้แปล <span className="translator">{chapter.translator}</span></span>
        </div>
      </section>

      <article ref={article} className="reader-article" id="main-content" tabIndex={-1}>
        {blocks.map((block, i) => {
          if (block.type === "title") return block.text === chapter.title ? null : <h2 className={blockClass(block)} key={i}>{block.text}</h2>;
          if (block.type === "separator") return <hr key={i} />;
          if (block.type === "heading") return <h3 className={blockClass(block)} key={i}>{block.text}</h3>;
          return <p className={blockClass(block)} key={i}>{renderInline(block.text)}</p>;
        })}
      </article>

      <div className="reader-end">
        {resumeHref ? (
          <div className="next-card">
            <div className="nx"><small>ตำแหน่งอ่านค้างไว้</small><strong>{chapterLabel(resume)} · {resume.title}</strong></div>
            <a ref={endAction} className="pill-btn primary" href={resumeHref}>กลับไปอ่านต่อ <ArrowRight size={17} /></a>
          </div>
        ) : neighbors.next ? (
          <div className="next-card">
            <div className="ring" aria-hidden="true" style={{ "--deg": `${(shownCountdown !== null ? (5 - shownCountdown) / 5 : 0) * 360}deg` }}>
              <i>{shownCountdown ?? "▸"}</i>
            </div>
            <div className="nx">
              <small role="status">{shownCountdown !== null ? "กำลังไปตอนถัดไปอัตโนมัติ…" : "ตอนถัดไป"}</small>
              <strong>{chapterLabel(neighbors.next)} · {neighbors.next.title}</strong>
              {gap ? <small>ตอน {missingLabel} ยังไม่พร้อมอ่านบน MoonRead</small> : null}
            </div>
            {shownCountdown !== null
              ? <button ref={endAction} className="pill-btn ghost" type="button" onClick={cancelCountdown}>ยกเลิก</button>
              : <Link ref={endAction} prefetch={false} className="pill-btn primary" href={neighbors.next.href} onNavigate={(e) => follow(e, neighbors.next.href)}>อ่านต่อ <ArrowRight size={17} /></Link>}
          </div>
        ) : (
          <div className="next-card"><div className="nx"><small>จบเท่าที่มีในตอนนี้</small><strong>ขอบคุณที่อ่านกับ MoonRead 🌙</strong></div></div>
        )}
      </div>

      <nav className="reader-bottom-nav" aria-label="ไปยังตอนก่อนหน้าหรือถัดไป">
        {neighbors.previous ? (
          <Link prefetch={false} href={neighbors.previous.href} onNavigate={(e) => follow(e, neighbors.previous.href)}><ChevronLeft size={20} /><span><small>{chapterLabel(neighbors.previous)}</small><strong>{neighbors.previous.title}</strong></span></Link>
        ) : <span className="nav-placeholder" />}
        {neighbors.next ? (
          <Link prefetch={false} className="next" href={neighbors.next.href} onNavigate={(e) => follow(e, neighbors.next.href)}><span><small>{chapterLabel(neighbors.next)}</small><strong>{neighbors.next.title}</strong></span><ChevronRight size={20} /></Link>
        ) : <span className="nav-placeholder" />}
      </nav>

      </div>

      {tocOpen ? (
        <div className="scrim" onClick={() => setTocOpen(false)}>
          <aside ref={tocRef} className={`sheet reader-toc${sheetNight}`} onClick={(e) => e.stopPropagation()} role="dialog" aria-modal="true" aria-labelledby="reader-toc-title">
            <div className="sheet-head">
              <div><strong id="reader-toc-title">สารบัญ</strong><span>{book?.title || "MoonRead"}</span></div>
              <button className="icon-button" type="button" onClick={() => setTocOpen(false)} aria-label="ปิดสารบัญ"><X size={20} /></button>
            </div>
            <div className="searchbox"><span className="ic"><Search size={17} /></span>
              <input value={tocQuery} onChange={(e) => setTocQuery(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter" && !e.nativeEvent.isComposing && tocQuery.trim() && tocFiltered.length === 1 && tocFiltered[0].href) tocRef.current?.querySelector(".sheet-toc a[href]")?.click(); }} placeholder="กระโดดไปตอน…" aria-label="ค้นหาตอน" /></div>
            {navigationMessage}
            <div className="toc-list sheet-toc">
              {!tocFiltered.length ? <p role="status" className="muted-line">ไม่พบตอนที่ค้นหา ลองพิมพ์เลขตอนหรือคำในชื่อตอน</p> : null}
              {tocFiltered.map((item) => {
                if (!item.href) return <div key={item.id} className="ch-row disabled" aria-disabled="true" data-gap="true"><span className="num">{item.number}</span><span className="ct"><strong>{chapterLabel(item)} ยังไม่พร้อมอ่าน</strong></span></div>;
                const isCurrent = item.id === chapter.id;
                const marked = store.isBookmarked(slug, item.id);
                const reviewTarget = review || (marked && !isCurrent && resume?.chapterId !== item.id);
                return <Link key={item.id} ref={isCurrent ? activeChapter : null} aria-current={isCurrent ? "page" : undefined} prefetch={false} className={`ch-row${isCurrent ? " reading" : ""}`} href={reviewTarget ? `${item.href}?review=1` : item.href} onNavigate={(e) => { if (isCurrent) setTocOpen(false); follow(e, item.href, reviewTarget); }}>
                  <span className="num">{String(chapterNumber(item)).padStart(3, "0")}</span>
                  <span className="ct"><strong>{item.title}</strong></span>
                  <span className="cm">{marked ? <Bookmark size={14} role="img" aria-label="คั่นไว้" fill="currentColor" color="var(--gold)" /> : null}</span>
                </Link>;
              })}
            </div>
          </aside>
        </div>
      ) : null}

      {settingsOpen ? (
        <div className="scrim" onClick={() => setSettingsOpen(false)}>
          <aside ref={settingsRef} className={`sheet${sheetNight}`} onClick={(e) => e.stopPropagation()} role="dialog" aria-modal="true" aria-labelledby="reader-settings-title">
            <div className="sheet-head">
              <div><strong id="reader-settings-title">ตั้งค่าการอ่าน</strong><span>ปรับให้สบายตาสำหรับการอ่านยาว</span></div>
              <button className="icon-button" type="button" onClick={() => setSettingsOpen(false)} aria-label="ปิดการตั้งค่า"><X size={20} /></button>
            </div>

            <div className="seg theme-seg">
              {readingThemes.map((t) => { const Ic = t.icon; return (
                <button key={t.id} type="button" aria-pressed={settings.theme === t.id} className={settings.theme === t.id ? "on" : ""} onClick={() => update({ theme: t.id })}><Ic size={17} /> {t.label}</button>
              ); })}
            </div>

            <div className="field">
              <label htmlFor="reader-size"><span><Type size={16} /> ขนาดตัวอักษร</span><span className="v" aria-hidden="true">{settings.fontSize}px</span></label>
              <input id="reader-size" type="range" min="18" max="28" value={settings.fontSize} onChange={(e) => update({ fontSize: Number(e.target.value) })} />
            </div>
            <div className="field">
              <label htmlFor="reader-line"><span><AlignLeft size={16} /> ระยะบรรทัด</span><span className="v" aria-hidden="true">{Number(settings.lineHeight).toFixed(2)}</span></label>
              <input id="reader-line" type="range" min="1.6" max="2.4" step="0.05" value={settings.lineHeight} onChange={(e) => update({ lineHeight: Number(e.target.value) })} />
            </div>
            <div className="field reader-width-field">
              <label htmlFor="reader-width"><span><Menu size={16} /> ความกว้างหน้าอ่าน</span><span className="v" aria-hidden="true">{settings.width}px</span></label>
              <input id="reader-width" type="range" min="600" max="900" step="20" value={settings.width} onChange={(e) => update({ width: Number(e.target.value) })} />
            </div>
            <div className="field">
              <label htmlFor="reader-paragraph"><span><AlignLeft size={16} /> ระยะย่อหน้า</span><span className="v" aria-hidden="true">{Number(settings.paragraphSpacing).toFixed(1)}em</span></label>
              <input id="reader-paragraph" type="range" min="0.8" max="1.8" step="0.1" value={settings.paragraphSpacing} onChange={(e) => update({ paragraphSpacing: Number(e.target.value) })} />
            </div>

            <div className="font-picker-label"><Type size={16} /> ฟอนต์สำหรับอ่าน</div>
            <div className="font-options">
              {readingFonts.map((f) => (
                <button key={f.id} type="button" aria-pressed={settings.fontFamily === f.id} className={`font-option${settings.fontFamily === f.id ? " selected" : ""}`} style={{ fontFamily: f.var }} onClick={() => update({ fontFamily: f.id })}>
                  <span className="font-option-label">{f.label}</span>
                  <span className="font-option-note">{f.note}</span>
                </button>
              ))}
            </div>

            <div className="toggle-row">
              <div><div className="tt">เลื่อนตอนถัดไปอัตโนมัติ</div><div className="td">เมื่ออ่านจบตอน จะนับถอยหลังไปต่อให้เอง</div></div>
              <button type="button" className={`switch${settings.autoAdvance ? " on" : ""}`} aria-pressed={settings.autoAdvance} aria-label="เลื่อนตอนถัดไปอัตโนมัติ" onClick={() => { setCountdownAllowed(!settings.autoAdvance); update({ autoAdvance: !settings.autoAdvance }); }}><i /></button>
            </div>
          </aside>
        </div>
      ) : null}
    </main>
  );
}
