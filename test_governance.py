"""Governance must fail on stale/oversized inputs, not merely document intentions."""

import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts import workspace_health as health
from novel_pipeline.config import load_app_config


ROOT = Path(__file__).resolve().parent


class GovernanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "00_Config").mkdir()
        (self.root / "proof.md").write_text("Inspected evidence\n", encoding="utf-8")
        self.ledger = {"definition": "reader incidents per 10 first publications", "history_complete": False,
                       "publication_cohorts": [], "incidents": []}

    def save(self):
        (self.root / "00_Config/quality_incidents.json").write_text(json.dumps(self.ledger), encoding="utf-8")

    def cohort(self, *, kind="historical-reader-snapshot", name="release", scope="ch001-ch010"):
        item = {"id": name, "kind": kind, "novel": "fixture", "chapters": [scope], "evidence": "proof.md"}
        if kind == "verified-publication":
            item.update(verified_at="2026-11-15T00:00:00Z", revision="revision-hash", live_url="https://example.org/verified")
        self.ledger["publication_cohorts"].append(item)
        return item

    def incident(self, *, name="incident", detector="reader", cohort="release", scope="ch001-ch003"):
        item = {"id": name, "novel": "fixture", "chapters": [scope], "publication_cohort": cohort,
                "discovered_on": "2026-11-15", "detected_by": detector, "evidence": "proof.md"}
        self.ledger["incidents"].append(item)
        return item

    def test_empty_history_has_no_invented_zero_rate(self):
        self.save()
        result = health.quality_metrics(self.root)
        self.assertIsNone(result["defect_escape_rate_per_10"])
        self.assertIsNone(result["known_published_cohort_incidence_per_10"])

    def test_partial_historical_ratio_is_not_prospective_escape_rate(self):
        self.cohort()
        self.incident()
        self.save()
        result = health.quality_metrics(self.root)
        self.assertEqual(result["known_reader_incidents"], 1)
        self.assertEqual(result["retrospective_snapshot_ratio_lower_bound_per_10"], 1)
        self.assertEqual(result["distinct_first_published_chapters"], 0)
        self.assertIsNone(result["defect_escape_rate_per_10"])

    def test_same_publication_or_regeneration_does_not_inflate_denominator(self):
        self.cohort(kind="verified-publication")
        self.cohort(kind="verified-publication", name="rerender")
        self.incident()
        self.incident(name="caught-before-release", detector="gate")
        self.ledger["history_complete"] = True
        self.save()
        result = health.quality_metrics(self.root)
        self.assertEqual(result["distinct_first_published_chapters"], 10)
        self.assertEqual(result["defect_escape_rate_per_10"], 1)

    def test_future_verified_cohorts_can_be_measured_despite_partial_legacy_history(self):
        self.cohort(kind="verified-publication")
        self.incident()
        self.save()
        result = health.quality_metrics(self.root)
        self.assertFalse(result["history_complete"])
        self.assertEqual(result["defect_escape_rate_per_10"], 1)
        self.assertIn("historical snapshots excluded", result["rate_scope"])

    def test_duplicate_incident_cannot_be_counted_twice(self):
        self.cohort()
        self.incident()
        self.incident()
        self.save()
        with self.assertRaisesRegex(ValueError, "duplicate incident"):
            health.quality_metrics(self.root)

    def test_incident_must_belong_to_a_published_cohort(self):
        self.cohort()
        self.incident(scope="ch011")
        self.save()
        with self.assertRaisesRegex(ValueError, "outside publication cohort"):
            health.quality_metrics(self.root)

    def test_generation_is_not_verified_publication(self):
        cohort = self.cohort(kind="verified-publication")
        del cohort["live_url"]
        self.save()
        with self.assertRaisesRegex(ValueError, "live URL"):
            health.quality_metrics(self.root)

    def test_unknown_legacy_discovery_date_is_explicit_and_new_incidents_need_a_date(self):
        cohort = self.cohort()
        incident = self.incident()
        incident.update(discovered_on=None, discovery_date_status="historical-unknown")
        self.save()
        self.assertEqual(health.quality_metrics(self.root)["known_reader_incidents"], 1)
        cohort.update(kind="verified-publication", verified_at="2026-11-15T00:00:00Z", revision="revision", live_url="https://example.org/verified")
        self.save()
        with self.assertRaisesRegex(ValueError, "discovery date"):
            health.quality_metrics(self.root)

    def test_evidence_pointer_must_resolve(self):
        self.cohort()["evidence"] = "missing.md"
        self.save()
        with self.assertRaisesRegex(ValueError, "evidence missing"):
            health.quality_metrics(self.root)

    def test_document_budget_detects_both_line_and_character_bloat(self):
        for name in health.DOC_BUDGETS:
            (self.root / name).write_text("# Compact\n", encoding="utf-8")
        (self.root / "00_Config/novel_registry.json").write_text('{"novels": []}', encoding="utf-8")
        self.save()
        self.assertTrue(health.check(self.root)["passed"])
        for content in ("checkpoint\n" * 71, "x" * 5001):
            (self.root / "PROJECT_BRAIN.md").write_text(content, encoding="utf-8")
            result = health.check(self.root)
            self.assertFalse(result["passed"])
            self.assertIn("PROJECT_BRAIN.md: exceeds budget", " ".join(result["errors"]))

    def test_local_files_do_not_expand_public_target_and_absence_is_unknown(self):
        novel = {"slug": "fixture", "folder": "Novel", "reader": {"enabled": True, "last_chapter": 1}}
        first = health.reader_state(self.root, novel)
        self.assertIsNone(first["local_output_count"])
        output = self.root / "Novel/05_Output/ch002"
        output.mkdir(parents=True)
        (output / "ch002.md").write_text("local only", encoding="utf-8")
        second = health.reader_state(self.root, novel)
        self.assertEqual(second["reader_target_count"], 1)
        self.assertEqual(second["local_only_ids"], ["ch002"])
        self.assertEqual(second["live_publication"], "not-probed")

    def test_reader_snapshot_cannot_claim_a_nonexistent_chapter(self):
        novel = {"slug": "fixture", "folder": "Novel", "reader": {"enabled": True, "last_chapter": 1}}
        directory = self.root / "MoonRead/content/generated/books/fixture"
        directory.mkdir(parents=True)
        (directory / "manifest.json").write_text('{"chapters": [{"id":"ch001","status":"available"}]}', encoding="utf-8")
        self.assertIn("reader file missing", " ".join(health.reader_state(self.root, novel)["errors"]))

    def test_report_index_folds_reruns_without_deleting_or_overwriting(self):
        directory = self.root / "07_Reports/generated/2026-11"
        directory.mkdir(parents=True)
        for stamp in ("20261114_000000", "20261115_000000_123456"):
            for ext in ("md", "json"):
                (directory / f"sentinel_quality_test_{stamp}.{ext}").write_text("evidence", encoding="utf-8")
        (self.root / "07_Reports/sentinel_quality_test_20261113_000000.md").write_text("old flat report", encoding="utf-8")
        result = health.report_index(self.root, "QUALITY_TEST")
        self.assertEqual(result["matching_files"], 5)
        self.assertEqual(result["scope_count"], 1)
        self.assertEqual(len(result["scopes"][0]["latest"]), 2)
        self.assertEqual(result["scopes"][0]["older_files"], 3)
        self.assertEqual(len(list(directory.iterdir())), 4)

    def test_before_compaction_archives_are_byte_preserved(self):
        archive = ROOT / "Backup_/governance/2026-11-15"
        manifest = health.load(archive / "manifest.json")
        for name, sha in manifest["sha256"].items():
            self.assertEqual(hashlib.sha256((archive / name).read_bytes()).hexdigest(), sha)

    def test_real_checkout_passes_governance_check(self):
        result = health.check(ROOT)
        self.assertTrue(result["passed"], result["errors"])

    def test_new_novels_have_their_own_voice_and_truthful_pending_state(self):
        for folder, slug, style, other_terms in (
            ("Investing in My Crippled Wife", "investing-in-my-crippled-wife", "investment_fantasy", ("Earth's System",)),
            ("Im a Young God Wont You Raise Me", "im-a-young-god-wont-you-raise-me", "young_god", ("Soren", "Ethea", "Ice Empress")),
        ):
            with self.subTest(novel=slug):
                config = load_app_config(ROOT / folder / ".system/config.yaml")
                self.assertEqual(config.novel_id, slug)
                self.assertEqual(config.source_language, "en")
                self.assertIn(style, config.style_profiles)
                voice = (config.workspace.system / "lean_voice.md").read_text(encoding="utf-8")
                for foreign_term in ("Duncan", "Gaon", *other_terms):
                    self.assertNotIn(foreign_term, voice)
                if config.research_profile.status == "pending":
                    self.assertFalse(config.research_readiness_summary()["bounded_translation_ready"])
                    registry = health.load(ROOT / "00_Config/novel_registry.json")
                    entry = next(n for n in registry["novels"] if n["slug"] == config.novel_id)
                    self.assertFalse(entry["reader"]["enabled"])

    def test_english_relay_listing_account_is_not_mislabeled_as_original_author(self):
        import yaml
        profile = yaml.safe_load((ROOT / "Im a Young God Wont You Raise Me/NOVEL_PROFILE.yaml").read_text(encoding="utf-8"))
        self.assertTrue(profile["input_is_english_relay"])
        self.assertEqual(profile["english_listing_account"], "Rein_lout")
        self.assertEqual(profile["original_author_attribution"]["status"], "secondary-catalog-attribution-not-primary-verified")


if __name__ == "__main__":
    unittest.main()
