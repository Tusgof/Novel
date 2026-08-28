# Immortality System: Libra - Pilot Gate Completion

Date: 2026-08-28

## Verdict

The mandatory 20-chapter Libra - Pilot Gate for Immortality System passed its
quality and generalization gates in an isolated experiment vault. This is a
setup-readiness result, not approval to publish experiment output or to start
production translation automatically.

## Scope And Reproducibility

- Source: Novel543, verified through `ch2570` (`2570/2570` usable chapters).
- Fixed seed: `20260828`.
- Sampling source: fetched `03_Raw/` only, with five strata and two chapters per
  set in each stratum.
- In-sample: `ch1307,ch1765,ch2439,ch2307,ch741,ch1424,ch1631,ch376,ch338,ch984`.
- Out-of-sample: `ch1410,ch1020,ch2313,ch2358,ch1149,ch1653,ch1984,ch213,ch544,ch282`.
- Source parity: `0` mismatches for the locked sample.

Sample evidence:

- `07_Reports/libra_pilot_gate_sample_20260828.md`
- `07_Reports/libra_pilot_gate_sample_20260828.json`

## Gate Results

| Gate | In-sample | Out-of-sample | Result |
|:--|--:|--:|:--|
| Chapters completed | 10/10 | 10/10 | pass |
| Blocks completed | 42/42 | 40/40 | pass |
| Current failed blocks | 0 | 0 | pass |
| Historical failed ledger records | 3, recovered | 0 | recorded, no current failure |
| Output cleanliness | 10/10 chapters clean | 10/10 chapters clean | pass |
| Blocking Sentinel | `0/0/0/0` | `0/0/0/0` | pass |
| Sentinel safe to publish | yes | yes | pass for experiment evidence only |
| Source parity | 0 mismatches | 0 mismatches | pass |

The final Sentinel reports are:

- `Immortality System/04_Work/_experiments/libra_pilot_immortality_system_v1/07_Reports/sentinel_quality_immortality-libra-v1-insample-closure_20260828_092332.md`
- `Immortality System/04_Work/_experiments/libra_pilot_immortality_system_v1/07_Reports/sentinel_quality_immortality-libra-v1-oos-closure_20260828_092333.md`

## Reliability Evidence

- In-sample had three historical OpenRouter empty-assistant refinement failures.
  They were recovered through the bounded recovery path; no force-accept was
  used and no failed artifact became final output.
- OOS had no historical failed ledger records. Fallback use was recorded in
  the provider metadata, including QA fallback and formatting fallback events.
- All sampled title sidecars were present and valid before final assembly.
- The experiment-aware Sentinel registry/report-root resolution is covered by
  `test_sentinel_env_overrides_resolve_nearest_experiment_registry` and
  `test_sentinel_env_overrides_leave_production_workspace_unchanged`.

Provider and checkpoint evidence:

- `Immortality System/04_Work/_experiments/libra_pilot_immortality_system_v1/07_Reports/immortality_libra_pilot_insample_checkpoint_20260828.md`
- `Immortality System/04_Work/_experiments/libra_pilot_immortality_system_v1/07_Reports/immortality_libra_pilot_oos_checkpoint_20260828.md`
- `Immortality System/04_Work/_experiments/libra_pilot_immortality_system_v1/07_Reports/immortality_libra_pilot_insample_provider_usage_20260828.md`
- `Immortality System/04_Work/_experiments/libra_pilot_immortality_system_v1/07_Reports/immortality_libra_pilot_oos_provider_usage_20260828.md`

## Glossary Decision

The audit found some exact-match differences for generic, context-dependent
terms such as `紀元`, `五姓`, `有人`, and `九域`. These are semantic variation
signals, not character/title/system-term failures: there were no suspicious
wrong variants and the blocking Sentinel found no glossary blocker or major.
They remain research evidence and are not promoted into the production
glossary.

## Limitations And Recommendation

This pilot did not run a causal baseline-versus-treatment comparison, and it
did not test broad unattended parallel translation/refinement/QA. Wall-clock
elapsed time includes pauses, retries, and recovery, so it is not a clean speed
benchmark.

Recommended first production mode:

1. Keep translation bounded and sequential.
2. Use 5-chapter glossary gates and explicit chapter ranges.
3. Keep deterministic output guardrails, blocking Sentinel, and the major-run
   spot-check checklist enabled.
4. Start production only after a separate explicit user-approved range; do not
   copy experiment output into production or MoonRead.

No production `05_Output`, production glossary intent, production ledger intent,
or MoonRead content was changed by this pilot.
