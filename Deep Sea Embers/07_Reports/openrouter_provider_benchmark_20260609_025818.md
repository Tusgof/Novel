# OpenRouter Provider Benchmark Report

Generated: 2026-06-09T03:16:42

## Summary

| Model | Calls | Hard fails | Avg score | Avg latency | Recommendation |
| --- | ---: | ---: | ---: | ---: | --- |
| `deepseek/deepseek-v4-flash` | 6 | 2 | 92.5 | 7.15s | reject or retest |
| `tencent/hy3-preview` | 6 | 6 | 75.0 | 20.68s | reject or retest |
| `minimax/minimax-m3` | 12 | 8 | 83.3 | 19.91s | reject or retest |
| `xiaomi/mimo-v2.5` | 6 | 5 | 76.7 | 11.88s | reject or retest |
| `openrouter/owl-alpha` | 6 | 0 | 100.0 | 29.61s | candidate |
| `anthropic/claude-sonnet-4.6` | 6 | 2 | 95.0 | 26.71s | reject or retest |
| `deepseek/deepseek-v4-pro` | 6 | 4 | 85.8 | 28.12s | reject or retest |
| `deepseek/deepseek-v3.2` | 6 | 2 | 95.0 | 16.46s | reject or retest |
| `google/gemini-3-flash-preview` | 6 | 0 | 100.0 | 3.34s | candidate |

## Per-Task Results

