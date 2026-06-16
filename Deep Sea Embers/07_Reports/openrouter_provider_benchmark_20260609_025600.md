# OpenRouter Provider Benchmark Report

Generated: 2026-06-09T02:56:02

## Summary

| Model | Calls | Hard fails | Avg score | Avg latency | Recommendation |
| --- | ---: | ---: | ---: | ---: | --- |
| `deepseek/deepseek-v4-flash` | 1 | 1 | 55.0 | 0.19s | reject or retest |
| `tencent/hy3-preview` | 1 | 1 | 55.0 | 0.32s | reject or retest |
| `minimax/minimax-m3` | 2 | 2 | 55.0 | 0.19s | reject or retest |
| `xiaomi/mimo-v2.5` | 1 | 1 | 55.0 | 0.19s | reject or retest |
| `openrouter/owl-alpha` | 1 | 1 | 55.0 | 0.21s | reject or retest |
| `anthropic/claude-sonnet-4.6` | 1 | 1 | 55.0 | 0.15s | reject or retest |
| `deepseek/deepseek-v4-pro` | 1 | 1 | 55.0 | 0.12s | reject or retest |
| `deepseek/deepseek-v3.2` | 1 | 1 | 55.0 | 0.24s | reject or retest |
| `google/gemini-3-flash-preview` | 1 | 1 | 55.0 | 0.15s | reject or retest |

## Per-Task Results

| Model | Role | OK | Score | Hard fail | Latency | Notes |
| --- | --- | --- | ---: | --- | ---: | --- |
| `deepseek/deepseek-v4-flash` | smoke | False | 55 | True | 0.193 | http_error, nonempty, json_valid_when_required, est_cost=0.00000000 |
| `tencent/hy3-preview` | smoke | False | 55 | True | 0.321 | http_error, nonempty, json_valid_when_required, est_cost=0.00000000 |
| `minimax/minimax-m3` | smoke | False | 55 | True | 0.172 | http_error, nonempty, json_valid_when_required, est_cost=0.00000000 |
| `minimax/minimax-m3` | smoke | False | 55 | True | 0.211 | http_error, nonempty, json_valid_when_required, est_cost=0.00000000 |
| `xiaomi/mimo-v2.5` | smoke | False | 55 | True | 0.193 | http_error, nonempty, json_valid_when_required, est_cost=0.00000000 |
| `openrouter/owl-alpha` | smoke | False | 55 | True | 0.207 | http_error, nonempty, json_valid_when_required, est_cost=0.00000000 |
| `anthropic/claude-sonnet-4.6` | smoke | False | 55 | True | 0.154 | http_error, nonempty, json_valid_when_required, est_cost=0.00000000 |
| `deepseek/deepseek-v4-pro` | smoke | False | 55 | True | 0.119 | http_error, nonempty, json_valid_when_required, est_cost=0.00000000 |
| `deepseek/deepseek-v3.2` | smoke | False | 55 | True | 0.238 | http_error, nonempty, json_valid_when_required, est_cost=0.00000000 |
| `google/gemini-3-flash-preview` | smoke | False | 55 | True | 0.146 | http_error, nonempty, json_valid_when_required, est_cost=0.00000000 |

## Safety

- API key was read from `OPENROUTER_API_KEY` only.
- No production ledger, glossary, source, work chapter artifacts, outputs, or provider config are edited by this script.
- Raw responses are stored under the experiment directory for review.
