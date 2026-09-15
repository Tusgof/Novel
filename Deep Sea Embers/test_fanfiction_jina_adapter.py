import unittest

from novel_pipeline.adapters.fanfiction_jina import FanfictionJinaAdapter
from novel_pipeline.types import SourceConfig


def _payload(chapter: int, title: str, body: str = "Story body.") -> bytes:
    return (
        f"Title: Story Chapter {chapter}: {title}, a fanfic\n\n"
        f"URL Source: http://www.fanfiction.net/s/123/{chapter}/Story-Slug\n\n"
        "Markdown Content:\n"
        f"**Chapter {chapter}: {title}**\n\n* * *\n\n{body}\n"
    ).encode("utf-8")


class FanfictionJinaAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.adapter = FanfictionJinaAdapter(
            SourceConfig(
                adapter="fanfiction_jina",
                toc_url="https://www.fanfiction.net/s/123/1/Story-Slug",
                delay_seconds=0,
                encoding="utf-8",
                extra={"max_chapter": 2},
            )
        )

    def test_build_manifest_reads_configured_range_and_titles(self) -> None:
        self.adapter.fetch_url = lambda url: _payload(
            int(url.split("/s/123/")[1].split("/", 1)[0]),
            "Arrival" if "/1/" in url else "Return",
        )

        manifest = self.adapter.build_manifest()

        self.assertEqual([item.chapter_id for item in manifest], ["ch001", "ch002"])
        self.assertEqual(manifest[0].title, "Chapter 1: Arrival")
        self.assertEqual(manifest[1].metadata["site_chapter"], 2)
        self.assertTrue(manifest[0].url.startswith("https://r.jina.ai/http://"))

    def test_extract_content_removes_jina_metadata_and_duplicate_title(self) -> None:
        content = self.adapter.extract_content(
            _payload(1, "Arrival", '"Hello," Subaru said.\n\n*Thought.*')
        )

        self.assertEqual(content, '* * *\n\n"Hello," Subaru said.\n\n*Thought.*')
        self.assertNotIn("URL Source", content)
        self.assertNotIn("Chapter 1: Arrival", content)

    def test_missing_chapter_fails_closed(self) -> None:
        payload = b"Markdown Content:\nFanFiction.Net Message Type 1\nChapter not found."

        with self.assertRaisesRegex(ValueError, "does not exist"):
            self.adapter.extract_content(payload)


if __name__ == "__main__":
    unittest.main()
