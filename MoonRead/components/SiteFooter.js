import Link from "next/link";

export default function SiteFooter() {
  return (
    <footer className="site-footer">
      <div className="footer-inner">
        <span className="footer-brand">MoonRead</span>
        <nav className="footer-links" aria-label="Footer navigation">
          <Link href="/">ค้นพบ</Link>
          <Link href="/shelf">ชั้นหนังสือ</Link>
          <Link href="/history">ประวัติ</Link>
        </nav>
        <span className="footer-note">แปลไทยโดยแฟน · อ่านฟรี</span>
      </div>
    </footer>
  );
}
