"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export default function ChapterRecovery({ slugs }) {
  const path = usePathname();
  if (/^\/read\/[^/]+\/?$/.test(path)) return <Link className="pill-btn ghost" href="/chapters">กลับไปสารบัญเรื่องนี้</Link>;
  const slug = path.match(/^\/books\/([^/]+)\/read\/[^/]+\/?$/)?.[1];
  return slugs.includes(slug) ? <Link className="pill-btn ghost" href={`/books/${slug}/chapters`}>กลับไปสารบัญเรื่องนี้</Link> : null;
}
