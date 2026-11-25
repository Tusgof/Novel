import Link from "next/link";
import Image from "next/image";
import ChapterRecovery from "../components/ChapterRecovery";
import { getBooks } from "../lib/chapters";

export default function NotFound() {
  return (
    <main className="not-found" id="main-content" tabIndex={-1}>
      <div className="not-found-art">
        <Image src="/images/404-cat.png" alt="" width={220} height={220} priority />
      </div>
      <h1>ไม่พบหน้านี้</h1>
      <p>หน้าที่คุณกำลังมองหาอาจถูกย้าย หรือยังไม่พร้อมให้อ่าน</p>
      <ChapterRecovery slugs={getBooks().map((book) => book.slug)} />
      <Link className="pill-btn primary" href="/">กลับหน้าแรก</Link>
    </main>
  );
}
