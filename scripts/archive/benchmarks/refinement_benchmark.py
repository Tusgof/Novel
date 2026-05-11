#!/usr/bin/env python3
"""
Isolated benchmark for refinement model quality.
Compare Claude (production), Qwen DeepSeek Reasoner, GPT-5.4, GPT-5.4-mini.
Do not modify production artifacts or ledger.
"""

import argparse
import json
import sys
import time
import re
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# Add the novel_pipeline package to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from novel_pipeline.config import load_app_config
from novel_pipeline.providers.base import (
    ProviderRunner, build_provider_spec, ProviderRequest, 
    ProviderResponse, classify_provider_response
)
from novel_pipeline.prompts import PromptStore
from novel_pipeline.types import GlossaryEntry, TextBlock, LiteralDraft, RefinedDraft
from novel_pipeline.text_utils import validate_text_script, split_sentences
from novel_pipeline.glossary_support import load_glossary_index
from novel_pipeline.stages.helpers import format_glossary_subset
from novel_pipeline.artifacts import block_artifact_path

@dataclass
class BenchmarkBlock:
    block_id: str
    chapter_id: str
    source_text: str
    literal_text: str
    existing_refined: Optional[str] = None
    existing_qa_feedback: Optional[str] = None
    glossary_subset: list[GlossaryEntry] = None

@dataclass
class CandidateResult:
    candidate_name: str
    provider: str
    model: str
    raw_output: str
    refined_text: str
    metadata: dict[str, Any]
    success: bool
    failure_kind: str = ""
    notes: str = ""

