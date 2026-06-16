# OpenRouter Provider Benchmark Report

Generated: 2026-06-09T02:57:41

## Summary

| Model | Calls | Hard fails | Avg score | Avg latency | Recommendation |
| --- | ---: | ---: | ---: | ---: | --- |
| `deepseek/deepseek-v4-flash` | 1 | 0 | 100.0 | 1.43s | candidate |
| `tencent/hy3-preview` | 1 | 1 | 75.0 | 18.66s | reject or retest |
| `minimax/minimax-m3` | 2 | 0 | 100.0 | 4.23s | candidate |
| `xiaomi/mimo-v2.5` | 1 | 1 | 75.0 | 2.28s | reject or retest |
| `openrouter/owl-alpha` | 1 | 0 | 100.0 | 3.36s | candidate |
| `anthropic/claude-sonnet-4.6` | 1 | 0 | 100.0 | 1.63s | candidate |
| `deepseek/deepseek-v4-pro` | 1 | 1 | 85.0 | 2.17s | reject or retest |
| `deepseek/deepseek-v3.2` | 1 | 0 | 100.0 | 3.57s | candidate |
| `google/gemini-3-flash-preview` | 1 | 0 | 100.0 | 1.52s | candidate |

## Per-Task Results

| Model | Role | OK | Score | Hard fail | Latency | Notes |
| --- | --- | --- | ---: | --- | ---: | --- |
| `deepseek/deepseek-v4-flash` | smoke | True | 100 | False | 1.432 | est_cost=0.00001484 |
| `tencent/hy3-preview` | smoke | True | 75 | True | 18.657 | nonempty, json_valid_when_required, est_cost=0.00002001 |
| `minimax/minimax-m3` | smoke | True | 100 | False | 2.241 | est_cost=0.00012210 |
| `minimax/minimax-m3` | smoke | True | 100 | False | 6.21 | est_cost=0.00016050 |
| `xiaomi/mimo-v2.5` | smoke | True | 75 | True | 2.282 | nonempty, json_valid_when_required, est_cost=0.00002954 |
| `openrouter/owl-alpha` | smoke | True | 100 | False | 3.362 | est_cost=0.00000000 |
| `anthropic/claude-sonnet-4.6` | smoke | True | 100 | False | 1.631 | est_cost=0.00051600 |
| `deepseek/deepseek-v4-pro` | smoke | True | 85 | True | 2.168 | json_valid_when_required, est_cost=0.00008569 |
| `deepseek/deepseek-v3.2` | smoke | True | 100 | False | 3.569 | est_cost=0.00001430 |
| `google/gemini-3-flash-preview` | smoke | True | 100 | False | 1.521 | est_cost=0.00004900 |

## Safety

- API key was read from `OPENROUTER_API_KEY` only.
- No production ledger, glossary, source, work chapter artifacts, outputs, or provider config are edited by this script.
- Raw responses are stored under the experiment directory for review.
