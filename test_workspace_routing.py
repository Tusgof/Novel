from __future__ import annotations

import unittest
import tempfile
import contextlib
import io
import json
import os
import shutil
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from novel_pipeline.config import ConfigError, _resolve_provider_command, load_app_config
from novel_pipeline import lean
from novel_pipeline import cli
from novel_pipeline.types import ProviderResponse, TextBlock, WorkspacePaths
from novel_pipeline.project_setup import initialize_novel_project
from novel_pipeline.stages.refine import _clean_refined_output


ROOT = Path(__file__).resolve().parent


class WorkspaceRoutingTests(unittest.TestCase):
    CONFIGS = (
        "Deep Sea Embers/.system/config.yaml",
        "Horror Game Developers/.system/config.yaml",
        "Infinite Regressor Stories/.system/config.yaml",
        "One Hit Kill Swordmaster/.system/config.yaml",
        "Re Zero Watching Him Die Again and Again/.system/config.yaml",
    )

    def test_refinement_cleaner_preserves_story_lists_and_scene_tail(self) -> None:
        story = "ก่อนฉาก\n\n- นิรนาม: ใครส่งข้อความมา?\n* ผู้ดูแล: ยินดีต้อนรับ\n\n---\n\nหลังฉาก"
        self.assertEqual(_clean_refined_output(story), story)
        self.assertEqual(_clean_refined_output(story + "\n**Craft notes\n- provider note"), story)

    def test_lean_repair_removes_cjk_source_annotations_before_qa(self) -> None:
        draft = lean.RefinedDraft(
            block_id="ch013-assembled",
            chapter_id="ch013",
            refined_text="ตัวอักษร 'โย่ว (右 - ขวา)' และ 'ขีดปัดซ้าย (撇)'",
            provider="fixture",
            style_profile="dark_fantasy",
            source_text="source",
        )
        repaired = lean._repair_refined_source_annotations(draft)
        self.assertNotRegex(repaired.refined_text, r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
        self.assertIn("ตัวอักษร 'โย่ว'", repaired.refined_text)
        self.assertEqual(repaired.metadata["source_script_annotation_repairs"], [{"type": "paren_cjk", "count": "2"}])

    def test_tdu_repair_normalizes_observed_names_and_typos(self) -> None:
        draft = lean.RefinedDraft(
            block_id="ch017-assembled",
            chapter_id="ch017",
            refined_text=(
                "\u0e09\u0e35\u0e0b\u0e35\u0e48\u0e22 \u0e2e\u0e27\u0e32\u0e2d\u0e35\u0e42\u0e21\u0e48 "
                "\u0e1e\u0e27\u0e01\u0e40\u0e02\u0e48\u0e32 \u0e1e\u0e27\u0e01\u0e40\u0e23\u0e08\u0e30 \u0e04\u0e48\u0e2d\u0e19\u0e01 "
                "\u0e40\u0e18\u0e08\u0e30 \u0e40\u0e02\u0e49\u0e32\u0e23\u0e39\u0e49\u0e14\u0e35\u0e27\u0e48\u0e32 "
                "\u0e09\u0e35\u0e40\u0e0b\u0e35\u0e48\u0e22\u0e35\u0e48\u0e15\u0e32\u0e25\u0e07 \u0e09\u0e35\u0e40\u0e0b\u0e35\u0e48\u0e22\u0e37\u0e19\u0e2d\u0e22\u0e39\u0e48"
            ),
            provider="fixture",
            style_profile="dark_fantasy",
            source_text="source",
        )
        repaired = lean._repair_refined_source_annotations(draft, novel_id="ten-day-ultimatum")
        self.assertIn("\u0e09\u0e35\u0e40\u0e0b\u0e35\u0e48\u0e22", repaired.refined_text)
        self.assertIn("\u0e2b\u0e32\u0e19\u0e2d\u0e35\u0e42\u0e21\u0e48", repaired.refined_text)
        self.assertIn("\u0e1e\u0e27\u0e01\u0e40\u0e02\u0e32", repaired.refined_text)
        self.assertIn("\u0e1e\u0e27\u0e01\u0e40\u0e23\u0e32\u0e08\u0e30", repaired.refined_text)
        self.assertIn("\u0e04\u0e48\u0e2d\u0e19\u0e02\u0e49\u0e32\u0e07", repaired.refined_text)
        self.assertIn("\u0e40\u0e18\u0e2d\u0e08\u0e30", repaired.refined_text)
        self.assertIn("\u0e40\u0e02\u0e32\u0e23\u0e39\u0e49\u0e14\u0e35\u0e27\u0e48\u0e32", repaired.refined_text)
        self.assertIn("\u0e09\u0e35\u0e40\u0e0b\u0e35\u0e48\u0e22\u0e2b\u0e23\u0e35\u0e48\u0e15\u0e32\u0e25\u0e07", repaired.refined_text)
        self.assertIn("\u0e09\u0e35\u0e40\u0e0b\u0e35\u0e48\u0e22\u0e22\u0e37\u0e19\u0e2d\u0e22\u0e39\u0e48", repaired.refined_text)
        self.assertTrue(repaired.metadata["tdu_repairs"])

    def test_each_registered_novel_uses_lean_and_its_own_context(self) -> None:
        for relative_config in self.CONFIGS:
            config = load_app_config(ROOT / relative_config)
            self.assertEqual(config.raw_config.get("pipeline_engine"), "lean")
            self.assertEqual(config.workspace.root.name, relative_config.split("/")[0])
            for spec in config.providers.values():
                self.assertEqual(spec.working_dir, config.workspace.root.resolve())
                for token in spec.executable:
                    if token.lower().endswith(".py"):
                        self.assertTrue(Path(token).exists(), token)
                        self.assertNotIn("Deep Sea Embers", str(Path(token))) if config.novel_id != "deep-sea-embers" else None

    def test_sibling_provider_helper_is_rejected(self) -> None:
        with self.assertRaises(ConfigError):
            _resolve_provider_command(
                ("python", r"..\Deep Sea Embers\scripts\openrouter_provider_shim.py"),
                novel_root=ROOT / "One Hit Kill Swordmaster",
                workspace_root=ROOT,
            )

        with self.assertRaises(ConfigError):
            _resolve_provider_command(
                (r"D:\\Fogust\\Workspace\\Novel\\Deep Sea Embers\\scripts\\openrouter_provider_shim.py",),
                novel_root=ROOT / "One Hit Kill Swordmaster",
                workspace_root=ROOT,
            )

    def test_shared_provider_helper_resolves_at_workspace_root(self) -> None:
        command = _resolve_provider_command(
            ("python", r"..\scripts\openrouter_provider_shim.py"),
            novel_root=ROOT / "One Hit Kill Swordmaster",
            workspace_root=ROOT,
        )
        self.assertEqual(Path(command[1]), ROOT / "scripts" / "openrouter_provider_shim.py")

    def test_workspace_cli_rejects_legacy_engine(self) -> None:
        config = SimpleNamespace(raw_config={"pipeline_engine": "legacy"}, novel_id="fixture")
        with patch.object(cli, "load_app_config", return_value=config), patch.dict(
            cli.COMMAND_HANDLERS, {"run": lambda *args: self.fail("legacy dispatch must not run")}
        ), patch.object(sys, "argv", ["novel-pipeline", "--config", "fixture.yaml", "run"]), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(cli.main(), 1)

    def test_production_rejects_paths_outside_selected_novel_before_provider_calls(self) -> None:
        config = load_app_config(ROOT / self.CONFIGS[3])
        for options in (
            ["--run-id", "../escape"],
            ["--run-id", "fixture", "--checkpoint-dir", str(ROOT / "Deep Sea Embers/04_Work")],
            ["--run-id", "fixture", "--output-dir", str(config.workspace.output)],
        ):
            with self.subTest(options=options), patch.object(lean, "run_chapter") as provider_work:
                with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                    lean.main(["--config", str(config.config_path), "--chapters", "ch001", *options])
                provider_work.assert_not_called()

    def test_new_novel_setup_selects_lean_without_inheriting_voice(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            template = load_app_config(ROOT / self.CONFIGS[0])
            result = initialize_novel_project(
                template_config=template, project_root=Path(temporary) / "New Novel",
                title="New Novel", source_url="https://example.com/toc", genre="comedy",
            )
            import yaml
            generated = yaml.safe_load(result["config_path"].read_text(encoding="utf-8"))
            self.assertEqual(generated["pipeline_engine"], "lean")
            voice = (result["config_path"].parent / "lean_voice.md").read_text(encoding="utf-8")
            self.assertIn("comedy", voice)
            self.assertNotIn("Duncan", voice)

    def test_real_lean_stages_use_shared_prompts_and_local_formatter(self) -> None:
        # Only the provider transport is mocked; prompt rendering and stages run.
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = load_app_config(ROOT / self.CONFIGS[3])
            config.workspace = WorkspacePaths.from_root(root)
            config.workspace.system.mkdir(parents=True)
            shutil.copyfile(ROOT / "One Hit Kill Swordmaster/.system/lean_voice.md", config.workspace.system / "lean_voice.md")
            config.workspace.glossary_dir.mkdir()
            source_dir = config.workspace.raw / "ch001"
            source_dir.mkdir(parents=True)
            source_text = "A swordsman returned home.\n\nHe opened the door."
            (source_dir / "source.json").write_text(json.dumps({
                "novel_id": config.novel_id, "chapter_id": "ch001", "title": "",
                "source_language": "en", "raw_text": source_text,
            }), encoding="utf-8")
            title_dir = config.workspace.work / "ch001"
            title_dir.mkdir(parents=True)
            (title_dir / "title.json").write_text(json.dumps({"thai_title": "บทที่ 1"}), encoding="utf-8")
            thai = "\u0e19\u0e31\u0e01\u0e14\u0e32\u0e1a\u0e01\u0e25\u0e31\u0e1a\u0e1a\u0e49\u0e32\u0e19\n\n\u0e40\u0e02\u0e32\u0e40\u0e1b\u0e34\u0e14\u0e1b\u0e23\u0e30\u0e15\u0e39"
            requests = []

            def fake_transport(_runner, request, **kwargs):
                requests.append(request)
                self.assertNotIn("{{", request.prompt)
                text = {"literal_translation": thai, "refinement": thai, "qa_judge": "PASS: Complete.", "term_harvest": "[]"}[request.stage]
                return ProviderResponse(provider=request.provider, command=("mock",), stdout=text, model=request.model, stage=request.stage)

            staged = config.workspace.work / "_lean_runs/fixture/_staged_output"
            checkpoints = staged.parent
            with patch.object(lean.ProviderRunner, "run_with_retry", new=fake_transport), patch.dict(os.environ, {}, clear=False):
                result = lean.run_chapter(config, "ch001", "fixture", staged, checkpoints / "trace", checkpoint_root=checkpoints)
                self.assertTrue(result["qa_passed"])
                self.assertEqual(result["formatter_provider"], "local")
                self.assertEqual([item.stage for item in requests], ["literal_translation", "refinement", "qa_judge", "term_harvest"])
                self.assertIn(source_text, requests[2].prompt)
                self.assertFalse(config.workspace.output.exists())
                resumed = lean.run_chapter(config, "ch001", "fixture", staged, checkpoints / "trace", checkpoint_root=checkpoints, resume=True)
                self.assertEqual(len(requests), 4)
                self.assertEqual(len(resumed["reused_stages"]), 5)

    def test_staged_sentinel_ignores_old_product_and_other_novels(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "scripts").mkdir()
            for name in ("sentinel_quality_report.py", "check_output_quality_guardrails.py"):
                shutil.copyfile(ROOT / "scripts" / name, root / "scripts" / name)
            (root / "00_Config").mkdir()
            novels = [{"slug": slug, "folder": folder} for slug, folder in (("fixture", "Selected"), ("other", "Other"))]
            (root / "00_Config/novel_registry.json").write_text(json.dumps({"novels": novels}), encoding="utf-8")
            staged = root / "Selected/04_Work/_lean_runs/test/_staged_output"
            paths = (staged / "ch001/ch001.md", root / "Selected/05_Output/ch001/ch001.md", root / "Other/05_Output/ch001/ch001.md", root / "MoonRead/content/generated/books/fixture/chapters/ch001.md")
            for path in paths:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("# Title\n\n\u0e21\u0e35\u0e40\u0e25\u0e02 \u0e51\n", encoding="utf-8")
            paths[0].write_text("# Title\n\n\u0e40\u0e19\u0e37\u0e49\u0e2d\u0e40\u0e23\u0e37\u0e48\u0e2d\u0e07\n", encoding="utf-8")
            config = SimpleNamespace(novel_id="fixture", workspace=SimpleNamespace(root=root / "Selected"))
            with patch.dict(os.environ, {"NOVEL_SENTINEL_SKIP_EXISTING_GUARDRAILS": "1"}):
                result = lean._run_production_sentinel(config, run_id="test", chapters="ch001", staged_output_root=staged)
                self.assertFalse(result["failed"], result)
                first_report = Path(result["json_path"])
                self.assertIn("lean-test-ch001_", first_report.name)
                second_chapter = staged / "ch002/ch002.md"
                second_chapter.parent.mkdir(parents=True)
                second_chapter.write_text(paths[0].read_text(encoding="utf-8"), encoding="utf-8")
                second_result = lean._run_production_sentinel(config, run_id="test", chapters="ch002", staged_output_root=staged)
                self.assertNotEqual(first_report, Path(second_result["json_path"]))
                self.assertEqual(json.loads(first_report.read_text(encoding="utf-8"))["chapters"], "ch001")
                paths[0].write_text("# Title\n\n\u0e21\u0e35\u0e40\u0e25\u0e02 \u0e51\n", encoding="utf-8")
                result = lean._run_production_sentinel(config, run_id="test", chapters="ch001", staged_output_root=staged)
                self.assertTrue(result["failed"], result)
                self.assertEqual(os.environ["NOVEL_SENTINEL_SKIP_EXISTING_GUARDRAILS"], "1")

    def test_literal_and_harvest_use_configured_fallback_routes(self) -> None:
        config = load_app_config(ROOT / self.CONFIGS[3])
        fallback = (config.providers["openrouter"], "fixture-fallback")
        requests = []

        def fake_transport(_runner, request, **kwargs):
            requests.append(request)
            is_fallback = request.model == "fixture-fallback"
            if request.stage == "literal_translation":
                text = "\u0e40\u0e02\u0e32\u0e01\u0e25\u0e31\u0e1a\u0e1a\u0e49\u0e32\u0e19" if is_fallback else ""
            else:
                text = "[]" if is_fallback else "{}"
            return ProviderResponse(provider=request.provider, command=("mock",), stdout=text, model=request.model)

        with patch.object(type(config), "fallback_routes_for_stage", return_value=[fallback]), patch.object(
            lean.ProviderRunner, "run_with_retry", new=fake_transport
        ), patch.dict(os.environ, {}, clear=False):
            block = TextBlock(block_id="ch001-block-001", chapter_id="ch001", block_index=1, source_text="He went home.", source_language="en")
            draft = lean._run_literal_with_configured_fallbacks(config, block)
            self.assertEqual(draft.metadata["literal_route_index"], 1)
            self.assertEqual(lean._harvest_candidates(
                config=config, chapter_id="ch001", source_text=block.source_text,
                final_text=draft.sentence_pairs[0].literal_sentence, run_id="fixture", trace_dir=ROOT,
            ), [])
        self.assertEqual([request.model for request in requests][1::2], ["fixture-fallback", "fixture-fallback"])

    def test_partial_promotion_is_reported_when_later_disk_write_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            workspace = SimpleNamespace(root=root, work=root / "04_Work", output=root / "05_Output", glossary_dir=root / "01_Glossary")
            config = SimpleNamespace(novel_id="fixture", workspace=workspace)
            workspace.glossary_dir.mkdir()
            for chapter in ("ch001", "ch002"):
                existing = workspace.output / chapter / f"{chapter}.md"
                existing.parent.mkdir(parents=True)
                existing.write_text("# Existing\n", encoding="utf-8")

            def fake_chapter(config, chapter_id, run_id, output_dir, trace_dir, **kwargs):
                path = output_dir / chapter_id / f"{chapter_id}.md"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("# Candidate\n", encoding="utf-8")
                return {"chapter_id": chapter_id, "staged_output": str(path)}

            real_replace = os.replace

            def replace_with_disk_failure(source, destination):
                if Path(destination) == workspace.output / "ch002/ch002.md":
                    raise OSError("simulated disk failure")
                return real_replace(source, destination)

            with patch.object(lean, "load_app_config", return_value=config), patch.object(
                lean, "run_chapter", side_effect=fake_chapter
            ), patch.object(lean, "_run_production_sentinel", return_value={"failed": False}), patch.object(
                lean.os, "replace", side_effect=replace_with_disk_failure
            ), contextlib.redirect_stdout(io.StringIO()), patch.dict(os.environ, {}, clear=False):
                self.assertEqual(lean.main(["--config", "fixture.yaml", "--chapters", "ch001-ch002", "--run-id", "disk-failure"]), 2)
            report = json.loads((workspace.work / "_lean_runs/disk-failure/lean_run_report.json").read_text(encoding="utf-8"))
            self.assertEqual(report["status"], "blocked")
            self.assertEqual(report["promoted_outputs"], [str(workspace.output / "ch001/ch001.md")])
            self.assertEqual((workspace.output / "ch002/ch002.md").read_text(encoding="utf-8"), "# Existing\n")

    def test_production_promotes_only_after_sentinel_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            workspace = SimpleNamespace(
                root=root,
                work=root / "04_Work",
                output=root / "05_Output",
                glossary_dir=root / "01_Glossary",
            )
            config = SimpleNamespace(novel_id="fixture", workspace=workspace)
            workspace.work.mkdir(parents=True)
            workspace.output.mkdir(parents=True)
            workspace.glossary_dir.mkdir()

            def fake_chapter(config, chapter_id, run_id, output_dir, trace_dir, **kwargs):
                path = output_dir / chapter_id
                path.mkdir(parents=True, exist_ok=True)
                output = path / f"{chapter_id}.md"
                output.write_text("# Candidate\n\nnew\n", encoding="utf-8")
                return {"chapter_id": chapter_id, "staged_output": str(output)}

            with patch.object(lean, "load_app_config", return_value=config), patch.object(
                lean, "run_chapter", side_effect=fake_chapter
            ), patch.object(
                lean,
                "_run_production_sentinel",
                return_value={"counts": {"blocker": 0, "major": 0}, "failed": False},
            ):
                self.assertEqual(
                    lean.main(
                        [
                            "--config",
                            "fixture.yaml",
                            "--chapters",
                            "ch001-ch001",
                            "--run-id",
                            "fixture-pass",
                        ]
                    ),
                    0,
                )
            self.assertEqual((workspace.output / "ch001/ch001.md").read_text(encoding="utf-8"), "# Candidate\n\nnew\n")

    def test_production_quarantines_sentinel_block_without_overwriting_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            workspace = SimpleNamespace(
                root=root,
                work=root / "04_Work",
                output=root / "05_Output",
                glossary_dir=root / "01_Glossary",
            )
            config = SimpleNamespace(novel_id="fixture", workspace=workspace)
            workspace.work.mkdir(parents=True)
            workspace.output.mkdir(parents=True)
            workspace.glossary_dir.mkdir()
            existing = workspace.output / "ch001/ch001.md"
            existing.parent.mkdir(parents=True)
            existing.write_text("# Existing\n\nkeep\n", encoding="utf-8")

            def fake_chapter(config, chapter_id, run_id, output_dir, trace_dir, **kwargs):
                path = output_dir / chapter_id
                path.mkdir(parents=True, exist_ok=True)
                output = path / f"{chapter_id}.md"
                output.write_text("# Unsafe candidate\n", encoding="utf-8")
                return {"chapter_id": chapter_id, "staged_output": str(output)}

            with patch.object(lean, "load_app_config", return_value=config), patch.object(
                lean, "run_chapter", side_effect=fake_chapter
            ), patch.object(
                lean,
                "_run_production_sentinel",
                return_value={"counts": {"blocker": 1, "major": 0}, "failed": True},
            ):
                self.assertEqual(
                    lean.main(
                        [
                            "--config",
                            "fixture.yaml",
                            "--chapters",
                            "ch001",
                            "--run-id",
                            "fixture-blocked",
                        ]
                    ),
                    0,
                )
            self.assertEqual(existing.read_text(encoding="utf-8"), "# Existing\n\nkeep\n")

    def test_production_continues_after_chapter_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            workspace = SimpleNamespace(
                root=root,
                work=root / "04_Work",
                output=root / "05_Output",
                glossary_dir=root / "01_Glossary",
            )
            config = SimpleNamespace(novel_id="fixture", workspace=workspace)
            workspace.work.mkdir(parents=True)
            workspace.glossary_dir.mkdir(parents=True)

            def fake_chapter(config, chapter_id, run_id, output_dir, trace_dir, **kwargs):
                if chapter_id == "ch001":
                    raise lean.ChapterQualityError("QA hard-fail: known chapter-local defect")
                path = output_dir / chapter_id
                path.mkdir(parents=True, exist_ok=True)
                output = path / f"{chapter_id}.md"
                output.write_text("# Candidate\n", encoding="utf-8")
                return {"chapter_id": chapter_id, "staged_output": str(output)}

            with patch.object(lean, "load_app_config", return_value=config), patch.object(
                lean, "run_chapter", side_effect=fake_chapter
            ), patch.object(
                lean,
                "_run_production_sentinel",
                return_value={"counts": {"blocker": 0, "major": 0}, "failed": False},
            ):
                self.assertEqual(
                    lean.main(
                        [
                            "--config",
                            "fixture.yaml",
                            "--chapters",
                            "ch001-ch002",
                            "--run-id",
                            "fixture-partial",
                        ]
                    ),
                    0,
                )
            report = json.loads((workspace.work / "_lean_runs/fixture-partial/lean_run_report.json").read_text(encoding="utf-8"))
            self.assertEqual(report["status"], "partial")
            self.assertEqual([item["chapter_id"] for item in report["quarantined_chapters"]], ["ch001"])
            self.assertEqual(report["promoted_outputs"], [str(workspace.output / "ch002/ch002.md")])
            self.assertTrue((workspace.output / "ch002/ch002.md").is_file())


if __name__ == "__main__":
    unittest.main()
