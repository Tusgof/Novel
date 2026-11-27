import unittest

from novel_pipeline.adapters.toonnovel import ToonnovelAdapter, normalize_title
from novel_pipeline.types import SourceConfig


def _bubble(pid: int) -> str:
    return (
        f'<button type="button" class="pcom-bubble" data-pid="{pid}" '
        f'aria-label="Comments on paragraph {pid}"><svg width="14" height="14">'
        f'<path d="M21 6v10"></path></svg><span class="pcom-cnt" data-pid="{pid}">3</span></button>'
    )


class ToonnovelAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.adapter = ToonnovelAdapter(SourceConfig(
            adapter="toonnovel",
            toc_url="https://toonnovel.com/novel/demo-novel/",
            delay_seconds=0,
            encoding="utf-8",
        ))

    def test_build_manifest_reads_catalog_links_and_titles(self) -> None:
        self.adapter.fetch_url = lambda url: (
            '<nav><a href="/novel/other/chapter/1/">Chapter 1: Other book</a></nav>'
            '<a href="/novel/demo-novel/chapter/2/">Chapter 2: Awakening!</a>'
            '<a href="/novel/demo-novel/chapter/1/">Chapter 1: I Married To The Ice Empress</a>'
        ).encode("utf-8")
        manifest = self.adapter.build_manifest()
        self.assertEqual([item.chapter_id for item in manifest], ["ch001", "ch002"])
        self.assertEqual(manifest[0].title, "Chapter 1 - I Married To The Ice Empress")
        self.assertEqual(manifest[0].url, "https://toonnovel.com/novel/demo-novel/chapter/1/")
        self.assertEqual(manifest[1].metadata["site_chapter"], 2)
        self.assertEqual(manifest[1].metadata["source_site"], "toonnovel")

    def test_build_manifest_fails_closed_without_chapter_links(self) -> None:
        self.adapter.fetch_url = lambda url: b"<html><body>No catalog here.</body></html>"
        with self.assertRaises(ValueError):
            self.adapter.build_manifest()

    def test_extract_content_drops_comment_buttons_and_scripts(self) -> None:
        story = " ".join(["The wastrel woke up in a cold room."] * 20)
        raw = (
            '<div class="ch-end-card">Not story text</div>'
            f'<div id="content"><p data-pid="1">&quot;UGH!&quot;{_bubble(1)}</p>'
            f'<p data-pid="2">{story}{_bubble(2)}</p>'
            '<p data-pid="3"><em>Still</em> story.<script>track()</script></p></div>'
            '<div class="action-row">Report</div>'
        ).encode("utf-8")
        self.assertEqual(
            self.adapter.extract_content(raw),
            '"UGH!"\n' + story + "\nStill story.",
        )

    def test_extract_content_fails_closed_without_body(self) -> None:
        raw = b'<div class="action-row">Report</div>'
        with self.assertRaises(ValueError):
            self.adapter.extract_content(raw)

    def test_short_body_fails_closed(self) -> None:
        raw = b'<div id="content"><p data-pid="1">Too short.</p></div>'
        with self.assertRaises(ValueError):
            self.adapter.extract_content(raw)

    def test_normalize_title_keeps_generic_heading(self) -> None:
        self.assertEqual(normalize_title("Chapter 7", 7), "Chapter 7")
        self.assertEqual(normalize_title("", 7), "Chapter 7")
        self.assertEqual(
            normalize_title("Chapter 249: Farewell [4]", 249),
            "Chapter 249 - Farewell [4]",
        )


if __name__ == "__main__":
    unittest.main()
