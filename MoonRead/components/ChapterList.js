"use client";

import { Fragment } from "react";
import { Compass } from "lucide-react";
import ChapterFinder from "./ChapterFinder";
import ChapterRow from "./ChapterRow";
import { bookmarkDestination } from "../lib/bookmark-links";
import { useReaderStore } from "../lib/reader-store";

export default function ChapterList({ chapters, slug, initialSearch }) {
  const store = useReaderStore();
  const progress = store.getProgress(slug);
  return <ChapterFinder chapters={chapters} initialSearch={initialSearch} renderRows={(filtered, returnChapterId) => (
    <div className="toc-list">
      {filtered.map((chapter) => {
        const reading = progress?.chapterId === chapter.id;
        const bookmark = progress && !reading && store.isBookmarked(slug, chapter.id) ? bookmarkDestination(chapter, progress) : undefined;
        return <Fragment key={chapter.id}>
          <ChapterRow slug={slug} chapter={chapter} store={store} reading={reading} bookmark={bookmark} linkId={`chapter-${chapter.id}`} />
          {chapter.status === "available" && chapter.id === returnChapterId ? (
            // Use document navigation to start Discover at the top.
            // eslint-disable-next-line @next/next/no-html-link-for-pages
            <a className="toc-discover text-link" href="/" tabIndex={0}><Compass size={16} aria-hidden="true" /> กลับหน้าแรก · ค้นพบ</a>
          ) : null}
        </Fragment>;
      })}
    </div>
  )} />;
}
