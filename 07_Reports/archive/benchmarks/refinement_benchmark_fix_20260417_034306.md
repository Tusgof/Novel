# Refinement Model Benchmark Fix Report
**Timestamp:** 20260417_034306
**Generated:** 2026-04-17 03:44:53
**Blocks tested:** ch004-block-002

## 1. Executive Summary

This benchmark fixes the previous invalid block loading and glossary validation.
- **Block-level source text:** corrected
- **Glossary subset:** now limited to terms appearing in each block
- **Claude calls:** avoided (reused previous outputs)
- **GPT provider:** fixed stdin transport

## 2. Detailed Results

### Block ch004-block-002

| Candidate | Success | Validation | Notes |
|-----------|---------|------------|-------|
| claude_sonnet_reused_previous | True | no Chinese, no meta, glossary OK | reused_existing_previous_benchmark_output |
| production_current_refined | True | no Chinese, no meta, glossary OK, Duncan speechless | production_current_refined |
| qwen_deepseek-reasoner | True | no Chinese, no meta, glossary OK | provider_called |
| codex_gpt-5.4 | False |  | provider_called |
| codex_gpt-5.4-mini | False |  | provider_called |

## 3. GPT Provider Fix

Codex provider spec updated to use stdin transport, extra_args: `--skip-git-repo-check --cd <project_root>`.

## 4. Recommendations

To be determined after QA judgment.
