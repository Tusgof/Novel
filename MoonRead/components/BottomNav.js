"use client";

import Link from "next/link";
import { useEffect, useRef } from "react";
import { usePathname } from "next/navigation";
import { Compass, Heart, History } from "lucide-react";

const NAV = [
  { href: "/", label: "ค้นพบ", icon: Compass, match: (p) => p === "/" || p.startsWith("/book") || p.startsWith("/books") },
  { href: "/shelf", label: "ชั้นหนังสือ", icon: Heart, match: (p) => p.startsWith("/shelf") },
  { href: "/history", label: "ประวัติ", icon: History, match: (p) => p.startsWith("/history") },
];

export default function BottomNav() {
  const pathname = usePathname();
  const bar = useRef(null);
  useEffect(() => {
    let frame;
    const reveal = (event) => {
      const focused = event.target;
      if (!focused.matches?.("a[href], button, input, select, textarea, summary, [tabindex='0']") || !focused.closest("main") || !bar.current?.getClientRects().length) return;
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(() => {
        if (document.activeElement !== focused || !focused.matches(":focus-visible")) return;
        const rect = focused.getBoundingClientRect();
        const bottom = bar.current.getBoundingClientRect().top - 8;
        const top = (document.querySelector(".appbar")?.getBoundingClientRect().bottom || 0) + 8;
        const delta = rect.bottom > bottom ? rect.bottom - bottom : rect.top < top ? rect.top - top : 0;
        if (delta) window.scrollBy({ top: delta, behavior: "instant" });
      });
    };
    document.addEventListener("focusin", reveal);
    return () => { document.removeEventListener("focusin", reveal); cancelAnimationFrame(frame); };
  }, []);
  return (
    <nav ref={bar} className="botnav" aria-label="เมนูหลักบนมือถือ">
      {NAV.map((n) => {
        const Icon = n.icon;
        const active = n.match(pathname);
        return (
          <Link key={n.href} href={n.href} className={active ? "active" : undefined} aria-current={active ? "page" : undefined}>
            <Icon size={20} /> {n.label}
          </Link>
        );
      })}
    </nav>
  );
}
