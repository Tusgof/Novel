"use client";

import Link from "next/link";
import Image from "next/image";
import { useEffect, useRef, useState, useSyncExternalStore } from "react";
import { usePathname } from "next/navigation";
import { Compass, Heart, History, Search, Moon, Sun, X } from "lucide-react";

const NAV = [
  { href: "/", label: "ค้นพบ", icon: Compass, match: (p) => p === "/" || p.startsWith("/book") || p.startsWith("/books") },
  { href: "/shelf", label: "ชั้นหนังสือ", icon: Heart, match: (p) => p.startsWith("/shelf") },
  { href: "/history", label: "ประวัติ", icon: History, match: (p) => p.startsWith("/history") },
];

// Site theme lives in localStorage under the existing key and is read through
// an external store, so the server render and first hydration render stay
// "light" and the stored value only takes over after hydration.
const SITE_THEME_KEY = "moonread-site-theme";
const siteThemeListeners = new Set();
let siteThemeSnapshot = null;

function readSiteTheme() {
  try {
    return window.localStorage.getItem(SITE_THEME_KEY) === "dark" ? "dark" : "light";
  } catch {
    return "light";
  }
}
function getSiteTheme() {
  if (siteThemeSnapshot === null) siteThemeSnapshot = readSiteTheme();
  return siteThemeSnapshot;
}
function getServerSiteTheme() {
  return "light";
}
function subscribeSiteTheme(listener) {
  siteThemeListeners.add(listener);
  return () => { siteThemeListeners.delete(listener); };
}
function setSiteTheme(next) {
  siteThemeSnapshot = next;
  if (typeof window !== "undefined") {
    try { window.localStorage.setItem(SITE_THEME_KEY, next); } catch {}
    document.documentElement.dataset.siteTheme = next;
  }
  siteThemeListeners.forEach((listener) => listener());
}

export default function AppHeader() {
  const pathname = usePathname();
  const field = useRef(null);
  const [query, setQuery] = useState("");
  const siteTheme = useSyncExternalStore(subscribeSiteTheme, getSiteTheme, getServerSiteTheme);
  const dark = siteTheme === "dark";

  useEffect(() => {
    document.documentElement.dataset.siteTheme = siteTheme;
  }, [siteTheme]);

  function toggleDark() {
    setSiteTheme(dark ? "light" : "dark");
  }

  return (
    <header className="appbar">
      <div className="appbar-inner">
        <Link prefetch={false} className="brand" href="/" aria-label="หน้าแรก MoonRead">
          <Image src="/images/moonread-logo.svg" alt="MoonRead" width={168} height={44} priority />
        </Link>

        <nav className="appbar-nav" aria-label="เมนูหลัก">
          {NAV.map((n) => {
            const Icon = n.icon;
            const active = n.match(pathname);
            return (
              <Link prefetch={false} key={n.href} href={n.href} className={active ? "active" : undefined} aria-current={active ? "page" : undefined}>
                <Icon size={16} /> {n.label}
              </Link>
            );
          })}
        </nav>

        <form className="appbar-search" action="/#catalog" method="get" role="search" aria-label="ค้นหาจากแถบนำทาง">
          <div className="searchbox">
            <span className="ic"><Search size={18} /></span>
            <input ref={field} type="search" name="q" onChange={(e) => setQuery(e.target.value)} placeholder="ค้นหานิยาย ผู้แต่ง หรือหมวด" aria-label="ค้นหานิยาย" />
            {query ? <button type="button" className="ic clear" onClick={() => { field.current.value = ""; setQuery(""); field.current.focus(); }} aria-label="ล้างคำค้น"><X size={16} /></button> : null}
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
