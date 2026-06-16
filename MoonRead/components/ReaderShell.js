"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
  AlignLeft,
  BookOpen,
  ChevronLeft,
  ChevronRight,
  List,
  Menu,
  Moon,
  Settings2,
  Sun,
  Type,
  X,
} from "lucide-react";

const defaults = {
  theme: "paper",
  fontSize: 20,
  lineHeight: 2,
  width: 760,
  paragraphSpacing: 1.25,
  fontFamily: "sarabun",
};

const readingFonts = [
  { id: "sarabun", label: "Sarabun", note: "สมดุล อ่านสบาย ใช้งานได้ยาว", var: "var(--reader-font-sarabun)" },
  { id: "plex", label: "IBM Plex Sans Thai", note: "คม ชัด เป็นระเบียบ", var: "var(--reader-font-ui)" },
  { id: "serif", label: "Noto Serif Thai", note: "อารมณ์นิยาย คล้ายหนังสือเล่ม", var: "var(--reader-font-serif)" },
  { id: "maitree", label: "Maitree", note: "นุ่ม อ่านต่อเนื่องดี", var: "var(--reader-font-maitree)" },
];

const readingThemes = [
  { id: "paper", label: "กระดาษ", icon: Sun },
  { id: "sepia", label: "ซีเปีย", icon: AlignLeft },
  { id: "night", label: "กลางคืน", icon: Moon },
];

function fontVarFor(id) {
  const match = readingFonts.find((font) => font.id === id);
  return match ? match.var : "var(--reader-font-sarabun)";
}

