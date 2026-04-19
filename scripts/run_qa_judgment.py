#!/usr/bin/env python3
"""
Run QA judgment on existing benchmark results.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

# Add the novel_pipeline package to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from novel_pipeline.config import load_app_config
from scripts.refinement_benchmark import RefinementBenchmark, CandidateResult

def load_existing_results(benchmark: RefinementBenchmark, output_dir: Path):
    """Load existing benchmark results from output directory."""
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
    parser = argparse.ArgumentParser(description="Run QA judgment on existing benchmark results")
    parser.add_argument("--output-dir", required=True, help="Path to benchmark output directory")
    parser.add_argument("--config", default=".system/config.yaml", help="Path to config.yaml")
    parser.add_argument("--skip-failed", action="store_true", help="Skip blocks where all candidates failed")
    args = parser.parse_args()

    output_dir = Path(args.output_dir).resolve()
    if not output_dir.exists():
        print(f"Output directory not found: {output_dir}")
        sys.exit(1)

    config_path = Path(args.config).resolve()
    if not config_path.exists():
        print(f"Config file not found: {config_path}")
        sys.exit(1)

    # Create benchmark instance with skip_providers=True (we won't call providers except for QA)
    benchmark = RefinementBenchmark(config_path, output_dir, output_dir, skip_providers=False)  # Need QA provider
    
    # Load existing results
    blocks, all_results = load_existing_results(benchmark, output_dir)
    print(f"Loaded {len(blocks)} blocks from {output_dir}")
    
    # Run QA judgment for each block
    for block in blocks:
        block_id = block.block_id
        results = all_results.get(block_id, [])
        print(f"Running QA judgment for {block_id}...")
        # Check if we have any successful candidates
        successful = [r for r in results if r.success]
        if not successful:
            print(f"  No successful candidates for {block_id}, skipping QA judgment.")
            if args.skip_failed:
                continue
            # Still create empty QA judgment file
            qa_data = {
                "candidates": {},
                "overall_comparison": "No successful candidates",
                "best_candidate": "",
                "best_reason": "No successful outputs to judge",
                "candidate_mapping": {}
            }
            qa_file = output_dir / block_id / "qa_judgment.json"
            qa_file.write_text(json.dumps(qa_data, ensure_ascii=False, indent=2), encoding='utf-8')
            print(f"  Empty QA judgment saved to {qa_file}")
            continue
            
        # Run QA judgment using benchmark method
        benchmark.run_qa_judgment(block, results)
    
    print("QA judgment complete.")

if __name__ == "__main__":
    main()