# QA Provider Cost/Quality Benchmark - qa_provider_benchmark_20260609_134339

Generated: 2026-06-09T13:43:59

## Scope

- Non-production QA-only comparison.
- Production routing was not changed.
- Compared `deepseek/deepseek-v4-pro`, `deepseek/deepseek-v4-flash`, and Qwen CLI current QA route.
- Cases: 1 total: 10 known-pass, 10 historical-recovery-derived fail cases, 10 adversarial fail cases.

## Summary

| Candidate | Provider | Model | Calls | Avg score | False negatives | Severe false negatives | False positives | Parse failures | Provider failures | Avg latency | Est. cost | Est. cost / 100 blocks |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `openrouter_v4_flash` | openrouter | `deepseek/deepseek-v4-flash` | 1 | 100.00 | 0 | 0 | 0 | 0 | 0 | 19.957s | 0.00059943 | 0.059943 |

## Recommendation

Insufficient OpenRouter data; keep current QA routing until the benchmark can be rerun.

## Per-Case Results

| Candidate | Case | Group | Expected | Predicted | Score | Latency | Cost | First line |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |
| `openrouter_v4_flash` | `pass__ch001-block-001` | known_pass | pass | pass | 100 | 19.957s | 0.0005994334 | PASS: Translation is complete, accurate, and consistent with the source; no omissions, additions, meaning drift, Chinese leakage, or tone issues. |

## Fixture Notes

- Historical-recovery-derived cases use blocks that had historical failed or hard-fail records, then inject one controlled failure when the original bad artifact was not preserved.
- Adversarial cases use current clean artifacts and inject one controlled QA defect.
- The report should be used for QA routing decisions only; it does not evaluate literal translation, refinement, glossary scan, or formatting.

## Safety

- No API key or bearer token is written to artifacts or this report.
- No production ledger, glossary notes, source files, chapter work artifacts, final outputs, or provider config are modified by the benchmark.
