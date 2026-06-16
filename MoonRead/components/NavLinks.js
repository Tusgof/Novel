"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Home } from "lucide-react";

const links = [
  { href: "/", label: "หน้าแรก", icon: Home },
];

export default function NavLinks() {
  const pathname = usePathname();

  return (
    <>
      {links.map((item) => {
        const Icon = item.icon;
        const active =
          item.href === "/"
            ? pathname === "/"
            : pathname.startsWith(item.href);

        return (
          <Link
            href={item.href}
            key={item.href}
            className={active ? "active" : undefined}
            aria-current={active ? "page" : undefined}
          >
            <Icon size={17} />
            {item.label}
          </Link>
        );
      })}
    </>
  );
}
