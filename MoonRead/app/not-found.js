import Link from "next/link";
import Image from "next/image";

export default function NotFound() {
  return (
    <main className="not-found">
      <div className="not-found-art">
        <Image src="/images/404-cat.png" alt="" width={220} height={220} priority />
      </div>
      <h1>ไม่พบหน้านี้</h1>
      <p>หน้าที่คุณกำลังมองหาอาจถูกย้าย หรือยังไม่พร้อมให้อ่าน</p>
      <Link className="pill-btn primary" href="/">กลับหน้าแรก</Link>
    </main>
  );
}
