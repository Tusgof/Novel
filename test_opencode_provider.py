from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from novel_pipeline.config import load_app_config
from novel_pipeline.preflight import build_preflight_summary


ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("novel_go_shim", ROOT / "scripts/opencode_provider_shim.py")
shim = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shim)
HAIKU = "opencode-go/claude-haiku-5-5"
DEEPSEEK = "opencode-go/deepseek-v4.1-flash"


def response(text="ข้อความไทย", reason="stop"):
    return "\n".join(json.dumps(event, ensure_ascii=False) for event in [
        {"type": "step_start", "part": {}},
        {"type": "reasoning", "part": {"text": "private reasoning"}},
        {"type": "text", "part": {"text": text}},
        {"type": "step_finish", "part": {
            "reason": reason, "tokens": {"input": 10, "output": 4}, "cost": 0,
        }},
    ])


class OpenCodeProviderTests(unittest.TestCase):
    def test_requires_approved_models_and_exact_supported_variants(self):
        for model in (f"{HAIKU}#low", f"{HAIKU}#high", f"{DEEPSEEK}#high", f"{DEEPSEEK}#max"):
            shim.validate_model(model)
        for model in (HAIKU, f"{DEEPSEEK}#medium", "opencode/claude-haiku-5-5#low", "opencode-go/gemini-3.8-flash#low"):
            with self.subTest(model=model), self.assertRaises(ValueError):
                shim.validate_model(model)

    def test_only_complete_assistant_text_is_returned(self):
        text, finish = shim.parse_response(response())
        self.assertEqual(text, "ข้อความไทย")
        self.assertEqual(finish["reason"], "stop")
        for reason in ("length", "tool-calls", "content-filter", "error", "unknown"):
            with self.subTest(reason=reason), self.assertRaises(ValueError):
                shim.parse_response(response(reason=reason))

    def test_rejects_empty_malformed_missing_finish_and_tool_events(self):
        for stream in (response(text=""), "not JSON", '{"type":"text","part":{"text":"partial"}}', response() + '\n{"type":"tool_use"}', response() + '\n{"type":"error"}'):
            with self.subTest(stream=stream), self.assertRaises(ValueError):
                shim.parse_response(stream)

    def test_transport_uses_stdin_private_server_and_isolated_tool_denied_agent(self):
        observed = {}

        def transport(**kwargs):
            observed.update(kwargs)
            config = json.loads((kwargs["cwd"] / "opencode.json").read_text(encoding="utf-8"))
            self.assertEqual(config["agents"]["novel-stage"]["permissions"], [
                {"action": "*", "resource": "*", "effect": "deny"},
            ])
            self.assertFalse(config["warming"])
            return 0, response(), ""

        output = io.StringIO()
        with patch.object(shim.shutil, "which", return_value="opencode"), patch.object(
            shim, "_run_provider_process", side_effect=transport
        ), patch.object(shim.sys, "stdin", io.StringIO("source text")), contextlib.redirect_stdout(output):
            self.assertEqual(shim.main(["-m", f"{HAIKU}#low"]), 0)
        self.assertEqual(output.getvalue(), "ข้อความไทย")
        self.assertEqual(observed["stdin_input"], "source text")
        self.assertNotIn("source text", observed["command"])
        self.assertIn("--standalone", observed["command"])
        self.assertNotEqual(observed["cwd"], Path.cwd())
        self.assertFalse(observed["cwd"].exists())

    def test_failure_does_not_emit_partial_text(self):
        for code, stream in ((0, response(reason="length")), (124, response()), (1, response())):
            output = io.StringIO()
            with patch.object(shim.shutil, "which", return_value="opencode"), patch.object(
                shim, "_run_provider_process", return_value=(code, stream, "transport failed")
            ), patch.object(shim.sys, "stdin", io.StringIO("source")), contextlib.redirect_stdout(output), contextlib.redirect_stderr(io.StringIO()):
                self.assertNotEqual(shim.main(["-m", f"{HAIKU}#low"]), 0)
            self.assertEqual(output.getvalue(), "")

    def test_usage_preserves_native_counters_without_claiming_free_usage(self):
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "usage.json"
            with patch.dict(os.environ, {"NOVEL_PIPELINE_PROVIDER_USAGE_FILE": str(target)}):
                shim.write_usage({"reason": "stop", "tokens": {"input": 10}, "cost": 0}, f"{HAIKU}#low")
            usage = json.loads(target.read_text(encoding="utf-8"))
            self.assertEqual(usage["opencode_tokens"], {"input": 10})
            self.assertNotIn("cost", usage)
            self.assertEqual(usage["cost_status"], "go_allowance_not_reported")

    def test_all_six_novels_route_only_to_go_with_task_specific_reasoning(self):
        registry = json.loads((ROOT / "00_Config/novel_registry.json").read_text(encoding="utf-8"))
        expected = {
            "term_extraction": f"{HAIKU}#low",
            "term_suggestion": f"{HAIKU}#medium",
            "literal_translation": f"{HAIKU}#low",
            "refinement": f"{DEEPSEEK}#high",
            "qa_judge": f"{DEEPSEEK}#high",
            "project_setup": f"{DEEPSEEK}#high",
            "fetch": f"{HAIKU}#low",
        }
        self.assertEqual(len(registry["novels"]), 6)
        for novel in registry["novels"]:
            config = load_app_config(ROOT / novel["folder"] / ".system/config.yaml")
            for stage, model in expected.items():
                with self.subTest(novel=novel["slug"], stage=stage):
                    route = config.stage_routing_for(stage)
                    self.assertEqual(route.provider, "opencode_go")
                    self.assertEqual(route.model, model)
                    shim.validate_model(model)
                    for provider, fallback in config.fallback_routes_for_stage(stage):
                        self.assertEqual(provider.name, "opencode_go")
                        shim.validate_model(fallback)
            provider = config.provider_for_stage("refinement")
            self.assertEqual(Path(provider.executable[1]), ROOT / "scripts/opencode_provider_shim.py")
            self.assertEqual(provider.prompt_transport, "stdin")
            self.assertEqual(provider.working_dir, config.workspace.root)

    def test_preflight_blocks_missing_opencode_without_calling_a_model(self):
        config = load_app_config(ROOT / "Deep Sea Embers/.system/config.yaml")
        original_which = shim.shutil.which
        with patch("shutil.which", side_effect=lambda value: None if value == "opencode" else original_which(value)):
            result = build_preflight_summary(config)
        self.assertTrue(any("OpenCode" in issue for issue in result["blocking_reasons"]), result)

    def test_preflight_finds_the_go_transport_without_calling_a_model(self):
        config = load_app_config(ROOT / "Deep Sea Embers/.system/config.yaml")
        original_which = shim.shutil.which
        with patch("shutil.which", side_effect=lambda value: "opencode" if value == "opencode" else original_which(value)):
            result = build_preflight_summary(config)
        provider = next(item for item in result["providers"] if item["provider"] == "opencode_go")
        self.assertEqual(provider["status"], "ready")
        self.assertTrue(provider["found"])
        self.assertFalse(any("Provider executable" in reason or "OpenCode CLI" in reason for reason in result["blocking_reasons"]))


if __name__ == "__main__":
    unittest.main()
