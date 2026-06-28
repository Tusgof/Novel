import { Suspense } from "react";
import AppHeader from "../../components/AppHeader";
import BottomNav from "../../components/BottomNav";
import SiteFooter from "../../components/SiteFooter";
import { ShelfView } from "../../components/Shelf";
import { getBooks } from "../../lib/chapters";

export const metadata = { title: "ชั้นหนังสือ | MoonRead" };

export default function ShelfPage() {
  return (
    <>
      <AppHeader />
      <Suspense fallback={<div className="page shell" />}>
        <ShelfView books={getBooks()} />
      </Suspense>
      <SiteFooter />
      <BottomNav />
    </>
  );
}
