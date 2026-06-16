import Link from "next/link";
import Image from "next/image";
import { LibraryBig } from "lucide-react";
import NavLinks from "./NavLinks";
import ThemeToggle from "./ThemeToggle";

export default function SiteHeader({ bookCount = 2 }) {
  return (
    <header className="site-header">
      <Link className="brand" href="/" aria-label="MoonRead home">
        <Image
          className="brand-logo-img"
          src="/images/moonread-logo.svg"
          alt="MoonRead Stardust Library"
          width={168}
          height={44}
          priority
        />
      </Link>

      <nav className="site-nav" aria-label="Primary navigation">
        <NavLinks />
      </nav>

      <div className="site-header-tools">
        <span className="library-badge">
          <LibraryBig size={16} />
          {bookCount} เรื่อง
        </span>
        <ThemeToggle />
      </div>
    </header>
  );
}
