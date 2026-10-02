# Research Log: V6.36 Lean Pipeline Smoke Pilot

- Timestamp UTC: `2026-10-02T16:39:43Z`
- Project: Novel Translation Pipeline
- Topic: First lean-pipeline smoke pilot with full provider trace
- Author: Codex
- Status: blocked

## 1. Objective

Validate that the experiment-only lean harness can make an auditable provider call and stop safely on a provider hard-fail before spending the rest of the pilot budget.

This is not an A/B result. It is an instrumentation and provider-readiness check.

## 2. Setup

- Novel: Horror Game Developer
- Chapter: `ch001`
- Run: `v6-36-lean-hgd-ch001-smoke`
- Arm: `lean`
- Source: production `03_Raw/ch001/source.json` read-only
- Output: `Horror Game Developers/04_Work/_experiments/v6_36_lean_hgd_ch001/05_Output/`
- Trace: `Horror Game Developers/04_Work/_experiments/v6_36_lean_hgd_ch001/trace/`
- Command: `Deep Sea Embers/scripts/run_lean_pipeline_experiment.py`

## 3. Expected Call Sequence

For this one-block chapter the expected sequence was:

1. block-safe literal translation
2. assembled chapter refinement
3. chapter-level QA
4. chapter-level formatting
5. proposed glossary harvest

The run stopped at step 1, so steps 2-5 were not called.

## 4. Observed Data

| Metric | Result |
|:--|:--|
| Provider calls | 1 |
| Completed chapters | 0 |
| Translation output | none |
| Provider failures | 1 |
| Failure stage | `literal_translation` |
| Provider/model | OpenRouter / `google/gemini-3.7-flash` |
| Requested output ceiling | 12,000 tokens |
| Provider affordable ceiling | 10,005 tokens |
| Error | HTTP 402: more credits or fewer `max_tokens` required |
| Usage/cost | not measured; provider returned no usage |
| Production output touched | no |
| MoonRead touched | no |

Full prompt, system prompt, response/error, hashes, command metadata, and context are in the trace JSON. The trace was sanitized to redact OpenRouter URLs and user identifiers. Do not paste the full trace into a research log because it contains source chapter text.

## 5. Separate Health Probes

These were not part of the experiment arm and were not used as quality evidence:

- Gemini with reasoning enabled/excluded and 16-token ceiling: returned `OK`.
- DeepSeek with reasoning enabled/excluded and 16-token ceiling: returned empty output with `finish_reason=length`.
- DeepSeek with reasoning enabled/excluded and 256-token ceiling: returned `OK`.

The 16-token DeepSeek result is a budget-bound probe, not a model-quality conclusion.

## 6. Cause, Prevention, Next Action

Cause: the configured OpenRouter route requests a 12,000-token maximum, but the account/key budget can currently afford only 10,005 tokens. The harness correctly stopped before producing partial translation output.

Prevention: run an exact-route credit/ceiling health check before every paid experiment window; do not silently lower the ceiling or switch provider routes because that would change the experiment treatment. Keep provider error redaction active so account URLs and identifiers do not enter durable logs.

Next action: restore enough credit or explicitly approve an isolated experiment configuration with a lower, measured output ceiling. Then rerun the same locked sample from the first chapter; do not treat this stopped smoke pilot as an A/B result.
