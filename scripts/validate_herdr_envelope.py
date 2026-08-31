"""Validate a HERDR/1 envelope without runtime or provider dependencies."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


PROTOCOL = "HERDR/1"
PHASES = {"ACK", "SMOKE", "START", "RETURN"}
SHA1 = re.compile(r"^[0-9a-fA-F]{40}$")


def _required_mapping(value: Any, path: str, errors: list[str]) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        errors.append(f"{path}: expected a JSON object")
        return None
    return value


def _required_string(mapping: dict[str, Any], key: str, errors: list[str]) -> str | None:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{key}: required non-empty string")
        return None
    return value


def _required_sha1(mapping: dict[str, Any], key: str, errors: list[str], path: str | None = None) -> str | None:
    value = mapping.get(key)
    label = path or key
    if not isinstance(value, str) or not SHA1.fullmatch(value):
        errors.append(f"{label}: expected a 40-character hexadecimal hash")
        return None
    return value


def _required_string_list(mapping: dict[str, Any], key: str, errors: list[str]) -> list[str] | None:
    value = mapping.get(key)
    if not isinstance(value, list):
        errors.append(f"scope.{key}: required JSON array of non-empty strings")
        return None
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            errors.append(f"scope.{key}[{index}]: expected a non-empty string")
    return value


def _check_no_overlap(first: list[str] | None, second: list[str] | None, label: str, errors: list[str]) -> None:
    if first is None or second is None:
        return
    left = {item for item in first if isinstance(item, str)}
    right = {item for item in second if isinstance(item, str)}
    overlap = sorted(left.intersection(right))
    if overlap:
        errors.append(f"scope.{label}: entries cannot appear in both lists: {', '.join(overlap)}")


def _check_result_list(value: Any, path: str, errors: list[str]) -> None:
    if not isinstance(value, list):
        errors.append(f"{path}: expected a JSON array of strings")
        return
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            errors.append(f"{path}[{index}]: expected a non-empty string")


def _check_return_result(result: dict[str, Any], scope: dict[str, Any], errors: list[str]) -> None:
    status = result.get("status")
    if status not in {"complete", "blocked"}:
        errors.append("result.status: expected 'complete' or 'blocked'")

    hashes = result.get("local_hashes")
    if not isinstance(hashes, dict) or not hashes:
        errors.append("result.local_hashes: required non-empty object of labeled hashes")
    elif any(not isinstance(label, str) or not label.strip() for label in hashes):
        errors.append("result.local_hashes: every label must be a non-empty string")
    else:
        for label, value in hashes.items():
            if not isinstance(value, str) or not SHA1.fullmatch(value):
                errors.append(f"result.local_hashes.{label}: expected a 40-character hexadecimal hash")

    changed_paths = result.get("changed_paths")
    if not isinstance(changed_paths, list):
        errors.append("result.changed_paths: required JSON array of repository-relative paths")
    else:
        allowed = scope.get("allowed_paths")
        forbidden = scope.get("forbidden_paths")
        for index, path in enumerate(changed_paths):
            if not isinstance(path, str) or not path.strip():
                errors.append(f"result.changed_paths[{index}]: expected a non-empty path")
            elif isinstance(allowed, list) and path not in allowed:
                errors.append(f"result.changed_paths[{index}]: path is outside scope: {path}")
            elif isinstance(forbidden, list) and path in forbidden:
                errors.append(f"result.changed_paths[{index}]: path is forbidden: {path}")

    commands = result.get("commands")
    if not isinstance(commands, list):
        errors.append("result.commands: required JSON array of command/result objects")
    else:
        for index, record in enumerate(commands):
            if not isinstance(record, dict):
                errors.append(f"result.commands[{index}]: expected an object")
                continue
            if not isinstance(record.get("command"), str) or not record["command"].strip():
                errors.append(f"result.commands[{index}].command: required non-empty string")
            if not isinstance(record.get("result"), str) or not record["result"].strip():
                errors.append(f"result.commands[{index}].result: required non-empty string")

    external = _required_mapping(result.get("external_actions"), "result.external_actions", errors)
    if external is not None:
        if type(external.get("performed")) is not bool:
            errors.append("result.external_actions.performed: required boolean")
        if not isinstance(external.get("details"), str) or not external["details"].strip():
            errors.append("result.external_actions.details: required non-empty string")

    worktree = _required_mapping(result.get("worktree"), "result.worktree", errors)
    if worktree is not None:
        if worktree.get("dirty_wip_preserved") is not True:
            errors.append("result.worktree.dirty_wip_preserved: must be true")
        _check_result_list(worktree.get("diff_scope"), "result.worktree.diff_scope", errors)

    _check_result_list(result.get("blockers"), "result.blockers", errors)
    _check_result_list(result.get("manual_gates"), "result.manual_gates", errors)
    next_action = result.get("next_action")
    if not isinstance(next_action, str) or not next_action.strip():
        errors.append("result.next_action: required non-empty string")
    if status == "blocked" and isinstance(result.get("blockers"), list) and not result["blockers"]:
        errors.append("result.blockers: blocked returns must name at least one blocker")


def validate_envelope(envelope: Any) -> list[str]:
    """Return actionable validation errors; an empty list means valid."""

    errors: list[str] = []
    root = _required_mapping(envelope, "envelope", errors)
    if root is None:
        return errors

    if root.get("protocol") != PROTOCOL:
        errors.append(f"protocol: expected {PROTOCOL!r}")
    phase = root.get("phase")
    if phase not in PHASES:
        errors.append("phase: expected one of ACK, SMOKE, START, RETURN")

    for key in ("order_id", "nonce", "sender", "recipient", "repository", "branch"):
        _required_string(root, key, errors)
    _required_sha1(root, "base_hash", errors)

    worker = _required_mapping(root.get("worker"), "worker", errors)
    if worker is not None:
        expected_worker = {
            "kind": "coding-agent-worker",
            "surface": "separate-tab-pane",
            "runtime": "gpt-5.6-luna",
            "reasoning": "max",
            "sandbox": "workspace-write",
            "approval": "never",
        }
        for key, expected in expected_worker.items():
            if worker.get(key) != expected:
                errors.append(f"worker.{key}: expected {expected!r}")

    scope = _required_mapping(root.get("scope"), "scope", errors)
    if scope is not None:
        allowed_paths = _required_string_list(scope, "allowed_paths", errors)
        forbidden_paths = _required_string_list(scope, "forbidden_paths", errors)
        allowed_actions = _required_string_list(scope, "allowed_actions", errors)
        forbidden_actions = _required_string_list(scope, "forbidden_actions", errors)
        _required_string(scope, "dirty_wip_boundary", errors)
        _check_no_overlap(allowed_paths, forbidden_paths, "allowed_paths/forbidden_paths", errors)
        _check_no_overlap(allowed_actions, forbidden_actions, "allowed_actions/forbidden_actions", errors)
    else:
        scope = {}

    stop_conditions = root.get("stop_conditions")
    _check_result_list(stop_conditions, "stop_conditions", errors)
    if isinstance(stop_conditions, list) and not stop_conditions:
        errors.append("stop_conditions: at least one stop condition is required")

    handoff = _required_mapping(root.get("handoff"), "handoff", errors)
    if handoff is not None:
        expected_handoff = {
            "transport": "Herdr",
            "recipient": "Inspector",
            "return_required": True,
            "worker_must_press_enter": True,
        }
        for key, expected in expected_handoff.items():
            if handoff.get(key) != expected:
                errors.append(f"handoff.{key}: expected {expected!r}")

    if phase == "ACK":
        ack = _required_mapping(root.get("ack"), "ack", errors)
        if ack is not None:
            if ack.get("scope_echoed") is not True:
                errors.append("ack.scope_echoed: must be true")
            for key in ("commands", "files_read", "edits"):
                if type(ack.get(key)) is not int or ack.get(key) != 0:
                    errors.append(f"ack.{key}: must be integer 0")
    elif phase == "SMOKE":
        smoke = _required_mapping(root.get("smoke"), "smoke", errors)
        if smoke is not None:
            _required_string(smoke, "cwd", errors)
            _required_string(smoke, "branch", errors)
            _required_sha1(smoke, "head", errors, "smoke.head")
            _required_string(smoke, "status", errors)
            if type(smoke.get("edits")) is not int or smoke.get("edits") != 0:
                errors.append("smoke.edits: must be integer 0")
    elif phase == "START":
        authorization = _required_mapping(root.get("authorization"), "authorization", errors)
        if authorization is not None and authorization.get("authorized") is not True:
            errors.append("authorization.authorized: must be true for START")
    elif phase == "RETURN":
        result = _required_mapping(root.get("result"), "result", errors)
        if result is not None:
            _check_return_result(result, scope, errors)

    return errors


def _read_json(source: str) -> Any:
    if source == "-":
        return json.load(sys.stdin)
    return json.loads(Path(source).read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate one HERDR/1 JSON envelope (use '-' or omit the path for stdin)."
    )
    parser.add_argument("envelope", nargs="?", default="-", help="JSON file path, or '-' for stdin")
    args = parser.parse_args(argv)

    try:
        envelope = _read_json(args.envelope)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        print(f"INVALID: cannot read JSON envelope: {exc}", file=sys.stderr)
        return 2

    errors = validate_envelope(envelope)
    if errors:
        print("INVALID")
        for error in errors:
            print(f"- {error}")
        return 1

    print("VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
