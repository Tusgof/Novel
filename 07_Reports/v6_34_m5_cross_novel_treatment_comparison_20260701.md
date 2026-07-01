# V6.34 M5 Cross-Novel Treatment Comparison

Date: 2026-07-01

## Scope

This report compares the V6.34 in-sample treatment evidence across the three active novels:

- Horror Game Developer treatment: `v6-34-m5-hgd-treatment-v1`
- Deep Sea Embers treatment v2: `v6-34-m5-dse-treatment-v2`
- Infinite Regressor Stories treatment: `v6-34-m5-irs-treatment-v1`

All outputs were isolated experiment outputs. No production `05_Output`, production glossary, production ledger, or MoonRead reader content was used as treatment output.

## Summary Table

| Novel | In-Sample Chapters | Blocks Complete | Current Failed | Final Sentinel | Source Parity | Key Remaining Risk |
|---|---:|---:|---:|---|---|---|
| HGD | 10 | 10/10 single-block chapters | 0 | 0/0/0/0 | not applicable to copied-vault issue | QA hard-fails and omission recoveries during long run |
| DSE | 10 | 56/56 | 0 | 0/0/0/0 | 0 mismatches | one recovered OpenRouter empty assistant |
| IRS | 10 | 32/32 | 0 | 0/0/1/0 | 0 mismatches | CJK/Hanja parenthetical leakage caused two QA hard-fails; one minor glossary miss |

## Treatment Effects

| Defect Class | Evidence Before / During Treatment | Treatment Result | Layer |
|---|---|---|---|
| HGD title/H1 glossary drift | baseline stopped at `ch037` with Sentinel `0/2/0/0` | HGD treatment completed all 10 chapters with latest Sentinel `0/0/0/0` | Layer 0 + Layer 2 |
| Approved glossary parenthetical leakage | HGD treatment initially stopped at `ch024` | deterministic cleanup and rerun cleared leakage | Layer 0 |
| BOM-prefixed glossary parsing | HGD `ch132` exposed skipped glossary notes | parser fix cleared the chapter | Layer 0 |
| Stale experiment vault source | DSE treatment v1 used stale/off-by-one raw source | source-parity gate prevented invalid treatment measurement; DSE v2 completed cleanly | Layer 0 |
| Empty English `Footnotes:` source marker | IRS `ch020` leaked invented Thai glossary/category notes | bare trailing marker stripping fixed blocker and runtime Sentinel passed | Layer 1 |
| CJK/Hanja parenthetical source annotation | IRS `ch080` and `ch261` retained Hanja/Han in refined output | rerun from refine cleared both blocks, but no durable prevention exists yet | Layer 1 candidate |

## Metric Interpretation

### Output-surface quality

Treatment improved output-surface quality enough to continue the experiment:

- all three novels finished their in-sample treatment slice
- current failed blocks are zero across all three treatment runs
- final scoped Sentinel has no blocker/major findings
- DSE and HGD are fully clean under latest Sentinel
- IRS has one minor glossary coverage miss only

### Long-run smoothness

Treatment does not yet prove unattended long-run reliability:

- HGD treatment still needed historical failure recovery, QA hard-fails, and five QA omission literal-safe recoveries.
- DSE treatment still observed one recovered OpenRouter empty-assistant refining failure.
- IRS treatment still observed two QA hard-fails from CJK/Hanja parenthetical leakage and two recovered OpenRouter refining failures.

This means the treatment improved correctness gates, but the pipeline still needs a small pre-OOS hardening step before using OOS as generalization evidence.

## Decision

Milestone 5 treatment evidence is strong enough to move toward OOS, but not immediately. Before Milestone 6, add one narrow prevention rule:

- For non-CJK source/output projects, strip or reject parenthetical chunks made only of CJK/Hanja/Hangul source annotations after the Thai meaning has already been expressed.
- This should be implemented as a low-risk cleanup/validation rule with tests, not as a broad rewrite of translated prose.
- The rule is justified by repeated IRS in-sample hard-fails and should reduce avoidable manual recovery in OOS.

Do not add a broad glossary-policy change yet for the single IRS minor `Complete Memory` miss. Track it in OOS. If repeated, promote it into a Libra glossary coverage treatment.

## Next Safe Action

1. Implement the narrow non-CJK parenthetical annotation cleanup/guard with tests.
2. Rerun verification commands.
3. Update `PROJECT_BRAIN.md` / `IMPLEMENT_PLAN.md` with the rule and evidence.
4. Then open Milestone 6 OOS with no additional in-round tuning.
