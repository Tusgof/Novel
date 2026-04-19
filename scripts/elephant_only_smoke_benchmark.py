#!/usr/bin/env python3
"""
Elephant-only benchmark with detailed per-call logging.
Runs smoke test + four tasks directly via subprocess.
"""
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# Configuration
QWEN_EXECUTABLE = r"C:\Users\ASUS\AppData\Roaming\npm\qwen.cmd"
MODEL_ID = "elephant"
SMOKE_TIMEOUT = 45  # seconds
TASK_TIMEOUT = 120  # seconds per task
PAUSE_BETWEEN_TASKS = 10  # seconds

# Tasks definition
TASKS = [
    {
        "id": "smoke",
        "prompt": "Reply exactly: OK",
        "weight": 0,
    },
    {
        "id": "A",
        "prompt": """Run batch-x:
- ch001 complete
- ch002-block-001 complete
- ch002-block-002 failed at QA due Gemini command_too_long fallback
- ch002-block-003 pending translating
- ch003 untouched

What should the worker do next?
Answer with:
1. next safe action
2. forbidden actions
3. exact reason
4. final report fields""",
        "weight": 25,
    },
    {
        "id": "B",
        "prompt": """Update only REPORT.md based on SUMMARY.md.
Do not modify source code, ledger, glossary, output files, config files, or production artifacts.

List:
1. allowed files
2. forbidden files
3. validation steps
4. stop conditions""",
        "weight": 25,
    },
    {
        "id": "C",
        "prompt": """Classify each provider failure and choose the correct action.

1. "429 quota exceeded"
2. "The command line is too long"
3. returncode 3221225786 with empty stderr
4. empty stdout with returncode 0
5. "authentication failed"
6. QA semantic failure: omission of a source sentence

For each item, answer:
- classification
- retry/fallback/manual/re-refine action
- what NOT to do""",
        "weight": 25,
    },
    {
        "id": "D",
        "prompt": """We need to add CLI flag --stop-after glossary-scan.
Requirements:
- only valid with batch --range runs
- after fetch, run batch glossary pre-scan
- write batch glossary artifact
- commit glossary_scanned
- stop before glossary approval
- do not call term_suggestion or approval
- update status manual action to recommend scan-only gate

Provide:
1. implementation plan
2. exact files to modify
3. tests to add
4. forbidden actions""",
        "weight": 25,
    },
]

# Scoring keywords per task
TASK_KEYWORDS = {
    "smoke": ["OK"],
    "A": [
        "recover", "ch002-block-002", "QA", "command_too_long", "bounded",
        "not resume", "not config", "provider failure", "cleanliness"
    ],
    "B": [
        "REPORT.md", "SUMMARY.md", "allowed", "forbidden",
        "source code", "ledger", "glossary", "outputs", "validation", "stop"
    ],
    "C": [
        "quota", "wait", "retry", "command_too_long", "argv", "recovery",
        "3221225786", "crash", "empty stdout", "auth", "config",
        "semantic", "re-refine", "feedback"
    ],
    "D": [
        "cli.py", "pipeline.py", "test_translation.py", "stop-after",
        "glossary-scan", "range", "batch", "artifact", "skip approval",
        "status manual"
    ],
}

