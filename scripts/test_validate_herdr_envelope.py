import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

import validate_herdr_envelope as validator


HASH = "4d0a29ecadb27ea9e0a001c1496817182bde64d4"


def envelope(phase="ACK"):
    value = {
        "protocol": "HERDR/1",
        "phase": phase,
        "order_id": "NOVEL-HERDR-20260831-001",
        "nonce": "9f741a1c-0c64-4c98-bc72-b22f4db6c805",
        "sender": "Inspector wK:p2",
        "recipient": "Worker wK:p5",
        "repository": "Novel",
        "branch": "main",
        "base_hash": HASH,
        "worker": {
            "kind": "coding-agent-worker",
            "surface": "separate-tab-pane",
            "runtime": "gpt-5.6-luna",
            "reasoning": "max",
            "sandbox": "workspace-write",
            "approval": "never",
        },
        "scope": {
            "allowed_paths": ["AGENTS.md", "scripts/example.py"],
            "allowed_actions": ["read", "edit"],
            "forbidden_paths": ["PROJECT_BRAIN.md"],
            "forbidden_actions": ["network"],
            "dirty_wip_boundary": "preserve all pre-existing modified/untracked paths",
        },
        "stop_conditions": ["unexpected scope expansion"],
        "handoff": {
            "transport": "Herdr",
            "recipient": "Inspector",
            "return_required": True,
            "worker_must_press_enter": True,
        },
    }
    if phase == "ACK":
        value["ack"] = {"scope_echoed": True, "commands": 0, "files_read": 0, "edits": 0}
    elif phase == "SMOKE":
        value["smoke"] = {
            "cwd": "D:/Fogust/Workspace/Novel",
            "branch": "main",
            "head": HASH,
            "status": "## main...origin/main",
            "edits": 0,
        }
    elif phase == "START":
        value["authorization"] = {"authorized": True}
    elif phase == "RETURN":
        value["result"] = {
            "status": "complete",
            "local_hashes": {"head": HASH, "worktree": HASH},
            "changed_paths": ["AGENTS.md", "scripts/example.py"],
            "commands": [{"command": "python -m unittest", "result": "pass"}],
            "external_actions": {"performed": False, "details": "None"},
            "worktree": {"dirty_wip_preserved": True, "diff_scope": ["AGENTS.md"]},
            "blockers": [],
            "manual_gates": [],
            "next_action": "Inspector verifies the bounded diff",
        }
    return value


class ValidateHerdrEnvelopeTests(unittest.TestCase):
    def assert_valid(self, value):
        self.assertEqual(validator.validate_envelope(value), [])

    def assert_error_contains(self, value, text):
        errors = validator.validate_envelope(value)
        self.assertTrue(any(text in error for error in errors), errors)

    def test_ack_smoke_start_and_return_are_valid(self):
        for phase in ("ACK", "SMOKE", "START", "RETURN"):
            with self.subTest(phase=phase):
                self.assert_valid(envelope(phase))

    def test_return_rejects_path_outside_allowed_scope(self):
        value = envelope("RETURN")
        value["result"]["changed_paths"] = ["PROJECT_BRAIN.md"]
        self.assert_error_contains(value, "outside scope")

    def test_rejects_wrong_worker_runtime(self):
        value = envelope()
        value["worker"]["runtime"] = "provider/model"
        self.assert_error_contains(value, "worker.runtime")

    def test_ack_rejects_activity_before_start(self):
        value = envelope()
        value["ack"]["files_read"] = 1
        self.assert_error_contains(value, "ack.files_read")

    def test_rejects_missing_stop_rules_and_incomplete_handoff(self):
        value = envelope()
        value["stop_conditions"] = []
        value["handoff"]["return_required"] = False
        errors = validator.validate_envelope(value)
        self.assertTrue(any("stop_conditions" in error for error in errors), errors)
        self.assertTrue(any("handoff.return_required" in error for error in errors), errors)

    def test_rejects_scope_overlap_and_nonzero_smoke_edits(self):
        value = envelope("SMOKE")
        value["scope"]["forbidden_paths"].append("AGENTS.md")
        value["smoke"]["edits"] = 1
        errors = validator.validate_envelope(value)
        self.assertTrue(any("cannot appear in both lists" in error for error in errors), errors)
        self.assertTrue(any("smoke.edits" in error for error in errors), errors)

    def test_cli_reports_actionable_invalid_envelope(self):
        output = io.StringIO()
        value = envelope("START")
        value["authorization"]["authorized"] = False
        with patch.object(validator, "_read_json", return_value=value), redirect_stdout(output):
            result = validator.main(["-"])
        self.assertEqual(result, 1)
        self.assertIn("authorization.authorized", output.getvalue())


if __name__ == "__main__":
    unittest.main()
