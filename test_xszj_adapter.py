import unittest

from novel_pipeline.adapters.xszj import XszjAdapter
from novel_pipeline.types import SourceConfig


class XszjAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.adapter = XszjAdapter(SourceConfig(
            adapter="xszj",
            toc_url="https://xszj.org/b/351379/cs/1",
            delay_seconds=0,
            encoding="utf-8",
            extra={"max_catalog_pages": 2},
        ))

    def test_extract_content_uses_content_paragraphs_only(self) -> None:
        raw = '<div id="content"><div id="booktxt"><p>第一段。</p><p>第二段。</p><script>ad()</script></div></div>'.encode("utf-8")
        self.assertEqual(self.adapter.extract_content(raw), "第一段。\n\n第二段。")

    def test_build_manifest_deduplicates_and_numbers_chapters(self) -> None:
        self.adapter.fetch_url = lambda url: (
            '<a rel="chapter" href="/b/351379/c/1" title="第1章 一"></a>'.encode("utf-8")
            + '<a rel="chapter" href="/b/351379/c/2" title="第2章 二"></a>'.encode("utf-8")
        )
        manifest = self.adapter.build_manifest()
        self.assertEqual([item.chapter_id for item in manifest], ["ch001", "ch002"])
        self.assertEqual(manifest[0].metadata["source_site"], "xszj")

    def test_catalog_parser_follows_next_page_anchor(self) -> None:
        self.adapter.fetch_url = lambda url: (
            ('<a rel="chapter" href="/b/351379/c/1" title="第1章 一"></a>'
             if url.endswith("/cs/1")
             else '<a rel="chapter" href="/b/351379/c/201" title="第201章 二"></a>')
            + ('<a href="/b/351379/cs/2" class="index-container-btn">下一页</a>'
               if url.endswith("/cs/1") else '')
        ).encode("utf-8")
        manifest = self.adapter.build_manifest()
        self.assertEqual([item.chapter_id for item in manifest], ["ch001", "ch201"])

    def test_catalog_pagination_normalizes_relative_urls_before_loop_check(self) -> None:
        self.adapter.config.extra["max_catalog_pages"] = 3
        pages = {
            "https://xszj.org/b/351379/cs/1": (
                '<a rel="chapter" href="/b/351379/c/1" title="第1章 一"></a>'
                '<a href="/b/351379/cs/2" class="index-container-btn">下一页</a>'
            ),
            "https://xszj.org/b/351379/cs/2": (
                '<a rel="chapter" href="/b/351379/c/201" title="第201章 二"></a>'
                '<a href="/b/351379/cs/1" class="index-container-btn">上一页</a>'
                '<a href="/b/351379/cs/3" class="index-container-btn">下一页</a>'
            ),
            "https://xszj.org/b/351379/cs/3": (
                '<a rel="chapter" href="/b/351379/c/401" title="第401章 三"></a>'
            ),
        }
        self.adapter.fetch_url = lambda url: pages[url].encode("utf-8")
        manifest = self.adapter.build_manifest()
        self.assertEqual([item.chapter_id for item in manifest], ["ch001", "ch201", "ch401"])

    def test_chapter_continuation_uses_rel_prev_page_link(self) -> None:
        pages = {
            "https://xszj.org/b/351379/c/1": (
                '<div id="content"><div id="booktxt"><p>第一部分。</p></div></div>'
                '<a rel="prev" href="/b/351379/c/1?page=2">下一页</a>'
            ),
            "https://xszj.org/b/351379/c/1?page=2": (
                '<div id="content"><div id="booktxt"><p>第二部分。</p></div></div>'
            ),
        }
        self.adapter.fetch_url = lambda url: pages[url].encode("utf-8")
        meta = type("Meta", (), {"url": "https://xszj.org/b/351379/c/1", "chapter_id": "ch001"})()
        self.assertEqual(self.adapter.fetch_chapter_text(meta), "第一部分。\n\n第二部分。")


if __name__ == "__main__":
    unittest.main()
