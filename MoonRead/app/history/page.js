import { Suspense } from "react";
import AppHeader from "../../components/AppHeader";
import BottomNav from "../../components/BottomNav";
import SiteFooter from "../../components/SiteFooter";
import { HistoryView } from "../../components/Shelf";
import { getBooks } from "../../lib/chapters";

export const metadata = { title: "ประวัติการอ่าน | MoonRead" };

export default function HistoryPage() {
  return (
    <>
      <AppHeader />
      <Suspense fallback={<div className="page shell" />}>
        <HistoryView books={getBooks()} />
      </Suspense>
      <SiteFooter />
      <BottomNav />
    </>
  );
}
