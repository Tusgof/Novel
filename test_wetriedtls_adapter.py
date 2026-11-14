import unittest

from novel_pipeline.adapters.wetriedtls import WetriedtlsAdapter
from novel_pipeline.stages.fetch import _derive_title_from_body_if_generic
from novel_pipeline.types import SourceConfig


def _paragraphs(*items: str) -> str:
    return "".join(f"<p>{item}</p>" for item in items)


class WetriedtlsAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.adapter = WetriedtlsAdapter(SourceConfig(
            adapter="wetriedtls",
            toc_url="https://example.test/series/demo",
            delay_seconds=0,
            encoding="utf-8",
        ))

    def test_bare_chapter_marker_is_still_supported(self) -> None:
        story = "The wastrel woke up." * 40
        raw = (
            _paragraphs("Site navigation", "Chapter 1")
            + _paragraphs(story)
            + _paragraphs("All rights deserved. website coded by heaning.")
        ).encode("utf-8")
        self.assertEqual(self.adapter.extract_content(raw), "Chapter 1\n" + story)

    def test_chapter_marker_with_inline_title_is_supported(self) -> None:
        story = "The wastrel woke up." * 40
        raw = (
            _paragraphs("Site navigation", "Chapter 12: The Wastrel's Reward")
            + _paragraphs(story)
            + _paragraphs("Join our discord at https://example.test/discord")
        ).encode("utf-8")
        self.assertEqual(
            self.adapter.extract_content(raw),
            "Chapter 12: The Wastrel's Reward\n" + story,
        )

    def test_missing_chapter_marker_fails_closed(self) -> None:
        raw = _paragraphs("Only a navigation shell.", "Still no heading.").encode("utf-8")
        with self.assertRaises(ValueError):
            self.adapter.extract_content(raw)

    def test_short_body_fails_closed(self) -> None:
        raw = _paragraphs("Chapter 1", "Too short.").encode("utf-8")
        with self.assertRaises(ValueError):
            self.adapter.extract_content(raw)


class FetchTitleDerivationTests(unittest.TestCase):
    """A generic manifest title must not discard a real inline chapter title."""

    def test_inline_chapter_title_replaces_generic_title(self) -> None:
        body = "Chapter 12: The Wastrel's Reward\nFirst body paragraph.\nSecond one."
        self.assertEqual(
            _derive_title_from_body_if_generic("Chapter 12", body),
            "Chapter 12: The Wastrel's Reward",
        )

    def test_heading_without_subtitle_keeps_generic_title(self) -> None:
        body = "Chapter 12\nFirst body paragraph.\nSecond one."
        self.assertEqual(_derive_title_from_body_if_generic("Chapter 12", body), "Chapter 12")

    def test_neighbouring_chapter_number_is_not_used(self) -> None:
        body = "Chapter 120: Someone Else\nFirst body paragraph.\nSecond one."
        self.assertEqual(_derive_title_from_body_if_generic("Chapter 12", body), "Chapter 12")

    def test_real_manifest_title_is_left_alone(self) -> None:
        body = "Chapter 12: The Wastrel's Reward\nFirst body paragraph."
        self.assertEqual(
            _derive_title_from_body_if_generic("The Wastrel's Reward", body),
            "The Wastrel's Reward",
        )

    def test_separator_form_still_works(self) -> None:
        body = "Chapter 12\n-------\nThe Wastrel's Reward\nFirst body paragraph."
        self.assertEqual(
            _derive_title_from_body_if_generic("Chapter 12", body),
            "Chapter 12 - The Wastrel's Reward",
        )


if __name__ == "__main__":
    unittest.main()
