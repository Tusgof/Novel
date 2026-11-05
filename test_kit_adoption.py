"""Provider-free checks for the released Kit v4.0.5 adoption contract."""

from __future__ import annotations

import fnmatch
import hashlib
import json
from pathlib import Path
import re
import unittest

import yaml


ROOT = Path(__file__).resolve().parent
ARCHIVE = ROOT / "Backup_/policy/2026-11-05_pre-v4.0.5"
KIT_COMMIT = "5af741b76e5c51442917d41af5ff91ec8ddc90bd"


def digest(path: Path, *, normalize: bool = False) -> str:
    data = path.read_bytes()
    if normalize:
        data = data.replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def effect(rules: list[dict], action: str, resource: str) -> str:
    result = "ask"
    for rule in rules:
        if fnmatch.fnmatchcase(action, rule["action"]) and fnmatch.fnmatchcase(resource, rule["resource"]):
            result = rule["effect"]
    return result


class KitAdoptionTests(unittest.TestCase):
    def test_pin_keeps_the_confirmed_unit_and_tier(self):
        lock = json.loads((ROOT / ".yuehua-kit.json").read_text(encoding="utf-8"))
        self.assertEqual(lock["kit_version"], "4.0.5")
        self.assertEqual(lock["kit_commit"], KIT_COMMIT)
        self.assertEqual(lock["adopted_on"], "2026-11-05")
        self.assertEqual((lock["level"], lock["tier"]), ("UNIT", "T2"))
        self.assertEqual(lock["status"], {
            "state": "active", "decided_on": "2026-10-07",
            "decision_ref": "PROJECT_BRAIN.md Decision Log #3",
        })
        self.assertEqual(lock["deviations"], [])
        self.assertTrue(lock["user_facing"])
        self.assertEqual(lock["real_surface"], "Each novel's final chapter output, gated by output guardrails and Sentinel, and the MoonRead reader built from it")

    def test_prior_policy_and_decision_document_are_byte_identical_archives(self):
        expected = {
            "AGENTS.md": "43ce3d0264dff0205ad65b913b55a9246f30aafd2539fe1b6c75d4c748d9cfce",
            "PROJECT_BRAIN.md": "3c523581213487eb0bd9d7c05cc8165fb93d9a1534ce235eb7913b1bc8edd586",
        }
        for name, sha in expected.items():
            self.assertEqual(digest(ARCHIVE / name), sha)
        old = (ARCHIVE / "PROJECT_BRAIN.md").read_text(encoding="utf-8")
        current = (ROOT / "PROJECT_BRAIN.md").read_text(encoding="utf-8")
        rows = lambda text: [line for line in text.splitlines() if re.match(r"\| \d+ \|", line)]
        self.assertEqual(rows(current)[:len(rows(old))], rows(old))
        self.assertEqual(len(rows(current)), len(rows(old)) + 1)

    def test_released_browser_and_execution_policies_are_pinned_bytes(self):
        expected = {
            "agent-browser.md": "ca485aa17fa9e90b05b3726d56aadc6af9b7baf106a534ca44749c7fa649ec2c",
            "execution-workers.md": "4bce2fe0be4b437de5d5148c63918510ff42e102f58bc8a3468c85fc944e1672",
        }
        for name, sha in expected.items():
            self.assertEqual(digest(ROOT / "policies" / name), sha)

    def test_unit_contract_retains_stronger_rules_and_uses_tool_neutral_policy(self):
        old = (ARCHIVE / "AGENTS.md").read_text(encoding="utf-8")
        current = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertEqual(current.split("## Yuehua Kit v4 Contract")[0], old.split("## Yuehua Kit v4 Contract")[0])
        self.assertIn("policies/agent-browser.md", current)
        self.assertIn("policies/execution-workers.md", current)
        self.assertIn("no browser product is required or preferred", current)
        self.assertNotIn("BrowserOS is the default", current)
        self.assertNotIn("12-Operate-[AGENT_BROWSER]", current)
        for term in ("OAuth", "prompt-skipping", "private tunnel", "vault", "resource", "profile", "EXPOSURE", "Medium/high", "immediately", "current model", "Extra Usage"):
            self.assertIn(term, current)

    def test_low_worker_uses_the_native_go_variant_and_denies_other_authority(self):
        text = (ROOT / ".opencode/agents/execution-worker.md").read_text(encoding="utf-8")
        profile = yaml.safe_load(text.split("---", 2)[1])
        self.assertEqual(profile["mode"], "subagent")
        self.assertEqual(profile["model"], "opencode-go/deepseek-v4.1-flash#low")
        self.assertNotIn("default_agent", profile)
        for action in ("read", "edit"):
            self.assertEqual(effect(profile["permissions"], action, "novel_pipeline/example.py"), "allow")
        for action in ("shell", "execute", "webfetch", "websearch", "subagent", "external_directory", "github_create_pull_request"):
            self.assertEqual(effect(profile["permissions"], action, "*"), "deny")
        for resource in (".env", "AGENTS.md", "CLAUDE.md", "PROJECT_BRAIN.md", "IMPLEMENT_PLAN.md", "ARCHITECTURE.md", "DOC_RECOVERY.md", "NOVEL_OPERATOR_GUIDE.md", "HERDR_WORKER_PROTOCOL.md", ".yuehua-kit.json", ".github/workflows/tests.yml", ".opencode/agents/novel-worker.md", "policies/agent-browser.md", "Backup_/policy/example.md"):
            self.assertEqual(effect(profile["permissions"], "edit", resource), "deny", resource)

    def test_other_worker_and_product_routes_are_unchanged(self):
        expected = {
            ".opencode/agents/novel-worker.md": "1e3392ba5b1d6ac788877d49582049243d93bb43a5897d5c438f81dbf3f3be41",
            "Deep Sea Embers/.system/providers.yaml": "ddf82a1448f1aa1838142bd20e2d81663b47ff5657538f95a54a7ab8a18962e5",
            "Horror Game Developers/.system/providers.yaml": "0d311b225725840fc746872eccaea4a68bb3998a4317f808dbe6d3fe11feef8b",
            "Infinite Regressor Stories/.system/providers.yaml": "0d311b225725840fc746872eccaea4a68bb3998a4317f808dbe6d3fe11feef8b",
            "One Hit Kill Swordmaster/.system/providers.yaml": "bb6f64f5b1e1921df0641b31298bc762bfa00293dcfc0d7bae25cdb9c56fe7af",
            "Re Zero Watching Him Die Again and Again/.system/providers.yaml": "0d311b225725840fc746872eccaea4a68bb3998a4317f808dbe6d3fe11feef8b",
            "Ten Day Ultimatum/.system/providers.yaml": "9404ee567a8715dca26e78fdbb815fba4c3c7e854a9df314dde03a5603c32b08",
        }
        for name, sha in expected.items():
            self.assertEqual(digest(ROOT / name, normalize=True), sha, name)

    def test_control_document_hashes_match_the_checked_out_bytes(self):
        text = (ROOT / "DOC_RECOVERY.md").read_text(encoding="utf-8")
        pairs = re.findall(r"\| `([^`]+\.md)` \| `([A-Fa-f0-9]{64})` \|", text)
        self.assertEqual(len(pairs), 4)
        for name, sha in pairs:
            self.assertEqual(digest(ROOT / name), sha.lower(), name)


if __name__ == "__main__":
    unittest.main()
