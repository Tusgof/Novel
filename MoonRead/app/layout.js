import "@fontsource/ibm-plex-sans-thai/300.css";
import "@fontsource/ibm-plex-sans-thai/400.css";
import "@fontsource/ibm-plex-sans-thai/500.css";
import "@fontsource/ibm-plex-sans-thai/600.css";
import "@fontsource/ibm-plex-sans-thai/700.css";
import "@fontsource/sarabun/300.css";
import "@fontsource/sarabun/400.css";
import "@fontsource/sarabun/500.css";
import "@fontsource/sarabun/600.css";
import "@fontsource/sarabun/700.css";
import "@fontsource/noto-serif-thai/400.css";
import "@fontsource/noto-serif-thai/500.css";
import "@fontsource/noto-serif-thai/600.css";
import "@fontsource/noto-serif-thai/700.css";
import "@fontsource/maitree/300.css";
import "@fontsource/maitree/400.css";
import "@fontsource/maitree/500.css";
import "@fontsource/maitree/600.css";
import "@fontsource/maitree/700.css";
import "./globals.css";

export const metadata = {
  metadataBase: new URL("https://moonread.vercel.app"),
  title: "MoonRead",
  description: "MoonRead — ชั้นนิยายแปลไทย อ่านฟรี จัดหน้าสบายตา",
  icons: {
    icon: "/icon.svg",
    apple: "/images/apple-touch-icon.png",
  },
  openGraph: {
    title: "MoonRead",
    description: "ชั้นนิยายแปลไทย อ่านฟรี จัดหน้าสบายตา",
    siteName: "MoonRead",
    images: [{ url: "/images/og-image.png", width: 1200, height: 630 }],
    locale: "th_TH",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "MoonRead",
    description: "ชั้นนิยายแปลไทย อ่านฟรี จัดหน้าสบายตา",
    images: ["/images/og-image.png"],
  },
};

export default function RootLayout({ children }) {
  return (
    <html lang="th" data-site-theme="light" data-scroll-behavior="smooth">
      <body>{children}</body>
    </html>
  );
}