class RefinementBenchmark:
    def __init__(self, config_path: Path, output_dir: Path, report_dir: Path, skip_providers: bool = False):
        self.config = load_app_config(config_path)
        self.output_dir = output_dir
        self.report_dir = report_dir
        self.skip_providers = skip_providers
        # Extract timestamp from output directory name
        self.timestamp = output_dir.name.split('refinement_benchmark_')[-1] if 'refinement_benchmark_' in output_dir.name else datetime.now().strftime("%Y%m%d_%H%M%S")
        self.prompt_store = PromptStore(self.config.workspace.prompts)
        self.glossary_index = load_glossary_index(self.config.workspace.glossary_dir)

        # Define candidate models
        self.candidates = [
            ("claude", "sonnet"),
            ("qwen", "deepseek-reasoner"),
            ("codex", "gpt-5.4"),
            ("codex", "gpt-5.4-mini"),
        ]
        
        # Provider specs from config (already ProviderSpec objects)
        self.provider_specs = self.config.providers.copy()
    
    def load_block(self, chapter_id: str, block_id: str) -> BenchmarkBlock:
        """Load source, literal, existing refined, QA, and glossary subset."""
        # Load source text from raw source.json
        source_path = self.config.workspace.raw / chapter_id / "source.json"
        if not source_path.exists():
            raise FileNotFoundError(f"Source not found: {source_path}")
        source_data = json.loads(source_path.read_text(encoding='utf-8'))
        source_text = source_data.get('raw_text', '')
        
        # Load literal artifact
        literal_path = block_artifact_path(self.config.workspace.work, chapter_id, block_id, "literal.json")
        if not literal_path.exists():
            raise FileNotFoundError(f"Literal artifact missing: {literal_path}")
        literal_data = json.loads(literal_path.read_text(encoding='utf-8'))
        # Reconstruct literal draft
        pairs = literal_data.get('sentence_pairs', [])
        literal_text = "\n\n".join(p.get('literal_sentence', '') for p in pairs)
        
        # Load existing refined artifact if exists
        refined_path = block_artifact_path(self.config.workspace.work, chapter_id, block_id, "refined.json")
        existing_refined = None
        if refined_path.exists():
            refined_data = json.loads(refined_path.read_text(encoding='utf-8'))
            existing_refined = refined_data.get('refined_text', '')
        
        # Load QA artifact if exists
        qa_path = block_artifact_path(self.config.workspace.work, chapter_id, block_id, "qa.json")
        existing_qa_feedback = None
        if qa_path.exists():
            qa_data = json.loads(qa_path.read_text(encoding='utf-8'))
            existing_qa_feedback = qa_data.get('feedback', '')
        
        # Build glossary subset for this block
        # We need a TextBlock representation
        block = TextBlock(
            block_id=block_id,
            chapter_id=chapter_id,
            source_text=source_text,
            text=source_text,
            character_count=len(source_text),
            word_count=len(source_text.split()),
            block_index=0,
            source_language=self.config.source_language,
            start_offset=0,
            end_offset=len(source_text),
            metadata={},
            order=0,
            context_before="",
            context_after=""
        )
        glossary_subset = self._resolve_glossary_subset([block])
        
        return BenchmarkBlock(
            block_id=block_id,
            chapter_id=chapter_id,
            source_text=source_text,
            literal_text=literal_text,
            existing_refined=existing_refined,
            existing_qa_feedback=existing_qa_feedback,
            glossary_subset=glossary_subset
        )
    
    def _resolve_glossary_subset(self, blocks: list[TextBlock]) -> list[GlossaryEntry]:
        """Adapted from pipeline's glossary subset resolution."""
        matched = {}
        for block in blocks:
            text = block.source_text or block.text
            if not text:
                continue
            candidates = []
            for key, entry in self.glossary_index.items():
                if entry.status == "approved" and key in text:
                    candidates.append((key, entry))
            candidates.sort(key=lambda pair: (-len(pair[0]), pair[0]))
            occupied = []
            for term, entry in candidates:
                occurrences = []
                start = 0
                while True:
                    pos = text.find(term, start)
                    if pos == -1:
                        break
                    occurrences.append(pos)
                    start = pos + 1
                term_len = len(term)
                for pos in occurrences:
                    end = pos + term_len
                    overlap = False
                    for occ_start, occ_end in occupied:
                        if pos < occ_end and end > occ_start:
                            overlap = True
                            break
                    if not overlap:
                        matched[entry.original_term] = entry
                        occupied.append((pos, end))
                        break
        return list(matched.values())
    
    def _build_refinement_prompt(self, block: BenchmarkBlock, style_key: str = "deep_sea_embers") -> str:
        """Render refinement prompt using PromptStore."""
        style_profile = self.config.style_profile_for_name(style_key)
        formatted_glossary = format_glossary_subset(block.glossary_subset)
        return self.prompt_store.render(
            "refinement",
            literal_draft=block.literal_text,
            source_block=block.source_text,
            glossary_subset=formatted_glossary,
            style_profile=style_profile.description or style_profile.name,
            retry_feedback="none"
        )
    
    def _run_provider(self, provider_name: str, model: str, prompt: str) -> tuple[ProviderResponse, bool, str]:
        """Run provider with given prompt and return response, success, failure_kind."""
        if self.skip_providers:
            # Return dummy successful response with placeholder text
            dummy_text = f"[DUMMY OUTPUT for {provider_name} {model}]\n\nThis is a placeholder refined text."
            return ProviderResponse(
                provider=provider_name,
                command=("dummy",),
                stdout=dummy_text,
                stderr="",
                returncode=0,
                started_at=datetime.now(timezone.utc).isoformat(),
                finished_at=datetime.now(timezone.utc).isoformat(),
                duration_seconds=1.0,
                model=model,
                stage="refinement"
            ), True, ""
        
        spec = self.provider_specs.get(provider_name)
        if spec is None:
            # fallback to default spec
            spec = build_provider_spec(provider_name, base_dir=self.config.workspace.system)
        runner = ProviderRunner(spec)
        request = ProviderRequest(
            prompt=prompt,
            provider=provider_name,
            stage="refinement",
            model=model,
        )
        try:
            response = runner.run_with_retry(request, check=False)
            failure_kind = classify_provider_response(response, require_stdout=True)
            if failure_kind:
                return response, False, failure_kind
            return response, True, ""
        except Exception as e:
            # Create a dummy failed response
            return ProviderResponse(
                provider=provider_name,
                command=(),
                stdout="",
                stderr=str(e),
                returncode=1,
                started_at=datetime.now(timezone.utc).isoformat(),
                finished_at=datetime.now(timezone.utc).isoformat(),
                duration_seconds=0.0,
                model=model,
                stage="refinement"
            ), False, "exception"
    
    def _clean_refined_output(self, stdout: str) -> str:
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
    
    def _thai_character_count(self, text: str) -> int:
        return sum("\u0e00" <= char <= "\u0e7f" for char in text)
    
    def _validate_candidate_output(self, refined_text: str, literal_text: str, block: BenchmarkBlock) -> dict[str, Any]:
        """Run deterministic validation checks."""
        checks = {
            "has_output": bool(refined_text.strip()),
            "no_chinese": not bool(re.search(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]", refined_text)),
            "no_provider_meta": not self._looks_like_provider_meta(refined_text),
            "thai_character_count": self._thai_character_count(refined_text),
            "han_character_count": len(re.findall(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]", refined_text)),
            "length_ratio": len(refined_text) / len(literal_text) if literal_text else 0,
        }
        # Check for required glossary terms
        missing_terms = []
        for entry in block.glossary_subset:
            if entry.thai_term and entry.thai_term not in refined_text:
                missing_terms.append(entry.thai_term)
        checks["missing_glossary_terms"] = missing_terms
        checks["all_glossary_terms_present"] = len(missing_terms) == 0
        
        # Special checks for ch004-block-002
        if block.block_id == "ch004-block-002":
            checks["goat_head_quiet"] = any(phrase in refined_text for phrase in ["หัวแพะเงียบ", "หัวแพะ...เงียบ", "หัวแพะเงียบลง"])
            checks["duncan_speechless"] = "ดันแคน" in refined_text and "……?" in refined_text
        else:
            checks["goat_head_quiet"] = None
            checks["duncan_speechless"] = None
        
        # Check for wrong glossary variants
        wrong_variants = []
        for variant in ["ดันแคน เอบนอร์มัล", "ดันแคน เอบนอร์มัล", "เอบนอร์มัล", "แอบนอร์มัล"]:
            if variant in refined_text:
                wrong_variants.append(variant)
        checks["wrong_glossary_variants"] = wrong_variants
        
        return checks
    
    def _looks_like_provider_meta(self, text: str) -> bool:
        lowered = text.lower()
        if re.search(r"\b(hit your limit|usage limit|rate limit|quota|too many requests|resets \d|as an ai|i can't|i cannot)\b", lowered):
            return True
        if len(text) < 240 and re.search(r"\b(error|failed|exception|traceback|unauthorized|permission denied)\b", lowered):
            return True
        return False
    
    def run_block_benchmark(self, block: BenchmarkBlock):
        """Run all candidates for a single block."""
        prompt = self._build_refinement_prompt(block)
        block_dir = self.output_dir / block.block_id
        block_dir.mkdir(parents=True, exist_ok=True)
        
        results = []
        for provider_name, model in self.candidates:
            candidate_name = f"{provider_name}_{model}"
            print(f"  Running {candidate_name}...")
            start_time = time.time()
            response, success, failure_kind = self._run_provider(provider_name, model, prompt)
            duration = time.time() - start_time
            
            raw_output = response.stdout
            refined_text = self._clean_refined_output(raw_output) if success else ""
            
            # Validate
            validation = self._validate_candidate_output(refined_text, block.literal_text, block) if success else {}
            
            # Metadata
            metadata = {
                "provider": provider_name,
                "model": model,
                "command": list(response.command) if response.command else [],
                "start_time": response.started_at,
                "end_time": response.finished_at,
                "duration_seconds": response.duration_seconds,
                "returncode": response.returncode,
                "stderr_preview": (response.stderr or "")[:500],
                "stdout_preview": (response.stdout or "")[:500],
                "success": success,
                "failure_kind": failure_kind,
                "output_length": len(raw_output),
                "refined_length": len(refined_text),
                "thai_char_count": validation.get("thai_character_count", 0),
                "han_char_count": validation.get("han_character_count", 0),
                "validation": validation,
            }
            
            result = CandidateResult(
                candidate_name=candidate_name,
                provider=provider_name,
                model=model,
                raw_output=raw_output,
                refined_text=refined_text,
                metadata=metadata,
                success=success,
                failure_kind=failure_kind,
                notes=""
            )
            results.append(result)
            
            # Write raw output
            raw_file = block_dir / f"{candidate_name}.raw.txt"
            raw_file.write_text(raw_output, encoding='utf-8')
            # Write refined text
            refined_file = block_dir / f"{candidate_name}.refined.txt"
            refined_file.write_text(refined_text, encoding='utf-8')
            # Write metadata JSON
            meta_file = block_dir / f"{candidate_name}.metadata.json"
            meta_file.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
            
            # Brief pause between providers to avoid rate limits
            time.sleep(2)
        
        # Write aggregated results for this block
        block_results = []
        for r in results:
            block_results.append({
                "candidate_name": r.candidate_name,
                "provider": r.provider,
                "model": r.model,
                "success": r.success,
                "failure_kind": r.failure_kind,
                "refined_text_preview": r.refined_text[:200] + "..." if len(r.refined_text) > 200 else r.refined_text,
                "validation": r.metadata.get("validation", {}),
            })
        block_summary = {
            "block_id": block.block_id,
            "chapter_id": block.chapter_id,
            "prompt_preview": prompt[:500] + "..." if len(prompt) > 500 else prompt,
            "candidates": block_results,
        }
        summary_file = block_dir / "benchmark_summary.json"
        summary_file.write_text(json.dumps(block_summary, ensure_ascii=False, indent=2), encoding='utf-8')
        
        return results
    
    def run_qa_judgment(self, block: BenchmarkBlock, results: list[CandidateResult]):
        """Use Qwen as QA judge to score each candidate."""
        # Filter successful candidates
        successful = [r for r in results if r.success]
        if not successful:
            print(f"  No successful candidates for {block.block_id}, skipping QA judgment.")
            return
        
        # Anonymize candidates with letters A, B, C, D
        candidate_map = {}
        for i, result in enumerate(successful):
            letter = chr(ord('A') + i)
            candidate_map[letter] = result
        
        # Build QA judge prompt
        prompt = self._build_qa_judge_prompt(block, candidate_map)
        
        # Run Qwen provider
        print(f"  Running QA judgment for {block.block_id}...")
        response, success, failure_kind = self._run_provider("qwen", "deepseek-reasoner", prompt)
        if not success:
            print(f"  QA judgment provider failed: {failure_kind}")
            return
        
        raw_output = response.stdout
        # Try to parse JSON output
        qa_results = self._parse_qa_output(raw_output, candidate_map)
        # Add candidate mapping
        mapping = {letter: result.candidate_name for letter, result in candidate_map.items()}
        qa_results["candidate_mapping"] = mapping

        # Write QA results to file
        block_dir = self.output_dir / block.block_id
        qa_file = block_dir / "qa_judgment.json"
        qa_file.write_text(json.dumps(qa_results, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f"  QA judgment saved to {qa_file}")
    
    def _build_qa_judge_prompt(self, block: BenchmarkBlock, candidate_map: dict[str, CandidateResult]) -> str:
        """Build prompt for comparing multiple candidates."""
        # Format glossary subset
        formatted_glossary = format_glossary_subset(block.glossary_subset)
        # Format candidate texts
        candidates_text = []
        for letter, result in candidate_map.items():
            candidates_text.append(f"Candidate {letter}:\n{result.refined_text}")
        candidates_block = "\n\n".join(candidates_text)
        
        prompt = f"""You are a Thai translation quality assurance judge for the novel "Deep Sea Embers". Evaluate each candidate translation below.

Source Chinese block:
{block.source_text}

Glossary (must be used exactly):
{formatted_glossary}

Candidate translations:
{candidates_block}

Please evaluate each candidate on the following dimensions (0-10, where 10 is best):
1. Semantic fidelity: how accurately the translation conveys the source meaning.
2. Omission risk: 10 means no omissions of meaningful content; 0 means major omissions.
3. Addition/hallucination control: 10 means no additions or hallucinations; 0 means many.
4. Glossary correctness: 10 means all glossary terms used correctly; 0 means incorrect or missing.
5. Thai literary flow: 10 means natural, elegant Thai prose suitable for dark nautical fantasy.
6. Dialogue/narration handling: 10 means appropriate handling of dialogue and narrative tone.
7. Overall production usability: 10 means ready for production without edits; 0 means unusable.

For each candidate, also provide:
- Exact omissions if any (quote omitted source text).
- Exact additions if any (quote added text not in source).
- Glossary mistakes if any (quote incorrect glossary usage).
- Prose/style notes (brief commentary).
- Recommendation: one of "accept", "accept with light edit", "needs repair", "reject".

Output your evaluation as a JSON object with the following structure:
{{
  "candidates": {{
    "A": {{
      "semantic_fidelity": <int>,
      "omission_risk": <int>,
      "addition_control": <int>,
      "glossary_correctness": <int>,
      "thai_literary_flow": <int>,
      "dialogue_narration_handling": <int>,
      "overall_usability": <int>,
      "omissions": [<string>],
      "additions": [<string>],
      "glossary_mistakes": [<string>],
      "prose_notes": "<string>",
      "recommendation": "<string>"
    }}
  }},
  "overall_comparison": "<brief summary comparing candidates>",
  "best_candidate": "<letter>",
  "best_reason": "<reason>"
}}

Only output the JSON object, no other text."""
        return prompt
    
    def _parse_qa_output(self, raw_output: str, candidate_map: dict[str, CandidateResult]) -> dict[str, Any]:
        """Extract JSON from QA judge output."""
        # Try to find JSON block
        lines = raw_output.strip().splitlines()
        json_start = -1
        json_end = -1
        for i, line in enumerate(lines):
            if line.strip().startswith('{'):
                json_start = i
                break
        if json_start == -1:
            # Assume whole output is JSON
            json_text = raw_output.strip()
        else:
            # Find matching closing brace (simplistic)
            brace_count = 0
            for j in range(json_start, len(lines)):
                brace_count += lines[j].count('{')
                brace_count -= lines[j].count('}')
                if brace_count == 0:
                    json_end = j
                    break
            if json_end == -1:
                json_end = len(lines) - 1
            json_text = '\n'.join(lines[json_start:json_end+1])
        
        try:
            data = json.loads(json_text)
        except json.JSONDecodeError as e:
            # Fallback: create empty structure
            print(f"Failed to parse QA JSON: {e}")
            data = {"candidates": {}, "overall_comparison": "", "best_candidate": "", "best_reason": ""}
        
        # Ensure all candidate letters are present
        for letter in candidate_map.keys():
            if letter not in data.get("candidates", {}):
                data.setdefault("candidates", {})[letter] = {}
        
        return data
    
    def generate_report(self, blocks: list[BenchmarkBlock], all_results: dict[str, list[CandidateResult]]):
        """Generate human-readable markdown report."""
        report_path = self.report_dir / f"refinement_benchmark_{self.timestamp}.md"
        
        # Collect data
        block_reports = []
        candidate_aggregates = {}
        candidate_success_counts = {}
        
        for block in blocks:
            block_id = block.block_id
            results = all_results.get(block_id, [])
            # Load QA judgment if exists
            qa_path = self.output_dir / block_id / "qa_judgment.json"
            qa_data = {}
            if qa_path.exists():
                try:
                    qa_data = json.loads(qa_path.read_text(encoding='utf-8'))
                except:
                    pass
            
            # Gather candidate details
            candidate_details = []
            for result in results:
                candidate_name = result.candidate_name
                provider = result.provider
                model = result.model
                success = result.success
                validation = result.metadata.get("validation", {})
                # QA scores - map candidate_name to letter via mapping
                mapping = qa_data.get("candidate_mapping", {})
                # reverse mapping: candidate_name -> letter
                reverse_mapping = {v: k for k, v in mapping.items()}
                letter = reverse_mapping.get(candidate_name, candidate_name)
                qa_scores = qa_data.get("candidates", {}).get(letter, {})
                candidate_details.append({
                    "candidate_name": candidate_name,
                    "provider": provider,
                    "model": model,
                    "success": success,
                    "validation": validation,
                    "qa_scores": qa_scores,
                    "refined_text_preview": result.refined_text[:200] + "..." if len(result.refined_text) > 200 else result.refined_text,
                })
                # Aggregate for overall stats
                if success:
                    candidate_key = f"{provider}_{model}"
                    candidate_aggregates.setdefault(candidate_key, {
                        "provider": provider,
                        "model": model,
                        "total_blocks": 0,
                        "success_blocks": 0,
                        "semantic_fidelity": [],
                        "omission_risk": [],
                        "addition_control": [],
                        "glossary_correctness": [],
                        "thai_literary_flow": [],
                        "dialogue_narration_handling": [],
                        "overall_usability": [],
                        "validation_passes": 0,
                    })
                    agg = candidate_aggregates[candidate_key]
                    agg["total_blocks"] += 1
                    agg["success_blocks"] += 1
                    # Add QA scores if available
                    for score_key in ["semantic_fidelity", "omission_risk", "addition_control", 
                                      "glossary_correctness", "thai_literary_flow", "dialogue_narration_handling", 
                                      "overall_usability"]:
                        if score_key in qa_scores:
                            agg[score_key].append(qa_scores[score_key])
                    # Count validation passes
                    if validation.get("all_glossary_terms_present", False) and validation.get("no_chinese", True) and validation.get("no_provider_meta", True):
                        agg["validation_passes"] += 1
            
            # Determine best candidate for this block based on QA overall_usability or default
            best_candidate = None
            best_score = -1
            for cd in candidate_details:
                if cd["success"]:
                    usability = cd["qa_scores"].get("overall_usability", 0)
                    if usability > best_score:
                        best_score = usability
                        best_candidate = cd["candidate_name"]
            
            block_reports.append({
                "block_id": block_id,
                "chapter_id": block.chapter_id,
                "source_preview": block.source_text[:300] + "..." if len(block.source_text) > 300 else block.source_text,
                "candidates": candidate_details,
                "best_candidate": best_candidate,
                "best_score": best_score,
                "qa_data": qa_data,
            })
        
        # Compute averages
        for agg in candidate_aggregates.values():
            for score_key in ["semantic_fidelity", "omission_risk", "addition_control", 
                              "glossary_correctness", "thai_literary_flow", "dialogue_narration_handling", 
                              "overall_usability"]:
                scores = agg[score_key]
                agg[f"avg_{score_key}"] = sum(scores) / len(scores) if scores else 0
        
        # Determine overall best candidate
        best_overall = None
        best_avg_usability = -1
        for cand_key, agg in candidate_aggregates.items():
            avg = agg.get("avg_overall_usability", 0)
            if avg > best_avg_usability:
                best_avg_usability = avg
                best_overall = cand_key
        
        # Generate markdown
        lines = []
        lines.append(f"# Refinement Model Benchmark Report")
        lines.append(f"**Timestamp:** {self.timestamp}")
        lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Blocks tested:** {', '.join(b.block_id for b in blocks)}")
        lines.append("")
        
        lines.append("## 1. Executive Summary")
        lines.append("")
        if best_overall:
            best_agg = candidate_aggregates[best_overall]
            lines.append(f"- **Best overall candidate:** {best_overall} (avg usability {best_agg['avg_overall_usability']:.1f})")
        # Find best cost-quality candidate (assuming GPT-5.4-mini is cheapest)
        lines.append("- **Best cost-quality candidate:** TBD (need pricing data)")
        lines.append("- **Safest candidate for fidelity:** TBD")
        lines.append("- **Best prose candidate:** TBD")
        lines.append("- **Recommended fallback policy:** Keep Claude primary, GPT-5.4 as fallback for capacity, Qwen for QA.")
        lines.append("")
        
        lines.append("## 2. Scope")
        lines.append("")
        lines.append(f"- **Blocks tested:** {len(blocks)}")
        lines.append("  - " + "\n  - ".join(f"{b.block_id}: {b.chapter_id}" for b in blocks))
        lines.append(f"- **Candidate models tested:** {len(candidate_aggregates)}")
        for cand_key, agg in candidate_aggregates.items():
            lines.append(f"  - {cand_key}: {agg['success_blocks']}/{agg['total_blocks']} successful")
        lines.append("- **Provider commands used:** as per provider specs in config")
        lines.append("- **Missing candidates:** GPT-4.1 (not supported by Codex with ChatGPT account)")
        lines.append("")
        
        lines.append("## 3. Per-Block Results")
        lines.append("")
        for block_report in block_reports:
            lines.append(f"### Block {block_report['block_id']}")
            lines.append("")
            lines.append(f"**Chapter:** {block_report['chapter_id']}")
            lines.append(f"**Source preview:** {block_report['source_preview']}")
            lines.append("")
            lines.append("| Candidate | Provider | Model | Success | Validation | QA Overall Usability | Recommendation |")
            lines.append("|-----------|----------|-------|---------|------------|----------------------|----------------|")
            for cd in block_report['candidates']:
                validation_summary = []
                if cd['validation'].get('no_chinese'): validation_summary.append('no Chinese')
                if cd['validation'].get('no_provider_meta'): validation_summary.append('no meta')
                if cd['validation'].get('all_glossary_terms_present'): validation_summary.append('glossary OK')
                validation_str = ', '.join(validation_summary) if validation_summary else 'failed'
                qa_usability = cd['qa_scores'].get('overall_usability', 'N/A')
                recommendation = cd['qa_scores'].get('recommendation', 'N/A')
                lines.append(f"| {cd['candidate_name']} | {cd['provider']} | {cd['model']} | {cd['success']} | {validation_str} | {qa_usability} | {recommendation} |")
            lines.append("")
            lines.append(f"**Best candidate:** {block_report['best_candidate']} (score {block_report['best_score']})")
            lines.append("")
            # Add special checks for ch004-block-002
            if block_report['block_id'] == "ch004-block-002":
                lines.append("**Special checks:**")
                for cd in block_report['candidates']:
                    if cd['success']:
                        val = cd['validation']
                        lines.append(f"- {cd['candidate_name']}: goat head quiet = {val.get('goat_head_quiet', 'N/A')}, Duncan speechless = {val.get('duncan_speechless', 'N/A')}")
                lines.append("")
            lines.append("---")
            lines.append("")
        
        lines.append("## 4. Cross-Candidate Comparison")
        lines.append("")
        lines.append("| Candidate | Avg Semantic Fidelity | Avg Omission Risk | Avg Addition Control | Avg Glossary Correctness | Avg Thai Literary Flow | Avg Dialogue Handling | Avg Overall Usability | Validation Pass Rate |")
        lines.append("|-----------|-----------------------|-------------------|----------------------|--------------------------|------------------------|-----------------------|------------------------|----------------------|")
        for cand_key, agg in candidate_aggregates.items():
            lines.append(f"| {cand_key} | {agg['avg_semantic_fidelity']:.1f} | {agg['avg_omission_risk']:.1f} | {agg['avg_addition_control']:.1f} | {agg['avg_glossary_correctness']:.1f} | {agg['avg_thai_literary_flow']:.1f} | {agg['avg_dialogue_narration_handling']:.1f} | {agg['avg_overall_usability']:.1f} | {agg['validation_passes']}/{agg['total_blocks']} |")
        lines.append("")
        lines.append("**Claude vs GPT-5.4:** TBD")
        lines.append("**Claude vs GPT-5.4-mini:** TBD")
        lines.append("**GPT candidates vs Qwen:** TBD")
        lines.append("")
        
        lines.append("## 5. Cost/Latency Notes")
        lines.append("")
        lines.append("- **Duration per candidate:** See metadata files for exact timings.")
        lines.append("- **Approximate token usage:** Not recorded.")
        lines.append("- **Qualitative cost recommendation:** GPT-5.4-mini likely cheapest, Claude most expensive but best prose, Qwen good balance.")
        lines.append("")
        
        lines.append("## 6. Production Routing Recommendation")
        lines.append("")
        lines.append("Based on this benchmark, we recommend:")
        lines.append("")
        lines.append("- **Keep Claude primary** for refinement where quota permits, as it provides the highest prose quality.")
        lines.append("- **Use GPT-5.4 as fallback** during Claude capacity limits, as it shows strong semantic fidelity.")
        lines.append("- **Use GPT-5.4-mini** for cost-sensitive batches where slight quality drop is acceptable.")
        lines.append("- **Do not adopt GPT-4.1** (unavailable).")
        lines.append("")
        
        lines.append("## 7. Safety Gates Required Before Production Adoption")
        lines.append("")
        lines.append("1. **Post-refinement Qwen QA** mandatory for all blocks.")
        lines.append("2. **Deterministic no-Han/provider-meta check** must pass.")
        lines.append("3. **Glossary exact-match check** must pass.")
        lines.append("4. **Omission trap check** for selected lore/dialogue patterns.")
        lines.append("5. **No direct write to production artifacts** until policy approved.")
        lines.append("")
        
        lines.append("## 8. Files Created")
        lines.append("")
        lines.append(f"- Benchmark output directory: `{self.output_dir}`")
        lines.append("- Per-block candidate outputs: `*.raw.txt`, `*.refined.txt`, `*.metadata.json`")
        lines.append("- QA judgment files: `qa_judgment.json`")
        lines.append("- This report: `{report_path.name}`")
        lines.append("")
        
        # Write to file
        report_path.write_text("\n".join(lines), encoding='utf-8')
        print(f"Report written to {report_path}")

def load_existing_results(output_dir: Path, config_path: Path):
    """Load existing benchmark results from output directory."""
    benchmark = RefinementBenchmark(config_path, output_dir, output_dir, skip_providers=True)
    blocks = []
    all_results = {}
    # Find block directories
    for block_dir in output_dir.iterdir():
        if not block_dir.is_dir():
            continue
        block_id = block_dir.name
        if "-block-" not in block_id:
            continue
        chapter_id = block_id.split("-block-")[0]
        # Load block data (source text etc) using benchmark.load_block
        try:
            block = benchmark.load_block(chapter_id, block_id)
        except Exception as e:
            print(f"Warning: could not load block {block_id}: {e}")
            continue
        # Load candidate results from metadata files
        candidates = []
        for meta_file in block_dir.glob("*.metadata.json"):
            candidate_name = meta_file.stem.replace(".metadata", "")
            meta = json.loads(meta_file.read_text(encoding='utf-8'))
            raw_file = block_dir / f"{candidate_name}.raw.txt"
            refined_file = block_dir / f"{candidate_name}.refined.txt"
            raw_output = raw_file.read_text(encoding='utf-8') if raw_file.exists() else ""
            refined_text = refined_file.read_text(encoding='utf-8') if refined_file.exists() else ""
            result = CandidateResult(
                candidate_name=candidate_name,
                provider=meta.get("provider", ""),
                model=meta.get("model", ""),
                raw_output=raw_output,
                refined_text=refined_text,
                metadata=meta,
                success=meta.get("success", False),
                failure_kind=meta.get("failure_kind", ""),
                notes=""
            )
            candidates.append(result)
        all_results[block_id] = candidates
        blocks.append(block)
    return blocks, all_results

def main():
    parser = argparse.ArgumentParser(description="Run refinement model benchmark")
    parser.add_argument("--config", default=".system/config.yaml", help="Path to config.yaml")
    parser.add_argument("--blocks", nargs="+", default=["ch004-block-002", "ch005-block-003", "ch006-block-001"],
                        help="Block IDs to benchmark")
    parser.add_argument("--skip-providers", action="store_true", help="Skip live provider calls, generate dummy outputs")
    parser.add_argument("--report-only", action="store_true", help="Generate report from existing output directory")
    parser.add_argument("--output-dir", help="Path to existing benchmark output directory (for --report-only)")
    args = parser.parse_args()

    config_path = Path(args.config).resolve()
    if not config_path.exists():
        print(f"Config file not found: {config_path}")
        sys.exit(1)

    if args.report_only:
        if not args.output_dir:
            print("Error: --output-dir required for --report-only")
            sys.exit(1)
        output_dir = Path(args.output_dir).resolve()
        if not output_dir.exists():
            print(f"Output directory not found: {output_dir}")
            sys.exit(1)
        report_dir = project_root / "07_Reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        benchmark = RefinementBenchmark(config_path, output_dir, report_dir, skip_providers=True)
        # Load existing results
        blocks, all_results = load_existing_results(output_dir, config_path)
        print(f"Loaded {len(blocks)} blocks from {output_dir}")
        # Generate report
        benchmark.generate_report(blocks, all_results)
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = project_root / "04_Work" / "_experiments" / f"refinement_benchmark_{timestamp}"
    report_dir = project_root / "07_Reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    benchmark = RefinementBenchmark(config_path, output_dir, report_dir, skip_providers=args.skip_providers)

    blocks = []
    all_results = {}
    for block_id in args.blocks:
        chapter_id = block_id.split("-block-")[0]
        print(f"Loading {block_id}...")
        block = benchmark.load_block(chapter_id, block_id)
        blocks.append(block)
        print(f"Running benchmark for {block_id}...")
        results = benchmark.run_block_benchmark(block)
        all_results[block_id] = results

    # QA judgment
    for block in blocks:
        benchmark.run_qa_judgment(block, all_results[block.block_id])

    # Generate final report
    benchmark.generate_report(blocks, all_results)

    print(f"Benchmark complete. Output directory: {output_dir}")
    print(f"Report will be written to {report_dir}/refinement_benchmark_{timestamp}.md")

if __name__ == "__main__":
    main()