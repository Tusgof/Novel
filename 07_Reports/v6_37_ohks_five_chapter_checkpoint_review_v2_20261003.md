# V6.37 OHKS Five-Chapter Checkpoint Review v2

Date: 2026-10-03
Chapters: `ch002,ch017,ch032,ch055,ch090`
Run: `v6-37-ohks-minimal-pilot-v2-checkpointed`

## Scope

This was an experiment-only rerun of five OHKS chapters after implementing the five approved improvements. It did not modify production output, production glossary, or MoonRead.

## Results

| Metric | Result |
|:--|--:|
| Chapters complete | 5/5 |
| Provider calls | 25 |
| Provider failures | 4 |
| Provider time | 1,122.728 seconds |
| Reported tokens | 182,904 |
| Reported cost | `$0.286459146` |
| QA passed | 5/5 |
| Blocking Sentinel | `0/0/0/0` |
| Advisory Sentinel | `0/0/33/0` |
| Glossary review rejected | 4 total |
| Experiment-only terms promoted for later chapters | 77 |
| MoonRead published | no |

The first run stopped safely at `ch090` because literal output was truncated. Resume reran only the broken chapter; the earlier four chapters reused their literal, refinement, QA, formatting, and harvest checkpoints. A second complete `--resume` run added zero provider calls and reused all five stages for all five chapters.

## Five improvements

1. **Source-backed QA disagreement**: the QA fallback receives the previous judge feedback. When an AI FAIL is followed by a PASS, the PASS must quote a source phrase and its Thai counterpart; otherwise the disagreement remains blocked. The run had provider timeouts but no AI FAIL/PASS disagreement, so this rule is regression-tested rather than experimentally exercised in this slice.
2. **Checkpoint resume**: checkpoints now carry source, glossary, prompt, and upstream artifact hashes. Stale checkpoints cannot be reused silently. The interrupted `ch090` recovery and the zero-call replay verify the behavior.
3. **Short novel-specific refine guidance**: OHKS guidance now describes voice, register, and context. The one-off `Grit` word rule was removed from the tracked production prompt; the experiment prompt keeps only a compact context reminder.
4. **Glossary feedback loop**: candidate terms must have exact source and Thai evidence, pass shape/noise/conflict checks, and only high-confidence, non-conflicting candidates enter an experiment-only glossary memory. Later chapters actually projected earlier approved terms, for example `Barba`, `Gaon`, `LoEl`, and `Feather Sword`. No term was written to the production glossary.
5. **Measured cost and reading quality**: all retries and fallbacks are included in trace totals. UTF-8 source-aligned checks covered opening, middle, and ending passages of every chapter; no truncation, CJK leakage, provider metadata, or blocking Sentinel finding remained in the completed outputs.

## Comparison

Against the previous OHKS five-chapter `pilot_v10` slice:

| Metric | v10 | v2 | Interpretation |
|:--|--:|--:|:--|
| Calls | 23 | 25 | v2 worse |
| Provider failures | 2 | 4 | v2 worse |
| Provider time | 919.486s | 1,122.728s | v2 worse |
| Reported cost | `$0.264046182` | `$0.286459146` | v2 worse |

This round demonstrates better recovery and auditability, not a cost or speed improvement. The sample is not paired, so it cannot prove a quality improvement over v10. The 33 advisory findings are mainly English chapter titles and game/system labels; they remain profile/title work before any publication decision.

## Decision

Retain the five mechanisms in the experiment harness. Do not promote the lean pipeline to production and do not publish these artifacts yet. Before publication, create OHKS title sidecars and review the advisory game/UI terminology as a small novel-specific profile, then run a separate bounded comparison focused on advisory findings and reader quality.

## Evidence

- Output: `One Hit Kill Swordmaster/04_Work/_experiments/v6_36_ohks_lean_v1/05_Output/pilot_v12/`
- Trace: `One Hit Kill Swordmaster/04_Work/_experiments/v6_36_ohks_lean_v1/trace/pilot_v12/`
- Blocking Sentinel: `07_Reports/sentinel_quality_experiment_20261003_024140.md`
- Advisory Sentinel: `07_Reports/sentinel_quality_experiment_20261003_023528.md`
- Regression suite: `Deep Sea Embers/test_translation.py`
