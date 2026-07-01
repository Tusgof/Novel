# V6.34 M6 Cross-Novel OOS Comparison And Production Recommendation

## Scope

V6.34 measured out-of-sample behavior across three isolated experiment vaults:

| Novel | Run ID | OOS Chapters | Blocks |
|---|---|---:|---:|
| Horror Game Developer | `v6-34-m6-hgd-oos-v1` | 10 | 10 |
| Deep Sea Embers | `v6-34-m6-dse-oos-v2` | 10 | 55 |
| Infinite Regressor Stories | `v6-34-m6-irs-oos-v1` | 10 | 33 |

Experiment outputs remain isolated. No MoonRead publication is approved by this report.

## Comparison

| Metric | HGD OOS | DSE OOS | IRS OOS | Interpretation |
|---|---:|---:|---:|---|
| Completed chapters | 10/10 | 10/10 | 10/10 | All three OOS slices finished after bounded recovery/treatment loops |
| Completed blocks | 10/10 | 55/55 | 33/33 | All intended blocks complete |
| Current failed blocks | 0 | 0 | 0 | No active blocker remains |
| Manual actions needed | 0 | 0 | 0 | No unresolved manual prompt remains |
| Source parity mismatch | 0 in final run | 0 in valid v2 run | 0 | Parity gate is necessary; DSE v1 proved copied vaults can be stale |
| Latest Sentinel blocker/major | 0/0 | 0/0 | 0/0 | Final output surface passes blocking quality gate |
| Deterministic output issues | 0 | 0 | 0 | Product-surface leakage/density/title checks passed |
| Historical provider failures | 1 OpenRouter refining failure | none in valid completion evidence | 2 OpenRouter refining failures | Provider smoothness is still not perfect |
| QA hard-fails during OOS | 2 | 1 | 0 | HGD/DSE still need bounded recovery discipline |
| Sentinel stop during OOS | 1 | 0 | 0 | HGD glossary conflict was caught correctly |
| Local recovery refinements | 5 | not a smooth path due DSE v1 rebuild + ch029 treatment | 2 | Long unattended runs are not ready |

## Hypotheses

| Hypothesis | OOS Result | Verdict |
|---|---|---|
| Source parity gate prevents invalid copied experiment measurements | DSE v1 failed parity; DSE v2 passed and produced valid measurement | Supported |
| Title/glossary/approved-output hardening reduces product-surface blocker/major defects | All latest OOS Sentinel reports show blocker/major `0/0` | Supported |
| CJK/Hanja parenthetical hardening prevents repeated IRS source-script leakage | IRS OOS did not repeat the earlier CJK/Hanja parenthetical hard-fail | Supported in this OOS slice |
| Boundary-aware glossary subset matching reduces false glossary misses | HGD `Enter` vs `Entering` false positive was fixed and did not block later OOS completion | Supported |
| Pipeline is ready for long unmonitored parallel production | OOS still needed recoveries, provider fallbacks, and treatments | Not supported |

## Production Recommendation

Recommended next production mode:

> Use bounded sequential production batches with explicit chapter ranges, scan/glossary gates, blocking Sentinel, deterministic output guardrails, source parity where experiment/copied vaults are involved, and major-run spot-checks. Do not enable broad unattended parallel translation/refinement/QA yet.

Allowed next production task:

- Deep Sea Embers continuation from current published `ch180` to `ch210`, after verifying exact range. This is `ch181-ch210`, which is 30 chapters, not 29.
- Use glossary batches of 5 chapters unless a scan gate shows an unusually high candidate count.
- Stop on provider failure, QA hard-fail, command length failure, validation failure, source mismatch, Sentinel blocker/major, or unexpected scope expansion.

Not recommended yet:

- Long unattended all-day production runs
- Broad parallel translate/refine/QA
- Publishing experiment output directly
- Disabling Sentinel or deterministic output guardrails to speed up runs

## Remaining Risks

- Provider empty-assistant output still recurs with OpenRouter during refining.
- HGD still required multiple recovery loops; novel-specific policy is improved but not fully smooth.
- DSE proved copied experiment vaults can silently contain stale/off-by-one raw source unless parity is checked.
- IRS OOS passed output quality, but smoothness still needed fallback/recovery and Gemini QA fallback.

## Next Safe Action

Close V6.34 documentation and proceed to the user-approved production request only as a bounded DSE batch after verifying `ch181-ch210` source/title readiness.
