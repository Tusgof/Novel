# Refinement Model Benchmark Fix Report
**Timestamp:** 20260417_033911
**Generated:** 2026-04-17 03:39:30
**Blocks tested:** ch004-block-002, ch005-block-003, ch006-block-001

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
| qwen_deepseek-reasoner | True | no Chinese, no meta | provider_called |
| codex_gpt-5.4 | True | no Chinese, no meta | provider_called |
| codex_gpt-5.4-mini | True | no Chinese, no meta | provider_called |

### Block ch005-block-003

| Candidate | Success | Validation | Notes |
|-----------|---------|------------|-------|
| claude_sonnet_reused_previous | True | no Chinese, no meta, glossary OK | reused_existing_previous_benchmark_output |
| production_current_refined | True | no Chinese, no meta, glossary OK | production_current_refined |
| qwen_deepseek-reasoner | True | no Chinese, no meta | provider_called |
| codex_gpt-5.4 | True | no Chinese, no meta | provider_called |
| codex_gpt-5.4-mini | True | no Chinese, no meta | provider_called |

### Block ch006-block-001

| Candidate | Success | Validation | Notes |
|-----------|---------|------------|-------|
| claude_sonnet_reused_previous | True | no Chinese, no meta, glossary OK | reused_existing_previous_benchmark_output |
| production_current_refined | True | no Chinese, no meta, glossary OK | production_current_refined |
| qwen_deepseek-reasoner | True | no Chinese, no meta | provider_called |
| codex_gpt-5.4 | True | no Chinese, no meta | provider_called |
| codex_gpt-5.4-mini | True | no Chinese, no meta | provider_called |

## 3. GPT Provider Fix

Codex provider spec updated to use stdin transport, extra_args: `--skip-git-repo-check --cd <project_root>`.

## 4. Recommendations

To be determined after QA judgment.
