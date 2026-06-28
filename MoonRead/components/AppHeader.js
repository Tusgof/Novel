"use client";

import Link from "next/link";
import Image from "next/image";
import { useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { Compass, Heart, History, Search, Moon, Sun, X } from "lucide-react";
import { useReaderStore } from "../lib/reader-store";

const NAV = [
  { href: "/", label: "ค้นพบ", icon: Compass, match: (p) => p === "/" || p.startsWith("/book") || p.startsWith("/books") },
  { href: "/shelf", label: "ชั้นหนังสือ", icon: Heart, match: (p) => p.startsWith("/shelf") },
  { href: "/history", label: "ประวัติ", icon: History, match: (p) => p.startsWith("/history") },
];

export default function AppHeader() {
  const pathname = usePathname();
  const router = useRouter();
  const [query, setQuery] = useState("");
  const [dark, setDark] = useState(false);

  useReaderStore();

  function toggleDark() {
    const next = dark ? "light" : "dark";
    setDark(!dark);
    if (typeof document !== "undefined") {
      document.documentElement.dataset.siteTheme = next;
      try { window.localStorage.setItem("moonread-site-theme", next); } catch {}
    }
  }

  function submit(e) {
    e.preventDefault();
    const q = query.trim();
    router.push(q ? `/?q=${encodeURIComponent(q)}` : "/");
  }

  return (
    <header className="appbar">
      <div className="appbar-inner">
        <Link className="brand" href="/" aria-label="MoonRead home">
          <Image src="/images/moonread-logo.svg" alt="MoonRead" width={168} height={44} priority />
        </Link>

        <nav className="appbar-nav" aria-label="Primary navigation">
          {NAV.map((n) => {
            const Icon = n.icon;
            const active = n.match(pathname);
            return (
              <Link key={n.href} href={n.href} className={active ? "active" : undefined} aria-current={active ? "page" : undefined}>
                <Icon size={16} /> {n.label}
              </Link>
            );
          })}
        </nav>

        <form className="appbar-search" onSubmit={submit} role="search">
          <div className="searchbox">
            <span className="ic"><Search size={18} /></span>
            <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="ค้นหานิยาย ผู้แต่ง หรือหมวด" aria-label="ค้นหานิยาย" />
            {query ? <button type="button" className="ic clear" onClick={() => setQuery("")} aria-label="ล้างคำค้น"><X size={16} /></button> : null}
          </div>
        </form>

        <div className="appbar-tools">
          <button className="iconbtn" type="button" onClick={toggleDark} aria-label={dark ? "โหมดสว่าง" : "โหมดมืด"} title={dark ? "โหมดสว่าง" : "โหมดมืด"}>
            {dark ? <Sun size={19} /> : <Moon size={19} />}
          </button>
        </div>
      </div>
    </header>
  );
}
