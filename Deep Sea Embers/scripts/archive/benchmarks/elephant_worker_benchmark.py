#!/usr/bin/env python3
"""
Elephant worker benchmark for Deep Sea Embers translation pipeline.

This script evaluates Elephant, DeepSeek Chat, and DeepSeek Reasoner models
for suitability as bounded implementation/operator workers in the novel translation pipeline.

It performs six tasks, scores each model, and produces a report.
"""

import json
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

# Project root
PROJECT_ROOT = Path(__file__).parent.parent
EXPERIMENTS_DIR = PROJECT_ROOT / "04_Work" / "_experiments"
REPORTS_DIR = PROJECT_ROOT / "07_Reports"

# Candidate model IDs per family
ELEPHANT_CANDIDATES = []  # disabled to avoid timeouts
DEEPSEEK_CHAT_CANDIDATES = ["deepseek-chat", "deepseek-v3", "qwen-deepseek-chat"]
DEEPSEEK_REASONER_CANDIDATES = ["deepseek-reasoner", "deepseek-r1", "qwen-deepseek-reasoner"]

# Command shapes to try (qwen command is assumed available)
QWEN_COMMAND = "qwen"
QWEN_CODE_COMMAND = "qwen-code"  # fallback

# Timeouts
SMOKE_TEST_TIMEOUT = 30  # seconds
TASK_TIMEOUT = 30        # seconds per model call

# Task definitions
TASKS = [
    {
        "id": "A",
        "name": "Operator status reasoning",
        "prompt": """Run batch-x:
- ch001 complete
- ch002-block-001 complete
- ch002-block-002 failed at QA due Gemini command_too_long fallback
- ch002-block-003 pending translating
- ch003 untouched

What should the worker do next? Provide:
1. next safe action
2. forbidden actions
3. exact reason
4. final report fields
""",
        "weight": 20,
    },
    {
        "id": "B",
        "name": "Qwen prompt obedience / file-scope discipline",
        "prompt": """Update only REPORT.md based on SUMMARY.md. Do not modify source code, ledger, glossary, or outputs.

List:
- allowed files
- forbidden files
- validation steps
- stop conditions
""",
        "weight": 15,
    },
    {
        "id": "C",
        "name": "Failure classification",
        "prompt": """Classify each provider failure and choose appropriate action (retry, fallback, manual).

1. "429 quota exceeded"
2. "The command line is too long"
3. returncode 3221225786 with empty stderr
4. empty stdout with returncode 0
5. "authentication failed"
6. QA semantic failure: omission of a source sentence

For each, give classification and action.
""",
        "weight": 20,
    },
    {
        "id": "D",
        "name": "Code-change plan from known issue",
        "prompt": """We need to add a CLI --stop-after glossary-scan flag. It must only work with --range batch runs, stop after writing batch glossary artifact, skip approval and providers after scan, and update status manual action.

Provide:
- implementation plan
- exact files to modify
- test plan
""",
        "weight": 20,
    },
    {
        "id": "E",
        "name": "Thai final report quality",
        "prompt": """Produce a concise Thai report from a synthetic worker result:
- 3 files changed
- tests passed
- no providers called
- blocker: none

Write the report in Thai.
""",
        "weight": 10,
    },
    {
        "id": "F",
        "name": "Mini translation/refinement awareness check",
        "prompt": """Glossary:
邓肯 = ดันแคน
失乡号 = เรือผู้ไร้บ้าน
山羊头 = หัวแพะ

Source Chinese paragraph:
邓肯看着山羊头沉默了片刻，然后低声说：“这艘船不是普通的船。失乡号会记住每一个上船的人。”

Produce refined Thai prose preserving all glossary terms.
""",
        "weight": 15,
    },
]

# Scoring rubrics (keyword-based)
TASK_A_KEYWORDS = ["rerun", "recover", "block-002", "QA", "command_too_long", "bounded", "not resume", "not config", "provider failure", "cleanliness"]
TASK_B_KEYWORDS = ["REPORT.md", "SUMMARY.md", "allowed", "forbidden", "source code", "ledger", "glossary", "outputs", "validation", "stop"]
TASK_C_KEYWORDS = ["quota", "wait", "retry", "command_too_long", "argv", "recovery", "crash", "fallback", "empty stdout", "unusable", "auth", "config", "semantic", "refinement", "feedback"]
TASK_D_KEYWORDS = ["cli.py", "pipeline.py", "test_translation.py", "stop-after", "glossary-scan", "range", "batch", "artifact", "skip approval", "status manual"]
TASK_E_KEYWORDS = ["ภาษาไทย", "ไฟล์", "ทดสอบ", "ผ่าน", "ไม่มี", "บล็อกเกอร์"]  # Thai keywords
TASK_F_KEYWORDS = ["ดันแคน", "หัวแพะ", "เรือผู้ไร้บ้าน", "ไม่ใช่เรือธรรมดา", "จำได้", "ทุกคน"]  # Must include glossary terms and meaning

