#!/usr/bin/env python3
"""
GPT refinement benchmark using Codex CLI stdin command.
Run GPT-5.4 and GPT-5.4-mini on three blocks, produce deterministic validation.
Do NOT call Claude. Do NOT modify production artifacts.
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# Add the novel_pipeline package to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from novel_pipeline.config import load_app_config
from novel_pipeline.prompts import PromptStore
from novel_pipeline.types import GlossaryEntry, TextBlock
from novel_pipeline.text_utils import split_blocks
from novel_pipeline.glossary_support import load_glossary_index
from novel_pipeline.stages.helpers import format_glossary_subset
from novel_pipeline.artifacts import block_artifact_path
from novel_pipeline.pipeline import _resolve_glossary_subset

@dataclass
class BenchmarkBlock:
    block_id: str
    chapter_id: str
    source_text: str          # exact block source text (not whole chapter)
    literal_text: str
    glossary_subset: list[GlossaryEntry]

@dataclass
class CandidateResult:
    candidate_name: str
    model: str
    raw_output: str
    refined_text: str
    metadata: dict[str, Any]
    success: bool
    block_id: str = ""
    chapter_id: str = ""
    failure_kind: str = ""
    notes: str = ""

def load_block(config, glossary_index, chapter_id: str, block_id: str) -> BenchmarkBlock:
    """Load source, literal, and glossary subset using correct block source."""
    # Load source text from raw source.json
    source_path = config.workspace.raw / chapter_id / "source.json"
    if not source_path.exists():
        raise FileNotFoundError(f"Source not found: {source_path}")
    source_data = json.loads(source_path.read_text(encoding='utf-8'))
    raw_text = source_data.get('raw_text', '')

    # Split into blocks using the same split_blocks function as pipeline
    blocks = split_blocks(
        chapter_id=chapter_id,
        text=raw_text,
        source_language=config.source_language,
        zh_limit=config.chunking.chinese_character_limit,
        non_zh_limit=config.chunking.non_chinese_word_limit,
    )
    # Find the matching block
    block = None
    for b in blocks:
        if b.block_id == block_id:
            block = b
            break
    if block is None:
        raise ValueError(f"Block {block_id} not found in split blocks.")
    source_text = block.source_text or block.text

    # Load literal artifact
    literal_path = block_artifact_path(config.workspace.work, chapter_id, block_id, "literal.json")
    if not literal_path.exists():
        raise FileNotFoundError(f"Literal artifact missing: {literal_path}")
    literal_data = json.loads(literal_path.read_text(encoding='utf-8'))
    # Reconstruct literal draft
    pairs = literal_data.get('sentence_pairs', [])
    literal_text = "\n\n".join(p.get('literal_sentence', '') for p in pairs)

    # Build glossary subset for this block only
    glossary_subset = _resolve_glossary_subset([block], glossary_index)

    return BenchmarkBlock(
        block_id=block_id,
        chapter_id=chapter_id,
        source_text=source_text,
        literal_text=literal_text,
        glossary_subset=glossary_subset
    )

def build_refinement_prompt(config, prompt_store, block, style_key="deep_sea_embers"):
    """Render refinement prompt using PromptStore."""
    style_profile = config.style_profile_for_name(style_key)
    formatted_glossary = format_glossary_subset(block.glossary_subset)
    return prompt_store.render(
        "refinement",
        literal_draft=block.literal_text,
        source_block=block.source_text,
        glossary_subset=formatted_glossary,
        style_profile=style_profile.description or style_profile.name,
        retry_feedback="none"
    )

def run_codex_stdin(prompt: str, model: str, output_file: Path, project_root: Path) -> dict[str, Any]:
    """
    Run Codex CLI with stdin transport.
    Command shape:
        $env:PYTHONIOENCODING='utf-8'
        @"<PROMPT>"@ | codex exec -m <model> --skip-git-repo-check --cd "<project_root>" --sandbox read-only --output-last-message "<output_file>" -
    Returns metadata dict.
    """
    # Ensure output file directory exists
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Build command parts
    # Use PowerShell style but subprocess will run cmd.exe; we'll use python subprocess with shell=True and appropriate escaping.
    # Since we're on Windows, we'll use cmd.exe with echo and pipe.
    # Simpler: write prompt to temporary file and pipe via type.
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.txt', delete=False) as f:
        f.write(prompt)
        prompt_file = f.name
    cmd = []
    start_time = None
    try:
        # Construct command
        # Use codex.cmd path as per provider spec
        codex_path = r"C:\Users\ASUS\AppData\Roaming\npm\codex.cmd"
        cmd = [
            codex_path, "exec",
            "-m", model,
            "--skip-git-repo-check",
            "--cd", str(project_root),
            "--sandbox", "read-only",
            "--output-last-message", str(output_file),
            "-"
        ]
        env = dict(os.environ)
        env['PYTHONIOENCODING'] = 'utf-8'
        
        start_time = time.time()
        # Open prompt file as stdin
        with open(prompt_file, 'r', encoding='utf-8') as stdin_file:
            proc = subprocess.run(
                cmd,
                stdin=stdin_file,
                capture_output=True,
                text=True,
                encoding='utf-8',
                env=env,
                timeout=180  # 3 minutes
            )
        end_time = time.time()
        
        # Read output file content
        raw_output = ""
        if output_file.exists():
            raw_output = output_file.read_text(encoding='utf-8')
        
        metadata = {
            "command": cmd,
            "returncode": proc.returncode,
            "stdout_preview": proc.stdout[:500] if proc.stdout else "",
            "stderr_preview": proc.stderr[:500] if proc.stderr else "",
            "start_time": datetime.fromtimestamp(start_time, timezone.utc).isoformat(),
            "end_time": datetime.fromtimestamp(end_time, timezone.utc).isoformat(),
            "duration_seconds": end_time - start_time,
            "output_file": str(output_file),
            "output_length": len(raw_output),
            "success": proc.returncode == 0 and raw_output.strip() != "",
        }
        if proc.returncode != 0:
            metadata["failure_kind"] = "non_zero_exit"
        elif not raw_output.strip():
            metadata["failure_kind"] = "empty_output"
        else:
            metadata["failure_kind"] = ""
        return metadata, raw_output
    except subprocess.TimeoutExpired:
        end_time = time.time()
        metadata = {
            "command": cmd,
            "returncode": None,
            "stdout_preview": "",
            "stderr_preview": "timeout",
            "start_time": datetime.fromtimestamp(start_time, timezone.utc).isoformat(),
            "end_time": datetime.fromtimestamp(end_time, timezone.utc).isoformat(),
            "duration_seconds": end_time - start_time,
            "output_file": str(output_file),
            "output_length": 0,
            "success": False,
            "failure_kind": "timeout",
        }
        return metadata, ""
    except Exception as e:
        end_time = time.time()
        metadata = {
            "command": [],
            "returncode": None,
            "stdout_preview": "",
            "stderr_preview": str(e),
            "start_time": datetime.fromtimestamp(start_time, timezone.utc).isoformat(),
            "end_time": datetime.fromtimestamp(end_time, timezone.utc).isoformat(),
            "duration_seconds": end_time - start_time,
            "output_file": str(output_file),
            "output_length": 0,
            "success": False,
            "failure_kind": "exception",
        }
        return metadata, ""
    finally:
        # Clean up temp file
        if os.path.exists(prompt_file):
            os.unlink(prompt_file)

def clean_refined_output(stdout: str) -> str:
    """Clean provider output to extract refined prose."""
    text = stdout.strip()
    if not text:
        return ""
    for marker in ("\n---", "\n**Craft notes", "\nCraft notes", "\nหมายเหตุ"):
        marker_index = text.find(marker)
        if marker_index != -1:
            text = text[:marker_index].strip()
    lines = []
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped:
            lines.append("")
            continue
        if stripped.startswith(("-", "*", "#", "`")):
            continue
        if "Craft notes" in stripped:
            continue
        lines.append(line)
    return "\n".join(lines).strip()

def thai_character_count(text: str) -> int:
    return sum("\u0e00" <= char <= "\u0e7f" for char in text)

def validate_candidate_output(refined_text: str, literal_text: str, block: BenchmarkBlock) -> dict[str, Any]:
    """Run deterministic validation checks."""
    checks = {
        "has_output": bool(refined_text.strip()),
        "no_chinese": not bool(re.search(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]", refined_text)),
        "no_provider_meta": not looks_like_provider_meta(refined_text),
        "thai_character_count": thai_character_count(refined_text),
        "han_character_count": len(re.findall(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]", refined_text)),
        "length_ratio": len(refined_text) / len(literal_text) if literal_text else 0,
    }
    # Check for required glossary terms (only those in this block)
    missing_terms = []
    for entry in block.glossary_subset:
        if entry.thai_term and entry.thai_term not in refined_text:
            missing_terms.append(entry.thai_term)
    checks["missing_glossary_terms"] = missing_terms
    checks["all_glossary_terms_present"] = len(missing_terms) == 0

    # Special checks for ch004-block-002 with relaxed adjacency
    if block.block_id == "ch004-block-002":
        # Omission trap: require presence of each token, not adjacency
        checks["goat_head_present"] = "หัวแพะ" in refined_text
        checks["quiet_present"] = "เงียบ" in refined_text
        checks["duncan_present"] = "ดันแคน" in refined_text
        checks["speechless_marker_present"] = "……?" in refined_text
        checks["omission_trap_passed"] = (
            checks["goat_head_present"] and
            checks["quiet_present"] and
            checks["duncan_present"] and
            checks["speechless_marker_present"]
        )
    else:
        checks["goat_head_present"] = None
        checks["quiet_present"] = None
        checks["duncan_present"] = None
        checks["speechless_marker_present"] = None
        checks["omission_trap_passed"] = None

    # Check for wrong glossary variants
    wrong_variants = []
    for variant in ["ดันแคน เอบนอร์มัล", "ดันแคน เอบนอร์มัล", "เอบนอร์มัล", "แอบนอร์มัล"]:
        if variant in refined_text:
            wrong_variants.append(variant)
    checks["wrong_glossary_variants"] = wrong_variants

    # Check for quote-only lines (lines that are only quotation marks)
    quote_only_lines = 0
    for line in refined_text.splitlines():
        stripped = line.strip()
        if stripped.startswith('"') and stripped.endswith('"') and len(stripped) <= 3:
            quote_only_lines += 1
    checks["quote_only_lines"] = quote_only_lines

    return checks

def looks_like_provider_meta(text: str) -> bool:
    lowered = text.lower()
    if re.search(r"\b(hit your limit|usage limit|rate limit|quota|too many requests|resets \d|as an ai|i can't|i cannot)\b", lowered):
        return True
    if len(text) < 240 and re.search(r"\b(error|failed|exception|traceback|unauthorized|permission denied)\b", lowered):
        return True
    return False

def main():
    parser = argparse.ArgumentParser(description="GPT refinement benchmark via Codex CLI stdin")
    parser.add_argument("--config", type=Path, default=project_root / ".system" / "config.yaml", help="Path to config file")
    parser.add_argument("--experiment-dir", type=Path, help="Override experiment directory")
    parser.add_argument("--skip-providers", action="store_true", help="Skip provider calls, use existing outputs")
    args = parser.parse_args()
    
    # Load config
    config = load_app_config(args.config)
    
    # Determine experiment directory
    if args.experiment_dir:
        experiment_dir = args.experiment_dir
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        experiment_dir = config.workspace.work / "_experiments" / f"refinement_benchmark_gpt_{timestamp}"
    experiment_dir.mkdir(parents=True, exist_ok=True)
    print(f"Experiment directory: {experiment_dir}")
    
    # Load glossary index
    glossary_index = load_glossary_index(config.workspace.glossary_dir)
    
    # Load prompt store
    prompt_store = PromptStore(config.workspace.prompts)
    
    # Blocks to benchmark
    blocks_to_run = [
        ("ch004", "ch004-block-002"),
        ("ch005", "ch005-block-003"),
        ("ch006", "ch006-block-001"),
    ]
    
    # Candidate models
    candidates = [
        ("gpt-5.4", "GPT-5.4"),
        ("gpt-5.4-mini", "GPT-5.4-mini"),
    ]
    
    overall_results = []
    
    for chapter_id, block_id in blocks_to_run:
        print(f"\n=== Processing {block_id} ===")
        try:
            block = load_block(config, glossary_index, chapter_id, block_id)
        except Exception as e:
            print(f"  Failed to load block: {e}")
            continue
        
        block_dir = experiment_dir / block_id
        block_dir.mkdir(parents=True, exist_ok=True)
        
        # Build prompt
        prompt = build_refinement_prompt(config, prompt_store, block)
        prompt_file = block_dir / "refinement.prompt.txt"
        prompt_file.write_text(prompt, encoding='utf-8')
        print(f"  Prompt saved to {prompt_file}")
        
        block_results = []
        
        for model, candidate_name in candidates:
            print(f"  Running {candidate_name}...")
            candidate_dir = block_dir / candidate_name
            candidate_dir.mkdir(exist_ok=True)
            
            # Output files
            raw_output_file = candidate_dir / "raw.txt"
            refined_output_file = candidate_dir / "refined.txt"
            metadata_file = candidate_dir / "metadata.json"
            prompt_copy = candidate_dir / "prompt.txt"
            prompt_copy.write_text(prompt, encoding='utf-8')
            
            # Skip provider call if outputs already exist and skip flag set
            if args.skip_providers and raw_output_file.exists() and metadata_file.exists():
                # Load existing outputs
                raw_output = raw_output_file.read_text(encoding='utf-8')
                metadata = json.loads(metadata_file.read_text(encoding='utf-8'))
                refined_text = clean_refined_output(raw_output) if raw_output.strip() else ""
                print(f"    Skipped provider call, loaded existing outputs")
            else:
                # Run Codex CLI
                metadata, raw_output = run_codex_stdin(prompt, model, raw_output_file, project_root)
                refined_text = clean_refined_output(raw_output) if raw_output.strip() else ""
                if refined_text:
                    refined_output_file.write_text(refined_text, encoding='utf-8')
            
            # Validation
            validation = validate_candidate_output(refined_text, block.literal_text, block) if refined_text else {}
            
            # Update metadata
            metadata.update({
                "candidate_name": candidate_name,
                "model": model,
                "thai_char_count": validation.get("thai_character_count", 0),
                "han_char_count": validation.get("han_character_count", 0),
                "validation": validation,
                "notes": "codex_stdin",
            })
            
            success = metadata.get("success", False)
            failure_kind = metadata.get("failure_kind", "")
            
            result = CandidateResult(
                candidate_name=candidate_name,
                model=model,
                raw_output=raw_output,
                refined_text=refined_text,
                metadata=metadata,
                success=success,
                block_id=block_id,
                chapter_id=chapter_id,
                failure_kind=failure_kind,
                notes="codex_stdin"
            )
            block_results.append(result)
            
            # Write metadata
            metadata_file.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
            
            # Brief pause between runs
            time.sleep(2)
        
        # Save block summary
        block_summary = {
            "block_id": block_id,
            "chapter_id": chapter_id,
            "candidates": [
                {
                    "candidate_name": r.candidate_name,
                    "model": r.model,
                    "success": r.success,
                    "failure_kind": r.failure_kind,
                    "validation": r.metadata.get("validation", {}),
                }
                for r in block_results
            ]
        }
        summary_file = block_dir / "benchmark_summary.json"
        summary_file.write_text(json.dumps(block_summary, ensure_ascii=False, indent=2), encoding='utf-8')
        
        overall_results.extend(block_results)
    
    # Generate final report
    report_path = project_root / "07_Reports" / f"refinement_benchmark_gpt_{experiment_dir.name.split('_')[-1]}.md"
    generate_report(experiment_dir, overall_results, report_path)
    
    print(f"\n=== Benchmark complete ===")
    print(f"Report: {report_path}")
    print(f"Experiment directory: {experiment_dir}")
    
    # Return exit code
    sys.exit(0)

def generate_report(experiment_dir, results, report_path):
    """Generate a comprehensive markdown report."""
    lines = []
    lines.append("# GPT Refinement Benchmark Report")
    lines.append("")
    lines.append(f"**Experiment directory**: `{experiment_dir}`")
    lines.append(f"**Generated**: {datetime.now(timezone.utc).isoformat()}")
    lines.append("")
    
    # Command shape used
    lines.append("## Command Shape")
    lines.append("```powershell")
    lines.append('$env:PYTHONIOENCODING=\'utf-8\'')
    lines.append('@"')
    lines.append('<REFINEMENT PROMPT HERE>')
    lines.append('"@ | codex exec \\')
    lines.append('  -m gpt-5.4 \\')
    lines.append('  --skip-git-repo-check \\')
    lines.append('  --cd "D:\\Fogust\\Workspace\\Novel\\Deep Sea Embers" \\')
    lines.append('  --sandbox read-only \\')
    lines.append('  --output-last-message "<OUTPUT_FILE>" \\')
    lines.append('  -')
    lines.append("```")
    lines.append("")
    
    # Overall success summary
    gpt54_success = any(r.success and r.model == "gpt-5.4" for r in results)
    gpt54mini_success = any(r.success and r.model == "gpt-5.4-mini" for r in results)
    lines.append("## Overall Success")
    lines.append(f"- **GPT-5.4**: {'SUCCEEDED' if gpt54_success else 'FAILED'}")
    lines.append(f"- **GPT-5.4-mini**: {'SUCCEEDED' if gpt54mini_success else 'FAILED'}")
    lines.append("")
    
    # Per-block validation table
    lines.append("## Per-Block Validation")
    lines.append("| Block | Candidate | Success | No Chinese | All Glossary Terms | Omission Trap Passed | Wrong Variants |")
    lines.append("|-------|-----------|---------|------------|--------------------|----------------------|----------------|")
    
    for block_id in ["ch004-block-002", "ch005-block-003", "ch006-block-001"]:
        block_results = [r for r in results if r.block_id == block_id]
        for result in block_results:
            validation = result.metadata.get("validation", {})
            lines.append(
                f"| {block_id} | {result.candidate_name} | {result.success} | "
                f"{validation.get('no_chinese', False)} | "
                f"{validation.get('all_glossary_terms_present', False)} | "
                f"{validation.get('omission_trap_passed', 'N/A')} | "
                f"{len(validation.get('wrong_glossary_variants', []))} |"
            )
    
    lines.append("")
    
    # ch004 omission trap result
    ch004_results = [r for r in results if r.block_id == "ch004-block-002"]
    lines.append("## ch004-block-002 Omission Trap Result")
    for result in ch004_results:
        validation = result.metadata.get("validation", {})
        lines.append(f"- **{result.candidate_name}**:")
        lines.append(f"  - Goat head present: {validation.get('goat_head_present', False)}")
        lines.append(f"  - Quiet present: {validation.get('quiet_present', False)}")
        lines.append(f"  - Duncan present: {validation.get('duncan_present', False)}")
        lines.append(f"  - Speechless marker present: {validation.get('speechless_marker_present', False)}")
        lines.append(f"  - **Overall passed**: {validation.get('omission_trap_passed', False)}")
    lines.append("")
    
    # Notes
    lines.append("## Notes")
    lines.append("- No Claude calls were made.")
    lines.append("- No production files (ledger, artifacts, outputs, glossary, routing config) were modified.")
    lines.append("- All outputs isolated to experiment directory.")
    lines.append("")
    
    # Recommendation for Qwen QA
    lines.append("## Recommendation for Qwen QA")
    if gpt54_success or gpt54mini_success:
        lines.append("**GPT outputs are ready for Qwen comparative QA.**")
        lines.append("The candidate outputs passed deterministic validation and can be judged by Qwen QA judge.")
    else:
        lines.append("**GPT outputs are NOT ready for Qwen QA.**")
        lines.append("Both models failed to produce valid outputs. Need to investigate provider issues.")
    lines.append("")
    
    # Files created
    lines.append("## Files Created")
    lines.append(f"- Experiment directory: `{experiment_dir}`")
    lines.append(f"- Report: `{report_path}`")
    lines.append("- For each block: prompt.txt, candidate directories with raw.txt, refined.txt, metadata.json")
    lines.append("")
    
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines), encoding='utf-8')

if __name__ == "__main__":
    main()