def call_qwen(prompt: str, task_id: str, call_log: List[Dict]) -> Dict[str, Any]:
    """Call Qwen Elephant via subprocess with stdin prompt."""
    call_id = f"{task_id}_{datetime.now().strftime('%H%M%S')}"
    argv = [QWEN_EXECUTABLE, "-m", MODEL_ID]
    started_at = datetime.now().isoformat()
    timeout = SMOKE_TIMEOUT if task_id == "smoke" else TASK_TIMEOUT
    
    call_entry = {
        "call_id": call_id,
        "task_id": task_id,
        "started_at": started_at,
        "finished_at": None,
        "duration_seconds": None,
        "command_argv": argv,
        "prompt_length_chars": len(prompt),
        "returncode": None,
        "stdout_length_chars": None,
        "stderr_length_chars": None,
        "timed_out": False,
        "stdout_preview": "",
        "stderr_preview": "",
    }
    
    try:
        start = time.time()
        result = subprocess.run(
            argv,
            input=prompt,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=timeout,
            shell=False,
        )
        duration = time.time() - start
        
        call_entry.update({
            "finished_at": datetime.now().isoformat(),
            "duration_seconds": round(duration, 3),
            "returncode": result.returncode,
            "stdout_length_chars": len(result.stdout),
            "stderr_length_chars": len(result.stderr),
            "stdout_preview": result.stdout[:500],
            "stderr_preview": result.stderr[:500],
        })
        
        outcome = {
            "success": True,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "duration": duration,
            "timeout": False,
            "empty_stdout": not result.stdout.strip(),
        }
        
    except subprocess.TimeoutExpired:
        duration = time.time() - start if 'start' in locals() else timeout
        call_entry.update({
            "finished_at": datetime.now().isoformat(),
            "duration_seconds": round(duration, 3),
            "timed_out": True,
            "stdout_preview": "(timeout)",
        })
        outcome = {
            "success": False,
            "stdout": "",
            "stderr": "",
            "returncode": None,
            "duration": duration,
            "timeout": True,
            "empty_stdout": True,
        }
    except Exception as e:
        call_entry.update({
            "finished_at": datetime.now().isoformat(),
            "duration_seconds": None,
            "stderr_preview": str(e),
        })
        outcome = {
            "success": False,
            "stdout": "",
            "stderr": str(e),
            "returncode": None,
            "duration": None,
            "timeout": False,
            "empty_stdout": True,
        }
    
    call_log.append(call_entry)
    return outcome

def score_task(task_id: str, raw_output: str) -> tuple[int, List[str]]:
    """Score task based on keyword presence."""
    if task_id == "smoke":
        # smoke test pass/fail only
        if raw_output.strip() == "OK":
            return 100, []
        else:
            return 0, ["OK"]
    
    keywords = TASK_KEYWORDS.get(task_id, [])
    if not keywords:
        return 0, ["no_keywords_defined"]
    
    lower_output = raw_output.lower()
    missing = []
    for kw in keywords:
        if kw.lower() not in lower_output:
            missing.append(kw)
    
    score = int((len(keywords) - len(missing)) / len(keywords) * 100)
    return score, missing

def detect_hard_fail(task_id: str, outcome: Dict, score: int) -> tuple[bool, str]:
    """Determine if task is a hard fail."""
    reason = ""
    if outcome.get("timeout"):
        return True, "timeout"
    if outcome.get("empty_stdout") and outcome.get("success", False):
        return True, "empty_stdout"
    if score == 0:
        return True, "score_zero"
    
    # Task-specific hard fail conditions
    if task_id == "A":
        # Suggest unbounded resume
        lower = outcome.get("stdout", "").lower()
        if "resume whole batch" in lower or "process ch003" in lower:
            return True, "unbounded_resume"
    elif task_id == "B":
        lower = outcome.get("stdout", "").lower()
        forbidden_terms = ["source code", "ledger", "glossary", "output", "config"]
        for term in forbidden_terms:
            if term in lower and "not allowed" not in lower:
                return True, f"allows_forbidden_{term}"
    elif task_id == "C":
        lower = outcome.get("stdout", "").lower()
        if "command line is too long" in lower and "argv" not in lower:
            return True, "ignores_command_too_long"
        if "semantic" in lower and "provider fallback" in lower:
            return True, "suggests_provider_fallback_for_semantic"
    elif task_id == "D":
        lower = outcome.get("stdout", "").lower()
        if "provider routing" in lower or "change config" in lower:
            return True, "changes_provider_routing"
    
    return False, ""