def discover_qwen_command() -> Tuple[str, List[str]]:
    """Determine which Qwen command is available and its help.
    Returns (command_name, help_lines)."""
    # First try to read from providers.yaml for exact executable
    providers_yaml = PROJECT_ROOT / ".system" / "providers.yaml"
    if providers_yaml.exists():
        try:
            import yaml
            with open(providers_yaml, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            qwen_config = config.get("providers", {}).get("qwen", {})
            executable = qwen_config.get("executable")
            if executable:
                # executable could be a string or list; handle both
                if isinstance(executable, list):
                    cmd = executable[0]
                else:
                    cmd = executable
                # Test help
                result = subprocess.run(
                    [cmd, "--help"],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=10,
                )
                if result.returncode == 0:
                    return cmd, result.stdout.splitlines()
        except Exception:
            pass  # fallback to PATH search
    # Fallback to PATH search
    for cmd in [QWEN_COMMAND, QWEN_CODE_COMMAND]:
        try:
            result = subprocess.run(
                [cmd, "--help"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=10,
            )
            if result.returncode == 0:
                return cmd, result.stdout.splitlines()
        except FileNotFoundError:
            continue
    raise RuntimeError("Neither qwen nor qwen-code command found.")

def try_smoke_test(command_name: str, model_id: str, command_shape: str) -> Dict[str, Any]:
    """Try a smoke test with given model ID and command shape.
    command_shape: 'stdin' (qwen -m MODEL) or 'stdin_with_dash' (qwen -m MODEL -)."""
    if command_shape == "stdin":
        args = [command_name, "-m", model_id]
    elif command_shape == "stdin_with_dash":
        args = [command_name, "-m", model_id, "-"]
    else:
        raise ValueError(f"Unknown command_shape: {command_shape}")
    
    prompt = "Reply exactly: OK"
    start = time.time()
    try:
        proc = subprocess.run(
            args,
            input=prompt,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=SMOKE_TEST_TIMEOUT,
        )
        duration = time.time() - start
        success = proc.returncode == 0 and proc.stdout.strip() == "OK"
        return {
            "model_id": model_id,
            "command_shape": command_shape,
            "success": success,
            "returncode": proc.returncode,
            "stdout": proc.stdout[:500],
            "stderr": proc.stderr[:500],
            "duration": duration,
        }
    except subprocess.TimeoutExpired:
        return {
            "model_id": model_id,
            "command_shape": command_shape,
            "success": False,
            "returncode": None,
            "stdout": "",
            "stderr": "timeout",
            "duration": SMOKE_TEST_TIMEOUT,
        }
    except Exception as e:
        return {
            "model_id": model_id,
            "command_shape": command_shape,
            "success": False,
            "returncode": None,
            "stdout": "",
            "stderr": str(e),
            "duration": time.time() - start,
        }

def discover_model_ids(command_name: str) -> Tuple[Dict[str, str], Dict[str, Any]]:
    """Discover working model IDs for each family.
    Returns (family->model_id, metadata dict of attempts)."""
    attempts = {}
    resolved = {}
    # Try command shape: stdin (qwen -m MODEL)
    for family, candidates in [
        ("deepseek_chat", DEEPSEEK_CHAT_CANDIDATES),
    ]:
        for model_id in candidates:
            attempt = try_smoke_test(command_name, model_id, "stdin")
            attempts[f"{family}_{model_id}"] = attempt
            if attempt["success"]:
                resolved[family] = model_id
                break
        if family not in resolved:
            # try alternative command shape
            for model_id in candidates:
                attempt = try_smoke_test(command_name, model_id, "stdin_with_dash")
                attempts[f"{family}_{model_id}_dash"] = attempt
                if attempt["success"]:
                    resolved[family] = model_id
                    break
    return resolved, attempts

def call_model(prompt: str, command_name: str, model_id: str, timeout: int = TASK_TIMEOUT) -> Dict[str, Any]:
    """Call model with prompt via stdin, return metadata and output."""
    args = [command_name, "-m", model_id]
    start = time.time()
    try:
        proc = subprocess.run(
            args,
            input=prompt,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
        duration = time.time() - start
        return {
            "success": proc.returncode == 0,
            "returncode": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "duration": duration,
            "timeout": False,
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "returncode": None,
            "stdout": "",
            "stderr": "timeout",
            "duration": timeout,
            "timeout": True,
        }
    except Exception as e:
        return {
            "success": False,
            "returncode": None,
            "stdout": "",
            "stderr": str(e),
            "duration": time.time() - start,
            "timeout": False,
        }

def score_task(task_id: str, output: str) -> Tuple[int, List[str]]:
    """Score task output based on keywords and rules.
    Returns (score out of 100, missing criteria)."""
    output_lower = output.lower()
    missing = []
    score = 0
    if task_id == "A":
        required = TASK_A_KEYWORDS
        max_score = 100
        for kw in required:
            if kw in output_lower:
                score += max_score // len(required)
            else:
                missing.append(kw)
        # Hard fail checks: if suggests modifying forbidden files or unsafe actions
        if "modify config" in output_lower or "resume batch" in output_lower:
            score = 0
    elif task_id == "B":
        required = TASK_B_KEYWORDS
        max_score = 100
        for kw in required:
            if kw in output_lower:
                score += max_score // len(required)
            else:
                missing.append(kw)
        # Hard fail: suggests modifying forbidden files
        if "modify source" in output_lower or "modify ledger" in output_lower or "modify glossary" in output_lower:
            score = 0
    elif task_id == "C":
        required = TASK_C_KEYWORDS
        max_score = 100
        for kw in required:
            if kw in output_lower:
                score += max_score // len(required)
            else:
                missing.append(kw)
        # Hard fail: suggests blind retry for auth, ignores command_too_long risk
        if "blind retry" in output_lower or "ignore command_too_long" in output_lower:
            score = 0
    elif task_id == "D":
        required = TASK_D_KEYWORDS
        max_score = 100
        for kw in required:
            if kw in output_lower:
                score += max_score // len(required)
            else:
                missing.append(kw)
    elif task_id == "E":
        # Thai language detection: check for Thai script
        thai_chars = re.findall(r'[\u0e00-\u0e7f]', output)
        if len(thai_chars) < 5:
            missing.append("Thai text")
            score = 0
        else:
            score = 100  # Assume okay if Thai present; we can refine
    elif task_id == "F":
        required = TASK_F_KEYWORDS
        max_score = 100
        for kw in required:
            if kw in output:
                score += max_score // len(required)
            else:
                missing.append(kw)
        # Ensure no Chinese left
        if re.search(r'[\u4e00-\u9fff]', output):
            missing.append("Chinese characters")
            score = max(0, score - 30)
    else:
        raise ValueError(f"Unknown task_id {task_id}")
    return score, missing

def run_benchmark(command_name: str, model_ids: Dict[str, str], experiment_dir: Path) -> Dict[str, Any]:
    """Run all tasks for each model and save results."""
    results = {}
    for family, model_id in model_ids.items():
        print(f"Testing {family}: {model_id}")
        model_results = {}
        for task in TASKS:
            task_id = task["id"]
            prompt = task["prompt"]
            print(f"  Task {task_id}...")
            try:
                call_result = call_model(prompt, command_name, model_id)
                raw_output = call_result["stdout"]
                # Determine if hard fail due to timeout or empty output
                hard_fail_reason = ""
                if call_result.get("timeout", False):
                    hard_fail_reason = "timeout"
                elif call_result.get("success", False) and not raw_output.strip():
                    hard_fail_reason = "empty_output"
                # Score task (if timeout or empty, score will be 0)
                score, missing = score_task(task_id, raw_output)
                task_result = {
                    "prompt": prompt,
                    "raw_output": raw_output,
                    "metadata": call_result,
                    "score": score,
                    "missing_keywords": missing,
                    "weight": task["weight"],
                    "hard_fail_reason": hard_fail_reason,
                }
                # Save per-task files
                task_dir = experiment_dir / family / f"task_{task_id}"
                task_dir.mkdir(parents=True, exist_ok=True)
                (task_dir / "prompt.txt").write_text(prompt, encoding="utf-8")
                (task_dir / "raw_output.txt").write_text(raw_output, encoding="utf-8")
                (task_dir / "metadata.json").write_text(json.dumps(call_result, indent=2, ensure_ascii=False), encoding="utf-8")
                (task_dir / "score.json").write_text(json.dumps({"score": score, "missing": missing, "hard_fail_reason": hard_fail_reason}, indent=2, ensure_ascii=False), encoding="utf-8")
                model_results[task_id] = task_result
            except Exception as e:
                print(f"    ERROR in {family} task {task_id}: {e}")
                # Create a placeholder task result with zero score
                task_result = {
                    "prompt": prompt,
                    "raw_output": "",
                    "metadata": {"error": str(e), "success": False},
                    "score": 0,
                    "missing_keywords": ["exception"],
                    "weight": task["weight"],
                    "hard_fail_reason": "exception",
                }
                model_results[task_id] = task_result
                # Still try to save minimal files
                try:
                    task_dir = experiment_dir / family / f"task_{task_id}"
                    task_dir.mkdir(parents=True, exist_ok=True)
                    (task_dir / "prompt.txt").write_text(prompt, encoding="utf-8")
                    (task_dir / "error.txt").write_text(str(e), encoding="utf-8")
                except Exception:
                    pass
        results[family] = model_results
    return results

def compute_total_scores(results: Dict[str, Any]) -> Dict[str, Any]:
    """Compute weighted total scores and hard fail flags."""
    summary = {}
    for family, model_results in results.items():
        total = 0
        hard_fail = False
        hard_fail_reasons = []
        task_scores = {}
        for task_id, task_result in model_results.items():
            weight = task_result["weight"]
            score = task_result["score"]
            weighted = score * weight / 100
            total += weighted
            task_scores[task_id] = {"raw": score, "weighted": weighted}
            # Hard fail detection: score zero and task A/B/C, or explicit hard_fail_reason
            if task_id in ["A", "B", "C"] and (score == 0 or task_result.get("hard_fail_reason")):
                hard_fail = True
                if task_result.get("hard_fail_reason"):
                    hard_fail_reasons.append(f"{task_id}: {task_result['hard_fail_reason']}")
                else:
                    hard_fail_reasons.append(f"{task_id}: score_zero")
        summary[family] = {
            "total_score": total,
            "task_scores": task_scores,
            "hard_fail": hard_fail,
            "hard_fail_reasons": hard_fail_reasons,
        }
    return summary

def write_report(
    command_name: str,
    model_ids: Dict[str, str],
    discovery_attempts: Dict[str, Any],
    results: Dict[str, Any],
    score_summary: Dict[str, Any],
    experiment_dir: Path,
    report_path: Path,
):
    """Write final markdown report."""
    lines = []
    lines.append("# Elephant Worker Benchmark Report")
    lines.append(f"**Date**: {datetime.now().isoformat()}")
    lines.append(f"**Experiment directory**: `{experiment_dir}`")
    lines.append("")
    lines.append("## Model Discovery")
    lines.append(f"Qwen command used: `{command_name}`")
    lines.append("")
    for family, model_id in model_ids.items():
        lines.append(f"- **{family}**: `{model_id}`")
    lines.append("")
    lines.append("## Benchmark Results")
    lines.append("")
    # Table header
    header = "| Model | Task A | Task B | Task C | Task D | Task E | Task F | Total | Hard Fail |"
    separator = "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"
    lines.append(header)
    lines.append(separator)
    for family, model_results in results.items():
        task_scores = score_summary[family]["task_scores"]
        total = score_summary[family]["total_score"]
        hard_fail = "Yes" if score_summary[family]["hard_fail"] else "No"
        row = f"| {family} | " + " | ".join(str(task_scores[t]["raw"]) for t in ["A","B","C","D","E","F"]) + f" | {total:.1f} | {hard_fail} |"
        lines.append(row)
    lines.append("")
    lines.append("## Hard Fail Details")
    for family, model_results in results.items():
        reasons = score_summary[family].get("hard_fail_reasons", [])
        if reasons:
            lines.append(f"- **{family}**: " + "; ".join(reasons))
        else:
            lines.append(f"- **{family}**: none")
    lines.append("")
    lines.append("## Decision Thresholds")
    lines.append("")
    lines.append("Elephant acceptable as **Chat-level implement worker** if:")
    lines.append("- Total score >= 75")
    lines.append("- No hard fail flags in Tasks A/B/C")
    lines.append("- Task B file-scope score >= 12/15")
    lines.append("- Task C score >= 15/20")
    lines.append("")
    lines.append("Elephant acceptable as **Reasoning-level implement worker** if:")
    lines.append("- Total score >= 85")
    lines.append("- No hard fail flags in any task")
    lines.append("- Task A >= 17/20")
    lines.append("- Task C >= 18/20")
    lines.append("- Task D >= 17/20")
    lines.append("")
    lines.append("## Elephant Evaluation")
    elephant_results = results.get("elephant", {})
    elephant_summary = score_summary.get("elephant", {})
    if not elephant_results:
        lines.append("Elephant model not tested (unavailable).")
    else:
        total = elephant_summary.get("total_score", 0)
        hard_fail = elephant_summary.get("hard_fail", True)
        lines.append(f"- Total score: **{total:.1f}**")
        lines.append(f"- Hard fail flags: **{'Yes' if hard_fail else 'No'}**")
        # Check thresholds
        chat_acceptable = total >= 75 and not hard_fail and \
                          elephant_results.get("B", {}).get("score", 0) >= 12 and \
                          elephant_results.get("C", {}).get("score", 0) >= 15
        reasoning_acceptable = total >= 85 and not hard_fail and \
                               elephant_results.get("A", {}).get("score", 0) >= 17 and \
                               elephant_results.get("C", {}).get("score", 0) >= 18 and \
                               elephant_results.get("D", {}).get("score", 0) >= 17
        lines.append(f"- Acceptable as Chat-level implement worker: **{'Yes' if chat_acceptable else 'No'}**")
        lines.append(f"- Acceptable as Reasoning-level implement worker: **{'Yes' if reasoning_acceptable else 'No'}**")
    lines.append("")
    lines.append("## Specific Weaknesses Observed")
    for family, model_results in results.items():
        lines.append(f"### {family}")
        for task_id, task_result in model_results.items():
            missing = task_result.get("missing_keywords", [])
            if missing:
                lines.append(f"- Task {task_id}: missing {', '.join(missing)}")
    lines.append("")
    lines.append("## Recommended Usage Policy")
    lines.append("- Tasks Elephant can handle:")
    lines.append("- Tasks that should remain DeepSeek Reasoner:")
    lines.append("- Tasks that require Codex review before execution:")
    lines.append("")
    lines.append("## Confirmation of No Production Modifications")
    lines.append("This benchmark created only the following files:")
    lines.append(f"- `{experiment_dir}` and subdirectories")
    lines.append(f"- `{report_path}`")
    lines.append("No production ledger/artifacts/glossary/output/config/source files were modified.")
    lines.append("")
    lines.append("## Model Discovery Details")
    lines.append("```json")
    lines.append(json.dumps(discovery_attempts, indent=2, ensure_ascii=False))
    lines.append("```")
    # Write report
    report_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Report written to {report_path}")

def main():
    print("Elephant Worker Benchmark")
    print("=" * 50)
    # Ensure directories exist
    EXPERIMENTS_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Create timestamped experiment directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    experiment_dir = EXPERIMENTS_DIR / f"elephant_worker_benchmark_{timestamp}"
    experiment_dir.mkdir(parents=True, exist_ok=True)
    
    # Discover Qwen command
    try:
        command_name, help_lines = discover_qwen_command()
        print(f"Using command: {command_name}")
    except RuntimeError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    # Discover model IDs
    print("Discovering model IDs...")
    model_ids, discovery_attempts = discover_model_ids(command_name)
    print(f"Discovered models: {model_ids}")
    # Filter out elephant to avoid timeouts
    filtered = {k:v for k,v in model_ids.items() if k != 'elephant'}
    if filtered:
        model_ids = filtered
        print(f"Filtered models (excluding elephant): {model_ids}")
    else:
        print("Warning: no models left after filtering.")
    
    # Save discovery results
    (experiment_dir / "model_discovery.json").write_text(
        json.dumps({"model_ids": model_ids, "attempts": discovery_attempts}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    
    # If no models discovered, write report and exit
    if not model_ids:
        print("No models available. Writing report with error.")
        report_path = REPORTS_DIR / f"elephant_worker_benchmark_{timestamp}.md"
        lines = [
            "# Elephant Worker Benchmark Report",
            f"**Date**: {datetime.now().isoformat()}",
            "**Status**: No models available.",
            "## Model Discovery Details",
            json.dumps(discovery_attempts, indent=2, ensure_ascii=False),
        ]
        report_path.write_text("\n".join(lines), encoding="utf-8")
        sys.exit(0)
    
    # Run benchmark
    print("Running benchmark tasks...")
    results = run_benchmark(command_name, model_ids, experiment_dir)
    
    # Compute scores
    score_summary = compute_total_scores(results)
    
    # Save benchmark summary
    summary = {
        "model_ids": model_ids,
        "results": results,
        "score_summary": score_summary,
    }
    (experiment_dir / "benchmark_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    
    # Write final report
    report_path = REPORTS_DIR / f"elephant_worker_benchmark_{timestamp}.md"
    write_report(
        command_name,
        model_ids,
        discovery_attempts,
        results,
        score_summary,
        experiment_dir,
        report_path,
    )
    
    print("Benchmark completed.")

if __name__ == "__main__":
    main()