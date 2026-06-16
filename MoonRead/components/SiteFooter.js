import Link from "next/link";

export default function SiteFooter() {
  return (
    <footer className="site-footer">
      <div className="footer-inner">
        <span className="footer-brand">MoonRead</span>
        <nav className="footer-links" aria-label="Footer navigation">
          <Link href="/">หน้าแรก</Link>
        </nav>
        <span className="footer-note">แปลไทยโดยแฟน · อ่านฟรี</span>
      </div>
    </footer>
  );
}
