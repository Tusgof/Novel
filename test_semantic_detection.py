"""Mutation checks of the real staged Sentinel, including the reader escape cases."""

import json
from pathlib import Path
import tempfile
import shutil
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from scripts import sentinel_quality_report as sentinel
from novel_pipeline import lean


class SemanticDetectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.novel = self.root / "Novel"
        self.glossary = self.novel / "01_Glossary"
        self.glossary.mkdir(parents=True)
        self.reader = self.root / "MoonRead"
        self.registry = {"novels": [{"slug": "deep-sea-embers", "folder": "Novel", "raw_dir": "03_Raw", "output_dir": "05_Output"}]}
        self.registry_path = self.root / "registry.json"
        self.addCleanup(patch.stopall)
        patch.multiple(sentinel, WORKSPACE_ROOT=self.root, MOONREAD_ROOT=self.reader,
                       REGISTRY_PATH=self.registry_path, REPORT_ROOT=self.root / "07_Reports/generated").start()
        patch.dict("os.environ", {"NOVEL_SENTINEL_WORKSPACE_ROOT": str(self.root),
                                  "NOVEL_SENTINEL_REGISTRY_PATH": str(self.registry_path),
                                  "NOVEL_SENTINEL_STAGE_ONLY": "1"}).start()

    def term(self, name, original, thai, rejected=""):
        (self.glossary / f"{name}.md").write_text(
            f"---\noriginal_term: {original}\nthai_term: {thai}\nstatus: approved\ncategory: title\n"
            + (f"rejected_variants:\n  - {rejected}\n" if rejected else "") + "---\n", encoding="utf-8")

    def output(self, chapter, body, source):
        raw = self.novel / "03_Raw" / chapter
        output = self.novel / "05_Output" / chapter
        raw.mkdir(parents=True, exist_ok=True)
        output.mkdir(parents=True, exist_ok=True)
        (raw / "source.json").write_text(json.dumps({"raw_text": source}), encoding="utf-8")
        (output / f"{chapter}.md").write_text(f"# บทที่ {int(chapter[2:])}: เรื่อง\n\n{body}\n", encoding="utf-8")

    def gate(self, chapter):
        self.registry_path.write_text(json.dumps(self.registry), encoding="utf-8")
        return sentinel.generate_sentinel_report(novel=self.registry["novels"][0]["slug"],
                                                chapters=chapter, scope="mutation", fail_on="major", skip_advisory_english=True)

    def test_chinese_required_term_detects_unknown_drift_without_a_denylist(self):
        self.term("审判官", "审判官", "ตุลาการ")
        self.output("ch140", "บุคคลที่เรียกผิดชื่อเดินมา", "审判官走进来。")
        result = self.gate("ch140")
        self.assertTrue(result["failed"])
        self.assertTrue(any(f.category == "glossary_coverage_missing" for f in result["findings"]))
        self.output("ch140", "ตุลาการเดินเข้ามา", "审判官走进来。")
        self.assertFalse(self.gate("ch140")["failed"])

    def test_dse_rejected_variant_cannot_hide_behind_one_correct_occurrence(self):
        self.term("审判官", "审判官", "ตุลาการ", "อินควิสิเตอร์")
        self.output("ch160", "ตุลาการเดินมา แล้วอินควิสิเตอร์ก็นั่งลง", "审判官走进来。")
        self.assertTrue(any(f.category == "glossary_rejected_variant" for f in self.gate("ch160")["findings"]))

    def test_hgd_149_glossary_escape_mutation_fails(self):
        self.registry["novels"][0]["slug"] = "horror-game-developer"
        self.output("ch149", "ทวิสเต็ดแมนยืนอยู่ข้างอโนมาลี", "Twisted Man stood near the Anomaly.")
        self.assertTrue(self.gate("ch149")["failed"])

    def test_hgd_203_and_206_escape_mutations_fail(self):
        self.registry["novels"][0]["slug"] = "horror-game-developer"
        for cid, bad in (("ch203", "กูจะทำเกมนี้"), ("ch206", "เขาเปิด A Twisted Game")):
            with self.subTest(chapter=cid):
                self.output(cid, bad, "Seth opened a game.")
                self.assertTrue(self.gate(cid)["failed"])

    def test_missing_source_is_not_reported_as_semantically_green(self):
        self.output("ch140", "ตุลาการเดินเข้ามา", "审判官走进来。")
        (self.novel / "03_Raw/ch140/source.json").unlink()
        result = self.gate("ch140")
        self.assertTrue(result["failed"])
        report = json.loads(result["json_path"].read_text(encoding="utf-8"))
        self.assertEqual(report["source_coverage"]["status"], "unverified")
        self.assertFalse(report["safe_to_publish"])

    def test_title_only_or_whitespace_source_does_not_count_as_semantic_input(self):
        self.output("ch140", "ตุลาการเดินเข้ามา", "审判官走进来。")
        raw = self.novel / "03_Raw/ch140/source.json"
        for payload in ({"title": "审判官"}, {"title": "审判官", "raw_text": "  \n "}, []):
            with self.subTest(payload=payload):
                raw.write_text(json.dumps(payload), encoding="utf-8")
                self.assertTrue(self.gate("ch140")["failed"])

    def test_partially_missing_product_scope_is_not_a_pass(self):
        self.output("ch140", "ตุลาการเดินเข้ามา", "审判官走进来。")
        self.assertTrue(self.gate("ch140-ch141")["failed"])

    def test_staged_gate_does_not_scan_an_old_reader_copy(self):
        self.term("审判官", "审判官", "ตุลาการ", "อินควิสิเตอร์")
        self.output("ch140", "ตุลาการเดินเข้ามา", "审判官走进来。")
        old = self.reader / "content/generated/books/deep-sea-embers/chapters"
        old.mkdir(parents=True)
        (old / "ch140.md").write_text("อินควิสิเตอร์", encoding="utf-8")
        self.assertFalse(self.gate("ch140")["failed"])

    def test_correct_non_source_term_does_not_require_an_unrelated_glossary_entry(self):
        self.term("other", "见习审判官", "ตุลาการฝึกหัด")
        self.output("ch140", "ชาวบ้านเดินเข้ามา", "一个人走进来。")
        self.assertFalse(self.gate("ch140")["failed"])

    def test_report_major_is_not_safe_and_reruns_preserve_evidence(self):
        finding = sentinel.Finding("major", "test", "fixture", "observed failure")
        first, _ = sentinel.write_reports([finding], scope="same", chapters="ch001", coverage={"status": "evaluated"})
        second, _ = sentinel.write_reports([], scope="same", chapters="ch001", coverage={"status": "evaluated"})
        self.assertNotEqual(first, second)
        self.assertTrue(first.is_file())
        self.assertFalse(json.loads(first.read_text(encoding="utf-8"))["safe_to_publish"])
        self.assertIn("generated", first.parts)

    def test_report_scope_cannot_escape_storage_directory(self):
        with self.assertRaises(ValueError):
            sentinel.write_reports([], scope="../outside", chapters=None)

    def test_real_lean_staging_hook_rejects_chinese_drift_without_touching_product(self):
        scripts = self.root / "scripts"
        scripts.mkdir()
        shared = Path(__file__).resolve().parent / "scripts"
        for name in ("sentinel_quality_report.py", "check_output_quality_guardrails.py"):
            shutil.copyfile(shared / name, scripts / name)
        config_root = self.root / "00_Config"
        config_root.mkdir()
        (config_root / "novel_registry.json").write_text(json.dumps(self.registry), encoding="utf-8")
        self.term("审判官", "审判官", "ตุลาการ")
        self.output("ch140", "ตุลาการเดิมที่ต้องคงไว้", "审判官走进来。")
        final = self.novel / "05_Output/ch140/ch140.md"
        before = final.read_bytes()
        staged = self.novel / "04_Work/_lean_runs/probe/_staged_output"
        path = staged / "ch140/ch140.md"
        path.parent.mkdir(parents=True)
        path.write_text("# บทที่ 140: เรื่อง\n\nชื่อที่ผิด\n", encoding="utf-8")
        config = SimpleNamespace(novel_id="deep-sea-embers", workspace=SimpleNamespace(root=self.novel))
        result = lean._run_production_sentinel(config, run_id="probe", chapters="ch140", staged_output_root=staged)
        self.assertTrue(result["failed"])
        self.assertIn("generated", Path(result["json_path"]).parts)
        self.assertEqual(final.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