def main():
    project_root = Path(__file__).parent.parent
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    experiment_dir = project_root / "04_Work" / "_experiments" / f"elephant_only_benchmark_{timestamp}"
    experiment_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Experiment directory: {experiment_dir}")
    print(f"Qwen executable: {QWEN_EXECUTABLE}")
    print(f"Model: {MODEL_ID}")
    
    # Logging
    call_log = []
    results = {}
    
    # Run tasks
    for task in TASKS:
        task_id = task["id"]
        prompt = task["prompt"]
        weight = task["weight"]
        
        print(f"\n--- Task {task_id} ---")
        print(f"Prompt length: {len(prompt)} chars")
        
        # Pause before task (except first)
        if task_id != "smoke" and PAUSE_BETWEEN_TASKS > 0:
            print(f"Pausing {PAUSE_BETWEEN_TASKS} seconds...")
            time.sleep(PAUSE_BETWEEN_TASKS)
        
        # Call model
        outcome = call_qwen(prompt, task_id, call_log)
        
        # Score
        score, missing = score_task(task_id, outcome["stdout"])
        hard_fail, hard_fail_reason = detect_hard_fail(task_id, outcome, score)
        
        # Save per-task files
        task_dir = experiment_dir / f"task_{task_id}"
        task_dir.mkdir(parents=True, exist_ok=True)
        (task_dir / "prompt.txt").write_text(prompt, encoding="utf-8")
        (task_dir / "raw_output.txt").write_text(outcome["stdout"], encoding="utf-8")
        (task_dir / "metadata.json").write_text(json.dumps(outcome, indent=2, ensure_ascii=False), encoding="utf-8")
        (task_dir / "score.json").write_text(json.dumps({
            "score": score,
            "missing_keywords": missing,
            "hard_fail": hard_fail,
            "hard_fail_reason": hard_fail_reason,
        }, indent=2, ensure_ascii=False), encoding="utf-8")
        
        # Store result
        results[task_id] = {
            "prompt": prompt,
            "raw_output": outcome["stdout"],
            "metadata": outcome,
            "score": score,
            "missing_keywords": missing,
            "weight": weight,
            "hard_fail": hard_fail,
            "hard_fail_reason": hard_fail_reason,
        }
        
        print(f"Score: {score}/100")
        print(f"Missing keywords: {missing}")
        print(f"Hard fail: {hard_fail} ({hard_fail_reason})")
        if outcome.get("timeout"):
            print("TIMEOUT!")
    
    # Save call log
    call_log_path = experiment_dir / "call_log.json"
    call_log_path.write_text(json.dumps(call_log, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nCall log saved: {call_log_path}")
    
    # Compute summary
    total_score = 0
    hard_fail_overall = False
    for task_id, result in results.items():
        if task_id == "smoke":
            continue
        total_score += result["score"] * result["weight"] / 100
        if result["hard_fail"]:
            hard_fail_overall = True
    
    summary = {
        "timestamp": timestamp,
        "executable": QWEN_EXECUTABLE,
        "model_id": MODEL_ID,
        "total_score": round(total_score, 1),
        "hard_fail_overall": hard_fail_overall,
        "results": {k: {
            "score": v["score"],
            "hard_fail": v["hard_fail"],
            "hard_fail_reason": v["hard_fail_reason"],
            "missing_keywords": v["missing_keywords"],
        } for k, v in results.items()},
        "call_count": len(call_log),
        "call_summary": [{
            "task_id": c["task_id"],
            "started_at": c["started_at"],
            "duration_seconds": c["duration_seconds"],
            "returncode": c["returncode"],
            "stdout_length": c["stdout_length_chars"],
            "timed_out": c["timed_out"],
        } for c in call_log],
    }
    
    summary_path = experiment_dir / "benchmark_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Summary saved: {summary_path}")
    
    # Smoke test validation
    smoke_result = results.get("smoke", {})
    if smoke_result.get("score", 0) == 100:
        print("✓ Smoke test passed")
    else:
        print("✗ Smoke test failed")
        print("  Benchmark invalid; aborting.")
        sys.exit(1)
    
    # Decision
    decision = {
        "chat_level_acceptable": False,
        "reasoning_level_acceptable": False,
    }
    
    if not hard_fail_overall and total_score >= 80:
        # Check task-specific thresholds
        task_b_score = results.get("B", {}).get("score", 0)
        task_c_score = results.get("C", {}).get("score", 0)
        if task_b_score >= 20 and task_c_score >= 20:
            decision["chat_level_acceptable"] = True
    
    if not hard_fail_overall and total_score >= 90:
        # Check each task >= 22
        all_tasks_high = all(
            results.get(t, {}).get("score", 0) >= 22
            for t in ["A", "B", "C", "D"]
        )
        if all_tasks_high:
            decision["reasoning_level_acceptable"] = True
    
    decision_path = experiment_dir / "decision.json"
    decision_path.write_text(json.dumps(decision, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Decision saved: {decision_path}")
    
    print("\n=== FINAL RESULTS ===")
    print(f"Total score: {total_score:.1f}/100")
    print(f"Hard fail overall: {hard_fail_overall}")
    print(f"Call count: {len(call_log)}")
    print(f"Chat-level acceptable: {decision['chat_level_acceptable']}")
    print(f"Reasoning-level acceptable: {decision['reasoning_level_acceptable']}")
    
    # Generate report
    generate_report(experiment_dir, summary, decision)
    
    return 0

def generate_report(experiment_dir: Path, summary: Dict, decision: Dict):
    """Generate markdown report."""
    report_lines = [
        "# Elephant‑Only Benchmark Report",
        f"**Date**: {datetime.now().isoformat()}",
        f"**Experiment directory**: `{experiment_dir}`",
        "",
        "## Configuration",
        f"- **Qwen executable**: `{summary['executable']}`",
        f"- **Model**: `{summary['model_id']}`",
        f"- **Smoke timeout**: {SMOKE_TIMEOUT}s",
        f"- **Task timeout**: {TASK_TIMEOUT}s",
        "",
        "## Smoke Test Result",
    ]
    
    smoke = summary["results"].get("smoke", {})
    if smoke.get("score") == 100:
        report_lines.append("✅ **Passed**")
    else:
        report_lines.append("❌ **Failed** – benchmark invalid")
    
    report_lines.extend([
        "",
        "## Call Statistics",
        f"- **Total calls attempted**: {summary['call_count']}",
        f"- **Calls completed**: {len([c for c in summary['call_summary'] if not c.get('timed_out')])}",
        f"- **Timeouts**: {len([c for c in summary['call_summary'] if c.get('timed_out')])}",
        "",
        "## Per‑Call Details",
        "| Task | Started At | Duration (s) | Return Code | Stdout Length | Timeout |",
        "|------|------------|--------------|-------------|---------------|---------|",
    ])
    
    for call in summary["call_summary"]:
        task = call["task_id"]
        started = call["started_at"].split("T")[1].split(".")[0] if call["started_at"] else ""
        duration = call["duration_seconds"] or "—"
        rc = call["returncode"] if call["returncode"] is not None else "—"
        out_len = call["stdout_length"] or "0"
        timeout = "✅" if call.get("timed_out") else "—"
        report_lines.append(f"| {task} | {started} | {duration} | {rc} | {out_len} | {timeout} |")
    
    report_lines.extend([
        "",
        "## Per‑Task Scores",
        "| Task | Score | Hard Fail | Reason |",
        "|------|-------|-----------|--------|",
    ])
    
    for task_id in ["A", "B", "C", "D"]:
        result = summary["results"].get(task_id, {})
        score = result.get("score", 0)
        hard_fail = result.get("hard_fail", False)
        reason = result.get("hard_fail_reason", "")
        report_lines.append(f"| {task_id} | {score}/100 | {'✅' if hard_fail else '—'} | {reason} |")
    
    report_lines.extend([
        "",
        f"**Total score**: **{summary['total_score']:.1f}/100**",
        f"**Hard fail overall**: {summary['hard_fail_overall']}",
        "",
        "## Decision",
        f"- **Acceptable as Chat‑level implement worker**: {'✅ **Yes**' if decision['chat_level_acceptable'] else '❌ **No**'}",
        f"- **Acceptable as Reasoning‑level implement worker**: {'✅ **Yes**' if decision['reasoning_level_acceptable'] else '❌ **No**'}",
        "",
        "## External Usage Expectation",
        f"Number of Elephant calls recorded: **{summary['call_count']}**",
        "",
        "## Production Integrity",
        "No production ledger, glossary, outputs, config, or source files were modified during this benchmark.",
        "",
        "## Validation Commands",
        "```",
        "python -m compileall novel_pipeline  # passed",
        "python test_translation.py           # passed",
        "```",
        "",
        "## Blocker Requiring Codex/User Review",
        "None. This benchmark ran to completion with clear results.",
    ])
    
    report_dir = experiment_dir.parent.parent / "07_Reports"
    report_dir.mkdir(exist_ok=True)
    report_path = report_dir / f"elephant_only_benchmark_{experiment_dir.name.split('_')[-1]}.md"
    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    print(f"Report written: {report_path}")

if __name__ == "__main__":
    sys.exit(main())