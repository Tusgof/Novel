import tempfile
import unittest
from pathlib import Path

import yaml

from novel_pipeline.preflight import _source_readiness


def _write_profile(root: Path, state: str | None) -> None:
    payload: dict = {"novel_id": "fixture", "source": {"adapter": ""}}
    if state is not None:
        payload["setup"] = {"source_state": state}
    (root / "NOVEL_PROFILE.yaml").write_text(yaml.safe_dump(payload), encoding="utf-8")


def _write_source(root: Path, chapter_id: str) -> None:
    directory = root / "03_Raw" / chapter_id
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "source.json").write_text("{}", encoding="utf-8")


class SourceStateReadinessTests(unittest.TestCase):
    def test_pending_without_source_is_consistent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            _write_profile(root, "pending")
            warnings: list[str] = []
            result = _source_readiness(root, warnings)
            self.assertTrue(result["state_consistent"])
            self.assertEqual(result["imported_chapters"], 0)
            self.assertEqual(warnings, [])

    def test_pending_with_imported_source_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            _write_profile(root, "pending")
            _write_source(root, "ch001")
            warnings: list[str] = []
            result = _source_readiness(root, warnings)
            self.assertFalse(result["state_consistent"])
            self.assertEqual(result["imported_chapters"], 1)
            self.assertEqual(len(warnings), 1)
            self.assertIn("declares setup.source_state: pending", warnings[0])

    def test_fetched_without_source_is_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            _write_profile(root, "fetched")
            warnings: list[str] = []
            result = _source_readiness(root, warnings)
            self.assertFalse(result["state_consistent"])
            self.assertIn("no chapter source.json", warnings[0])

    def test_fetched_with_source_is_consistent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            _write_profile(root, "validated")
            _write_source(root, "ch001")
            _write_source(root, "ch002")
            warnings: list[str] = []
            result = _source_readiness(root, warnings)
            self.assertTrue(result["state_consistent"])
            self.assertEqual(result["imported_chapters"], 2)
            self.assertEqual(warnings, [])

    def test_legacy_vault_without_state_is_not_checked(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            _write_profile(root, None)
            _write_source(root, "ch001")
            warnings: list[str] = []
            result = _source_readiness(root, warnings)
            self.assertEqual(result["declared_state"], "unset")
            self.assertTrue(result["state_consistent"])
            self.assertEqual(warnings, [])

    def test_missing_profile_is_not_checked(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            warnings: list[str] = []
            result = _source_readiness(Path(temporary), warnings)
            self.assertEqual(result["declared_state"], "unset")
            self.assertEqual(warnings, [])


if __name__ == "__main__":
    unittest.main()
