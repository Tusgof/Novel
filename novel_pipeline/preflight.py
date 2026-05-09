from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any

from novel_pipeline.types import AppConfig

_GENERATED_REPORT_PREFIXES: tuple[str, ...] = (
    "checkpoint_",
    "cleanliness_",
    "provider_usage_",
    "glossary_decisions_",
    "glossary_conflicts_",
    "glossary_audit_",
    "glossary_guard_",
    "product_review_",
)


def _resolve_executable(command: tuple[str, ...]) -> tuple[bool, str]:
    if not command:
        return False, ""
    target = command[0]
    candidate = Path(target)
    if candidate.is_absolute():
        return candidate.exists(), str(candidate)
    resolved = shutil.which(target)
    if resolved:
        return True, resolved
    return False, target


def _git_capture(workspace_root: Path, *args: str) -> tuple[bool, str]:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=str(workspace_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False, ""
    output = (completed.stdout or completed.stderr or "").strip()
    return completed.returncode == 0, output


def _status_line_path(line: str) -> str:
    if len(line) >= 3 and line[2] == " ":
        raw = line[3:]
    else:
        parts = line.split(maxsplit=1)
        raw = parts[1] if len(parts) == 2 else line
    path_text = raw.split(" -> ", 1)[-1].strip()
    return path_text.replace("\\", "/")


def _is_generated_report_path(path_text: str) -> bool:
    normalized = path_text.replace("\\", "/").strip()
    if not normalized.startswith("07_Reports/"):
        return False
    name = Path(normalized).name
    if name in {"preflight_report.md", "recovery_drill.md"}:
        return True
    return any(name.startswith(prefix) and name.endswith(".md") for prefix in _GENERATED_REPORT_PREFIXES)


def build_preflight_summary(config: AppConfig) -> dict[str, Any]:
    warnings: list[str] = []
    blocking_reasons: list[str] = []
    provider_stage_map: dict[str, list[str]] = {}
    for stage, routing in config.stage_routing.items():
        provider_stage_map.setdefault(routing.provider, []).append(stage)
        for fallback in routing.fallbacks:
            provider_name = str(fallback.get("provider", "")).strip()
            if provider_name:
                provider_stage_map.setdefault(provider_name, []).append(f"{stage}:fallback")

    provider_checks: list[dict[str, Any]] = []
    for provider_name in sorted(provider_stage_map):
        spec = config.providers[provider_name]
        found, resolved_path = _resolve_executable(spec.executable)
        command_preview = list(spec.executable) + list(spec.extra_args)
        provider_status = "ready" if found else "blocked"
        if not found:
            blocking_reasons.append(
                f"Provider executable not found: {provider_name} ({spec.executable[0]})."
            )
        provider_checks.append(
            {
                "provider": provider_name,
                "status": provider_status,
                "found": found,
                "resolved_path": resolved_path,
                "command": command_preview,
                "prompt_transport": spec.prompt_transport,
                "working_dir": str(spec.working_dir) if spec.working_dir else "",
                "stages": sorted(provider_stage_map[provider_name]),
            }
        )

    research = config.research_readiness_summary()
    if not research["bounded_translation_ready"]:
        blocking_reasons.append(
            "Research profile is not ready for bounded translation."
        )
    elif not research["translation_ready"]:
        warnings.append("Research profile is drafted; full production remains gated.")

    git_available = shutil.which("git") is not None
    git_summary: dict[str, Any] = {
        "available": git_available,
        "in_work_tree": False,
        "branch": "",
        "head": "",
        "origin": "",
        "status_short": "",
        "clean": False,
        "warnings": [],
        "ignored_generated_changes": [],
    }
    if not git_available:
        git_summary["warnings"].append("git is not available in PATH.")
        warnings.append("git is not available in PATH; backup guardrails are reduced.")
    else:
        ok, inside = _git_capture(config.workspace.root, "rev-parse", "--is-inside-work-tree")
        git_summary["in_work_tree"] = ok and inside.strip().lower() == "true"
        if not git_summary["in_work_tree"]:
            git_summary["warnings"].append("Workspace is not inside a git work tree.")
            warnings.append("Workspace is not inside a git work tree; commit/push guardrails are unavailable.")
        else:
            _, git_summary["branch"] = _git_capture(config.workspace.root, "branch", "--show-current")
            _, git_summary["head"] = _git_capture(config.workspace.root, "rev-parse", "--short", "HEAD")
            origin_ok, git_summary["origin"] = _git_capture(config.workspace.root, "remote", "get-url", "origin")
            _, git_summary["status_short"] = _git_capture(config.workspace.root, "status", "--short")
            status_lines = [line for line in git_summary["status_short"].splitlines() if line.strip()]
            relevant_lines: list[str] = []
            ignored_generated_changes: list[str] = []
            for line in status_lines:
                path_text = _status_line_path(line)
                if _is_generated_report_path(path_text):
                    ignored_generated_changes.append(path_text)
                else:
                    relevant_lines.append(line)
            git_summary["status_short"] = "\n".join(relevant_lines)
            git_summary["ignored_generated_changes"] = ignored_generated_changes
            git_summary["clean"] = not bool(relevant_lines)
            if not git_summary["clean"]:
                git_summary["warnings"].append("Working tree is dirty.")
                warnings.append("Working tree is dirty; commit or stash before large write actions.")
            if not origin_ok:
                git_summary["warnings"].append("Remote 'origin' is not configured.")
                warnings.append("Remote 'origin' is not configured; push-based backup guardrails are unavailable.")

    required_dirs = [
        ".system",
        "01_Glossary",
        "03_Raw",
        "04_Work",
        "05_Output",
        "06_Logs",
        "07_Reports",
    ]
    missing_dirs = [name for name in required_dirs if not (config.workspace.root / name).exists()]
    if missing_dirs:
        blocking_reasons.append("Workspace is missing required directories: " + ", ".join(missing_dirs))

    if blocking_reasons:
        status = "blocked"
    elif warnings:
        status = "degraded"
    else:
        status = "ready"
    next_safe_action = "Preflight is ready for normal production."
    if status == "blocked":
        next_safe_action = "Fix blocking issues before translation or resume."
    elif status == "degraded":
        next_safe_action = "Continue only with bounded operations while warnings remain."

    return {
        "status": status,
        "workspace_root": str(config.workspace.root),
        "config_path": str(config.config_path),
        "providers": provider_checks,
        "git": git_summary,
        "research_readiness": research,
        "missing_directories": missing_dirs,
        "warnings": warnings,
        "blocking_reasons": blocking_reasons,
        "next_safe_action": next_safe_action,
    }


def print_preflight_summary(summary: dict[str, Any]) -> None:
    print(f"Preflight: {summary['status']}")
    print(f"Workspace: {summary['workspace_root']}")
    print(f"Config: {summary['config_path']}")
    print("Providers:")
    for item in summary["providers"]:
        status = "ready" if item["found"] else "missing"
        stages = ", ".join(item["stages"])
        print(f"  - {item['provider']}: {status} ({item['resolved_path']}) [{stages}]")
    git_info = summary["git"]
    print("Git guardrails:")
    if not git_info["available"]:
        print("  - git unavailable")
    elif not git_info["in_work_tree"]:
        print("  - not inside a git work tree")
    else:
        clean_text = "clean" if git_info["clean"] else "dirty"
        print(f"  - branch: {git_info['branch'] or '(detached)'}")
        print(f"  - head: {git_info['head']}")
        print(f"  - remote origin: {git_info['origin'] or 'missing'}")
        print(f"  - working tree: {clean_text}")
        if git_info.get("ignored_generated_changes"):
            print(
                "  - ignored generated report changes: "
                + ", ".join(git_info["ignored_generated_changes"])
            )
    research = summary["research_readiness"]
    print("Research readiness:")
    print(
        "  - status: "
        f"{research['status']} / {research['readiness']} "
        f"(bounded={'yes' if research['bounded_translation_ready'] else 'no'}, "
        f"production={'yes' if research['translation_ready'] else 'no'})"
    )
    if summary["missing_directories"]:
        print("Missing directories:")
        for item in summary["missing_directories"]:
            print(f"  - {item}")
    if summary["warnings"]:
        print("Warnings:")
        for item in summary["warnings"]:
            print(f"  - {item}")
    if summary["blocking_reasons"]:
        print("Blocking:")
        for item in summary["blocking_reasons"]:
            print(f"  - {item}")
    print(f"Next safe action: {summary['next_safe_action']}")