| Model | Role | OK | Score | Hard fail | Latency | Notes |
| --- | --- | --- | ---: | --- | ---: | --- |
| `deepseek/deepseek-v4-flash` | smoke | True | 100 | False | 2.765 | est_cost=0.00000619 |
| `deepseek/deepseek-v4-flash` | glossary | True | 75 | True | 12.478 | nonempty, json_valid_when_required, est_cost=0.00027278 |
| `deepseek/deepseek-v4-flash` | literal | True | 100 | False | 4.403 | est_cost=0.00011698 |
| `deepseek/deepseek-v4-flash` | refine | True | 100 | False | 9.15 | est_cost=0.00022314 |
| `deepseek/deepseek-v4-flash` | qa | True | 80 | True | 7.433 | qa_known_bad_caught, est_cost=0.00012337 |
| `deepseek/deepseek-v4-flash` | format | True | 100 | False | 6.671 | est_cost=0.00013487 |
| `tencent/hy3-preview` | smoke | True | 85 | True | 12.088 | json_valid_when_required, est_cost=0.00002001 |
| `tencent/hy3-preview` | glossary | True | 75 | True | 11.759 | nonempty, json_valid_when_required, est_cost=0.00023759 |
| `tencent/hy3-preview` | literal | True | 75 | True | 36.04 | nonempty, json_valid_when_required, est_cost=0.00027594 |
| `tencent/hy3-preview` | refine | True | 90 | True | 25.43 | nonempty, est_cost=0.00037596 |
| `tencent/hy3-preview` | qa | True | 55 | True | 19.732 | nonempty, json_valid_when_required, qa_known_bad_caught, est_cost=0.00027745 |
| `tencent/hy3-preview` | format | True | 70 | True | 19.048 | nonempty, format_not_truncated, est_cost=0.00033432 |
| `minimax/minimax-m3` | smoke | True | 100 | False | 3.978 | est_cost=0.00013770 |
| `minimax/minimax-m3` | glossary | True | 75 | True | 16.999 | nonempty, json_valid_when_required, est_cost=0.00128820 |
| `minimax/minimax-m3` | literal | True | 75 | True | 30.037 | nonempty, json_valid_when_required, est_cost=0.00159720 |
| `minimax/minimax-m3` | refine | True | 90 | True | 28.731 | nonempty, est_cost=0.00233670 |
| `minimax/minimax-m3` | qa | True | 55 | True | 17.825 | nonempty, json_valid_when_required, qa_known_bad_caught, est_cost=0.00179400 |
| `minimax/minimax-m3` | format | True | 100 | False | 19.754 | est_cost=0.00207570 |
| `minimax/minimax-m3` | smoke | True | 100 | False | 2.254 | est_cost=0.00011490 |
| `minimax/minimax-m3` | glossary | True | 75 | True | 17.508 | nonempty, json_valid_when_required, est_cost=0.00128820 |
| `minimax/minimax-m3` | literal | True | 75 | True | 32.361 | nonempty, json_valid_when_required, est_cost=0.00159720 |
| `minimax/minimax-m3` | refine | True | 90 | True | 31.675 | nonempty, est_cost=0.00233670 |
| `minimax/minimax-m3` | qa | True | 65 | True | 24.019 | json_valid_when_required, qa_known_bad_caught, est_cost=0.00179400 |
| `minimax/minimax-m3` | format | True | 100 | False | 13.725 | est_cost=0.00181290 |
| `xiaomi/mimo-v2.5` | smoke | True | 75 | True | 5.872 | nonempty, json_valid_when_required, est_cost=0.00002954 |
| `xiaomi/mimo-v2.5` | glossary | True | 75 | True | 10.41 | nonempty, json_valid_when_required, est_cost=0.00040936 |
| `xiaomi/mimo-v2.5` | literal | True | 75 | True | 13.035 | nonempty, json_valid_when_required, est_cost=0.00039298 |
| `xiaomi/mimo-v2.5` | refine | True | 100 | False | 15.025 | est_cost=0.00052108 |
| `xiaomi/mimo-v2.5` | qa | True | 65 | True | 12.277 | json_valid_when_required, qa_known_bad_caught, est_cost=0.00045892 |
| `xiaomi/mimo-v2.5` | format | True | 70 | True | 14.639 | nonempty, format_not_truncated, est_cost=0.00048916 |
| `openrouter/owl-alpha` | smoke | True | 100 | False | 1.674 | est_cost=0.00000000 |
| `openrouter/owl-alpha` | glossary | True | 100 | False | 25.557 | est_cost=0.00000000 |
| `openrouter/owl-alpha` | literal | True | 100 | False | 45.198 | est_cost=0.00000000 |
| `openrouter/owl-alpha` | refine | True | 100 | False | 58.735 | est_cost=0.00000000 |
| `openrouter/owl-alpha` | qa | True | 100 | False | 9.321 | est_cost=0.00000000 |
| `openrouter/owl-alpha` | format | True | 100 | False | 37.164 | est_cost=0.00000000 |
| `anthropic/claude-sonnet-4.6` | smoke | True | 100 | False | 1.986 | est_cost=0.00051600 |
| `anthropic/claude-sonnet-4.6` | glossary | True | 85 | True | 13.473 | json_valid_when_required, est_cost=0.01868700 |
| `anthropic/claude-sonnet-4.6` | literal | True | 85 | True | 28.901 | json_valid_when_required, est_cost=0.02011200 |
| `anthropic/claude-sonnet-4.6` | refine | True | 100 | False | 92.815 | est_cost=0.02767800 |
| `anthropic/claude-sonnet-4.6` | qa | True | 100 | False | 13.998 | est_cost=0.01452600 |
| `anthropic/claude-sonnet-4.6` | format | True | 100 | False | 9.074 | est_cost=0.01794000 |
| `deepseek/deepseek-v4-pro` | smoke | True | 75 | True | 3.62 | nonempty, json_valid_when_required, est_cost=0.00008569 |
| `deepseek/deepseek-v4-pro` | glossary | True | 75 | True | 14.743 | nonempty, json_valid_when_required, est_cost=0.00120713 |
| `deepseek/deepseek-v4-pro` | literal | True | 75 | True | 50.355 | nonempty, json_valid_when_required, est_cost=0.00120495 |
| `deepseek/deepseek-v4-pro` | refine | True | 90 | True | 19.57 | nonempty, est_cost=0.00167040 |
| `deepseek/deepseek-v4-pro` | qa | True | 100 | False | 15.13 | est_cost=0.00126281 |
| `deepseek/deepseek-v4-pro` | format | True | 100 | False | 65.323 | est_cost=0.00059682 |
| `deepseek/deepseek-v3.2` | smoke | True | 100 | False | 1.334 | est_cost=0.00001430 |
| `deepseek/deepseek-v3.2` | glossary | True | 85 | True | 27.847 | json_valid_when_required, est_cost=0.00055484 |
| `deepseek/deepseek-v3.2` | literal | True | 85 | True | 25.914 | no_han_for_thai_roles, est_cost=0.00029572 |
| `deepseek/deepseek-v3.2` | refine | True | 100 | False | 24.153 | est_cost=0.00045760 |
| `deepseek/deepseek-v3.2` | qa | True | 100 | False | 11.368 | est_cost=0.00033840 |
| `deepseek/deepseek-v3.2` | format | True | 100 | False | 8.163 | est_cost=0.00026323 |
| `google/gemini-3-flash-preview` | smoke | True | 100 | False | 1.044 | est_cost=0.00004900 |
| `google/gemini-3-flash-preview` | glossary | True | 100 | False | 4.118 | est_cost=0.00236500 |
| `google/gemini-3-flash-preview` | literal | True | 100 | False | 4.811 | est_cost=0.00210250 |
| `google/gemini-3-flash-preview` | refine | True | 100 | False | 4.071 | est_cost=0.00235400 |
| `google/gemini-3-flash-preview` | qa | True | 100 | False | 2.807 | est_cost=0.00121050 |
| `google/gemini-3-flash-preview` | format | True | 100 | False | 3.191 | est_cost=0.00137900 |

## Safety

- API key was read from `OPENROUTER_API_KEY` only.
- No production ledger, glossary, source, work chapter artifacts, outputs, or provider config are edited by this script.
- Raw responses are stored under the experiment directory for review.