function blockClass(block) {
  if (block.type === "title") return "reader-title";
  if (block.type === "heading") return "reader-heading";
  if (/^[“"']/.test(block.text)) return "reader-paragraph dialogue";
  if (/^\(.+\)$/.test(block.text)) return "reader-paragraph aside";
  return "reader-paragraph";
}

function chapterLabel(chapter) {
  return `ตอน ${String(chapter.number).padStart(3, "0")}`;
}

function renderInlineMarkdown(text) {
  const parts = [];
  const pattern = /(\*\*([^*]+)\*\*|\*([^*]+)\*)/g;
  let lastIndex = 0;
  let match;

  while ((match = pattern.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push(text.slice(lastIndex, match.index));
    }
    if (match[2]) {
      parts.push(<strong key={`strong-${match.index}`}>{match[2]}</strong>);
    } else if (match[3]) {
      parts.push(<em key={`em-${match.index}`}>{match[3]}</em>);
    }
    lastIndex = pattern.lastIndex;
  }

  if (lastIndex < text.length) {
    parts.push(text.slice(lastIndex));
  }
  return parts;
}

export default function ReaderShell({ chapter, neighbors, chapters, blocks, book }) {
  const [settings, setSettings] = useState(defaults);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [tocOpen, setTocOpen] = useState(false);
  const [hiddenChrome, setHiddenChrome] = useState(false);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const saved = window.localStorage.getItem("moonread-reader-settings")
      || window.localStorage.getItem("dse-reader-settings");
    if (!saved) return;

    window.requestAnimationFrame(() => {
      try {
        setSettings({ ...defaults, ...JSON.parse(saved) });
      } catch {
        setSettings(defaults);
      }
    });
  }, []);

  useEffect(() => {
    window.localStorage.setItem("moonread-reader-settings", JSON.stringify(settings));
  }, [settings]);

  useEffect(() => {
    window.localStorage.setItem(
      "dse-last-read",
      JSON.stringify({ id: chapter.id, title: chapter.title, href: chapter.href, book: book?.slug || "deep-sea-embers" })
    );
  }, [book?.slug, chapter.href, chapter.id, chapter.title]);

  useEffect(() => {
    let lastY = window.scrollY;

    const onScroll = () => {
      const max = document.documentElement.scrollHeight - window.innerHeight;
      setProgress(max > 0 ? Math.min(100, Math.max(0, (window.scrollY / max) * 100)) : 0);
      setHiddenChrome(window.scrollY > 180 && window.scrollY > lastY);
      lastY = window.scrollY;
    };

    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const readerStyle = {
    "--reader-font-family": fontVarFor(settings.fontFamily),
    "--reader-font-size": `${settings.fontSize}px`,
    "--reader-line-height": settings.lineHeight,
    "--reader-width": `${settings.width}px`,
    "--reader-paragraph-spacing": `${settings.paragraphSpacing}em`,
  };

  return (
    <main className={`reader-page theme-${settings.theme}`} style={readerStyle}>
      <div className={`reader-topbar ${hiddenChrome ? "hidden" : ""}`}>
        <Link href={book?.chaptersHref || "/chapters"} className="icon-button" aria-label="กลับไปสารบัญ">
          <ChevronLeft size={20} />
        </Link>
        <div className="reader-top-title">
          <strong>{chapter.title}</strong>
          <span>{Math.round(progress)}% ของตอนนี้</span>
        </div>
        <button className="icon-button" type="button" onClick={() => setTocOpen(true)} aria-label="เปิดสารบัญ">
          <List size={20} />
        </button>
        <button className="icon-button" type="button" onClick={() => setSettingsOpen(true)} aria-label="ตั้งค่าการอ่าน">
          <Settings2 size={20} />
        </button>
        <span className="progress-line" style={{ transform: `scaleX(${progress / 100})` }} />
      </div>

      <section className="reader-head">
        <span className="reader-kicker">{chapterLabel(chapter)}</span>
        <h1>{chapter.title}</h1>
        <p>MoonRead · {book?.title || "Deep Sea Embers"} · ประมาณ {chapter.readingMinutes} นาที</p>
      </section>

      <article className="reader-article">
        {blocks.map((block, index) => {
          if (block.type === "title") {
            return (
              <h2 className={blockClass(block)} key={`${block.type}-${index}`}>
                {block.text}
              </h2>
            );
          }
          if (block.type === "heading") {
            return (
              <h3 className={blockClass(block)} key={`${block.type}-${index}`}>
                {block.text}
              </h3>
            );
          }
          return (
            <p className={blockClass(block)} key={`${block.type}-${index}`}>
              {renderInlineMarkdown(block.text)}
            </p>
          );
        })}
      </article>

      <nav className="reader-bottom-nav" aria-label="Chapter navigation">
        {neighbors.previous ? (
          <Link href={neighbors.previous.href}>
            <ChevronLeft size={20} />
            <span>
              <small>{chapterLabel(neighbors.previous)}</small>
              <strong>{neighbors.previous.title}</strong>
            </span>
          </Link>
        ) : (
          <span className="nav-placeholder" />
        )}
        {neighbors.next ? (
          <Link href={neighbors.next.href}>
            <span>
              <small>{chapterLabel(neighbors.next)}</small>
              <strong>{neighbors.next.title}</strong>
            </span>
            <ChevronRight size={20} />
          </Link>
        ) : (
          <span className="nav-placeholder" />
        )}
      </nav>

      {tocOpen ? (
        <aside className="reader-drawer" aria-label="สารบัญตอน">
          <div className="drawer-panel">
            <div className="drawer-head">
              <div>
                <strong>สารบัญ</strong>
                <span>{book?.title || "Deep Sea Embers"}</span>
              </div>
              <button className="icon-button" type="button" onClick={() => setTocOpen(false)} aria-label="ปิดสารบัญ">
                <X size={20} />
              </button>
            </div>
            <div className="drawer-list">
              {chapters.map((item) => (
                <Link
                  className={item.id === chapter.id ? "active" : ""}
                  href={item.href}
                  key={item.id}
                  onClick={() => setTocOpen(false)}
                >
                  <BookOpen size={16} />
                  <span>
                    <small>{chapterLabel(item)}</small>
                    <strong>{item.title}</strong>
                  </span>
                </Link>
              ))}
            </div>
          </div>
        </aside>
      ) : null}

      {settingsOpen ? (
        <aside className="reader-drawer" aria-label="ตั้งค่าการอ่าน">
          <div className="drawer-panel settings-panel">
            <div className="drawer-head">
              <div>
                <strong>ตั้งค่าการอ่าน</strong>
                <span>ปรับฟอนต์และโทนหน้ากระดาษให้เหมาะกับการอ่านยาว</span>
              </div>
              <button className="icon-button" type="button" onClick={() => setSettingsOpen(false)} aria-label="ปิดการตั้งค่า">
                <X size={20} />
              </button>
            </div>

            <label>
              <span><Type size={17} /> ขนาดตัวอักษร</span>
              <input
                type="range"
                min="18"
                max="28"
                value={settings.fontSize}
                onChange={(event) => setSettings({ ...settings, fontSize: Number(event.target.value) })}
              />
            </label>

            <label>
              <span><AlignLeft size={17} /> ระยะบรรทัด</span>
              <input
                type="range"
                min="1.7"
                max="2.3"
                step="0.05"
                value={settings.lineHeight}
                onChange={(event) => setSettings({ ...settings, lineHeight: Number(event.target.value) })}
              />
            </label>

            <label>
              <span><Menu size={17} /> ความกว้างหน้าอ่าน</span>
              <input
                type="range"
                min="620"
                max="920"
                step="20"
                value={settings.width}
                onChange={(event) => setSettings({ ...settings, width: Number(event.target.value) })}
              />
            </label>

            <label>
              <span><AlignLeft size={17} /> ระยะย่อหน้า</span>
              <input
                type="range"
                min="0.9"
                max="1.8"
                step="0.1"
                value={settings.paragraphSpacing}
                onChange={(event) => setSettings({ ...settings, paragraphSpacing: Number(event.target.value) })}
              />
            </label>

            <div className="font-picker">
              <span className="font-picker-label"><Type size={17} /> ฟอนต์สำหรับอ่าน</span>
              <div className="font-options">
                {readingFonts.map((font) => (
                  <button
                    type="button"
                    key={font.id}
                    className={settings.fontFamily === font.id ? "font-option selected" : "font-option"}
                    style={{ fontFamily: font.var }}
                    onClick={() => setSettings({ ...settings, fontFamily: font.id })}
                  >
                    <span className="font-option-label">{font.label}</span>
                    <span className="font-option-note">{font.note}</span>
                  </button>
                ))}
              </div>
            </div>

            <div className="theme-switcher" id="reader-settings">
              {readingThemes.map((theme) => {
                const Icon = theme.icon;
                return (
                  <button
                    type="button"
                    key={theme.id}
                    className={settings.theme === theme.id ? "selected" : ""}
                    onClick={() => setSettings({ ...settings, theme: theme.id })}
                  >
                    <Icon size={18} />
                    {theme.label}
                  </button>
                );
              })}
            </div>
          </div>
        </aside>
      ) : null}
    </main>
  );
}
