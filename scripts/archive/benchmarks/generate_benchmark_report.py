#!/usr/bin/env python3
"""
Generate report from an existing benchmark output directory.
"""

import json
import sys
from pathlib import Path
from typing import Any
from datetime import datetime
from dataclasses import dataclass

# Add the novel_pipeline package to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from novel_pipeline.config import load_app_config
from novel_pipeline.providers.base import ProviderResponse

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

def load_results_from_output(output_dir: Path):
    """Load candidate results from benchmark output directory."""
    # Use the existing function from refinement_benchmark module
    from scripts.refinement_benchmark import load_existing_results
    # We need a config path to create a benchmark instance, but load_existing_results
    # requires a benchmark instance. Let's create a minimal config path.
    # Actually load_existing_results takes config_path as second argument.
    # Let's use a dummy config path that exists
    config_path = Path(".system/config.yaml")
    if not config_path.exists():
        # Fallback to empty dict
        return [], {}
    return load_existing_results(output_dir, config_path)

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate report from existing benchmark output")
    parser.add_argument("--output-dir", required=True, help="Path to benchmark output directory")
    parser.add_argument("--config", default=".system/config.yaml", help="Path to config.yaml")
    args = parser.parse_args()
    
    output_dir = Path(args.output_dir).resolve()
    if not output_dir.exists():
        print(f"Output directory not found: {output_dir}")
        sys.exit(1)
    
    config_path = Path(args.config).resolve()
    if not config_path.exists():
        print(f"Config file not found: {config_path}")
        sys.exit(1)
    
    # Load results
    blocks, all_results = load_results_from_output(output_dir)
    print(f"Loaded {len(blocks)} blocks from {output_dir}")
    
    # Create benchmark instance (we need to import RefinementBenchmark)
    from scripts.refinement_benchmark import RefinementBenchmark
    # Since RefinementBenchmark expects output_dir and report_dir, we'll reuse existing dir
    report_dir = project_root / "07_Reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    benchmark = RefinementBenchmark(config_path, output_dir, report_dir, skip_providers=True)
    # Hack: set timestamp from output_dir name
    benchmark.timestamp = output_dir.name.split('refinement_benchmark_')[-1] if 'refinement_benchmark_' in output_dir.name else datetime.now().strftime("%Y%m%d_%H%M%S")
    # Generate report
    benchmark.generate_report(blocks, all_results)

if __name__ == "__main__":
    main()