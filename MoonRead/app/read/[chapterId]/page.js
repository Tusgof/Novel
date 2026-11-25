import { notFound } from "next/navigation";
import ReaderShell from "../../../components/ReaderShell";
import {
  getAvailableChapters,
  getChapter,
  getChapterMarkdown,
  getChapterNeighbors,
  getManifest,
  markdownToBlocks,
} from "../../../lib/chapters";

export function generateStaticParams() {
  return getAvailableChapters().map((chapter) => ({ chapterId: chapter.id }));
}

export async function generateMetadata({ params }) {
  const { chapterId } = await params;
  const chapter = getChapter(chapterId);
  return { title: chapter ? `${chapter.title} | MoonRead` : "MoonRead" };
}

export default async function ReadChapterPage({ params }) {
  const { chapterId } = await params;
  const chapter = getChapter(chapterId);
  const markdown = getChapterMarkdown(chapterId);

  if (!chapter || !markdown) notFound();

  return (
    <ReaderShell
      key={chapter.id}
      chapter={chapter}
      neighbors={getChapterNeighbors(chapterId)}
      chapters={getAvailableChapters().map(({ id, number, title, href }) => ({ id, number, title, href }))}
      blocks={markdownToBlocks(markdown)}
      book={{ slug: getManifest().novel.slug, title: getManifest().novel.title, chaptersHref: "/chapters" }}
    />
  );
}
