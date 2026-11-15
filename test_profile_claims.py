import json
import tempfile
import unittest
from pathlib import Path

import yaml

from novel_pipeline.preflight import _profile_claims


def _write_source(root: Path, chapter_id: str, text: str) -> None:
    directory = root / "03_Raw" / chapter_id
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "source.json").write_text(
        json.dumps({"chapter_id": chapter_id, "raw_text": text}), encoding="utf-8"
    )


def _write_profile(root: Path, synopsis: str, terminology: list[str]) -> None:
    (root / "RESEARCH_PROFILE.yaml").write_text(
        yaml.safe_dump({"synopsis": synopsis, "terminology": terminology}), encoding="utf-8"
    )


class ProfileClaimTests(unittest.TestCase):
    def test_names_supported_by_source_are_consistent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for chapter in ("ch001", "ch002", "ch003"):
                _write_source(root, chapter, "Cedric Montraven walked into the hall.")
            _write_profile(root, "Cedric Montraven loses everything.", ["Cedric Montraven"])
            warnings: list[str] = []
            result = _profile_claims(root, warnings)
            self.assertTrue(result["checked"])
            self.assertEqual(result["unsupported_names"], [])
            self.assertEqual(len(result["coverage_chapters"]), 3)
            self.assertTrue(result["consistent"])
            self.assertEqual(warnings, [])

    def test_invented_name_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for chapter in ("ch001", "ch002", "ch003"):
                _write_source(root, chapter, "Cedric Montraven walked into the hall.")
            _write_profile(root, "Cedric Montraven meets Guildmaster Thane.", ["Guildmaster Thane"])
            warnings: list[str] = []
            result = _profile_claims(root, warnings)
            self.assertFalse(result["consistent"])
            self.assertEqual(result["unsupported_names"], ["Guildmaster Thane"])
            self.assertEqual(len(warnings), 1)
            self.assertIn("no occurrence in 03_Raw", warnings[0])

    def test_synopsis_names_are_checked_even_when_not_declared(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            _write_source(root, "ch001", "Nothing relevant here.")
            _write_profile(root, "The story follows Hollow Court politics.", [])
            warnings: list[str] = []
            result = _profile_claims(root, warnings)
            self.assertEqual(result["unsupported_names"], ["Hollow Court"])

    def test_single_chapter_coverage_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            _write_source(root, "ch001", "Cedric Montraven walked into the hall.")
            _write_profile(root, "Cedric Montraven loses everything.", ["Cedric Montraven"])
            warnings: list[str] = []
            result = _profile_claims(root, warnings)
            self.assertEqual(len(result["coverage_chapters"]), 1)
            self.assertFalse(result["consistent"])
            self.assertIn("needs a spread of chapters", warnings[0])

    def test_missing_source_is_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            _write_profile(root, "Cedric Montraven loses everything.", ["Cedric Montraven"])
            warnings: list[str] = []
            result = _profile_claims(root, warnings)
            self.assertFalse(result["checked"])
            self.assertEqual(warnings, [])

    def test_missing_profile_is_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            _write_source(root, "ch001", "Cedric Montraven walked into the hall.")
            warnings: list[str] = []
            result = _profile_claims(root, warnings)
            self.assertFalse(result["checked"])
            self.assertEqual(warnings, [])


if __name__ == "__main__":
    unittest.main()
