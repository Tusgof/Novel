import Link from "next/link";
import { Clock3, CheckCircle2, Lock, XCircle } from "lucide-react";
import AppHeader from "../../components/AppHeader";
import BottomNav from "../../components/BottomNav";
import SiteFooter from "../../components/SiteFooter";
import { getManifest } from "../../lib/chapters";

function icon(status) {
  if (status === "available") return <CheckCircle2 size={18} />;
  if (status === "rejected") return <XCircle size={18} />;
  return <Lock size={18} />;
}

export const metadata = { title: "สารบัญ | MoonRead" };

export default function ChaptersPage() {
  const manifest = getManifest();
  const { novel, summary, chapters } = manifest;

  return (
    <>
      <AppHeader />
      <div className="page shell">
        <section className="page-title">
          <span className="eyebrow gold">สารบัญ</span>
          <h1>สารบัญ {novel.title}</h1>
          <p>รวม {summary.available} ตอนที่พร้อมอ่าน — ตอนที่ยังไม่พร้อมจะแสดงเป็นรายการปิดไว้จนกว่าจะเข้าคลัง</p>
        </section>

        <div className="toc-list" style={{ marginTop: 8 }}>
          {chapters.map((c) => {
            const disabled = c.status !== "available";
            const label = `ตอน ${String(c.number).padStart(3, "0")}`;
            const inner = (
              <>
                <span className="num">{String(c.number).padStart(3, "0")}</span>
                <span className="ct"><small>{label}</small><strong>{disabled ? `${label} ยังไม่พร้อมอ่าน` : c.title}</strong></span>
                <span className="cm"><Clock3 size={13} /> {disabled ? (c.status === "rejected" ? "รอตรวจไฟล์" : "เร็วๆ นี้") : `${c.readingMinutes} น.`}</span>
                <span className={`ch-state ${c.status}`}>{icon(c.status)}</span>
              </>
            );
            return disabled
              ? <div className="ch-row disabled" key={c.id} aria-disabled="true">{inner}</div>
              : <Link className="ch-row" key={c.id} href={c.href}>{inner}</Link>;
          })}
        </div>
      </div>
      <SiteFooter />
      <BottomNav />
    </>
  );
}
