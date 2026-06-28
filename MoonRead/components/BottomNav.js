"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Compass, Heart, History } from "lucide-react";

const NAV = [
  { href: "/", label: "ค้นพบ", icon: Compass, match: (p) => p === "/" || p.startsWith("/book") || p.startsWith("/books") },
  { href: "/shelf", label: "ชั้นหนังสือ", icon: Heart, match: (p) => p.startsWith("/shelf") },
  { href: "/history", label: "ประวัติ", icon: History, match: (p) => p.startsWith("/history") },
];

export default function BottomNav() {
  const pathname = usePathname();
  return (
    <nav className="botnav" aria-label="Mobile navigation">
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
