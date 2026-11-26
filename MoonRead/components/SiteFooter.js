import Link from "next/link";

export default function SiteFooter() {
  return (
    <footer className="site-footer">
      <div className="footer-inner">
        <span className="footer-brand">MoonRead</span>
        <nav className="footer-links" aria-label="Footer navigation">
          <Link prefetch={false} href="/">ค้นพบ</Link>
          <Link prefetch={false} href="/shelf">ชั้นหนังสือ</Link>
          <Link prefetch={false} href="/history">ประวัติ</Link>
        </nav>
        <span className="footer-note">แปลไทยโดยแฟน · อ่านฟรี</span>
      </div>
    </footer>
  );
}
