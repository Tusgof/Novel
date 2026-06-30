# IMPLEMENT_PLAN.md

Last updated: 2026-07-01

## Overview

- **Start state**: The workspace has three active novels in the multi-novel system: Deep Sea Embers published through `ch180`, Horror Game Developer published through `ch270`, and Infinite Regressor Stories published through clean `ch050`. V6.34 Cross-Novel Libra - Blind Pilot Gate is active. Verified raw source pools currently exist for DSE `ch001-ch180`, HGD `ch001-ch270`, and IRS `ch001-ch394`. The old implementation plan was archived to `Backup_IMPLEMENT_PLAN/01072026_IMPLEMENT_PLAN.md`.
- **End state**: The pipeline has measured evidence that a cross-novel Libra - Pilot research loop improves consistency, translation quality, and long-run sustainability. The experiment samples from raw source across all three novels, completes one full baseline round before changes, applies only evidence-backed fixes at the correct layer, reruns treatment, measures metric movement, records research logs, and recommends the next production execution mode.
- **Total milestones**: 6
- **Estimated total effort**: XL

This plan is research-first. Experiment output is not production output and must not be published to MoonRead unless a separate production publication gate approves it.

Locked user decisions for this V6.34 plan:

- The goal is pipeline research and improvement, not absolute proof.
- A treatment passes only when evidence shows measurable improvement after a hypothesis-driven change.
- Sampling must come from verified raw source across all three novels; if raw source is incomplete, fetch or record the verified boundary before sampling.
- V6.34 artifacts are experiment-only unless a later production gate approves them.
- Every defect must be classified as cross-novel, language-level, novel-specific, run-local, or MoonRead-specific before a fix is promoted.
- Complete one experiment round before applying fixes, so the result can be analyzed honestly.
- The sample pool is cross-novel, not one-novel-first.
- The priority outcomes are consistency, translation quality, and sustainable long-run execution.

Current progress:

- Milestone 1 complete: experiment charter, measurement contract, stop/no-production rules, and charter research log are in place.
- Milestone 2 complete: raw source pools were audited for DSE, HGD, and IRS; fixed-seed sample manifest was created from raw source only.
- Milestone 3 stopped at a valid baseline gate: HGD baseline reached `ch037`, then Sentinel found major glossary coverage failures in experiment output. The next step is Milestone 4 analysis, not manual repair.
- Milestone 4 initial analysis complete: HGD `ch037` failure is title sidecar/glossary inconsistency, not body translation loss.

---

## V6.34 Measurement Contract

Official experiment question:

> Which pipeline changes measurably reduce cross-novel translation defects and improve sustainable long-run operation across Deep Sea Embers, Horror Game Developer, and Infinite Regressor Stories?

Primary success metrics:

| Metric | Evidence Source | Improvement Means |
|:--|:--|:--|
| Sentinel blocker/major/minor counts | scoped Sentinel reports for experiment outputs | blocker/major reach zero; minor count does not increase without explanation |
| Glossary coverage failures | Libra/glossary coverage reports and Sentinel glossary findings | fewer missing or leaked approved terms |
| Pronoun/name/title drift | deterministic guardrail reports, Sentinel findings, sampled manual review notes | fewer inconsistent variants and no known rejected variants |
| English/CJK/Thai numeral leakage | deterministic output guardrails and Sentinel reports | fewer leakage findings; blocker/major leakage reaches zero |
| Paragraph-density and formatting failures | output guardrail reports and sampled review notes | fewer dense/broken paragraphs without meaning loss |
| QA hard-fails | run ledger and status reports | fewer hard-fails per completed block |
| Provider failures and empty outputs | run ledger metadata and provider error reports | fewer failures/timeouts/empty outputs per completed block |
| Manual repairs | recovery reports and research logs | fewer manual artifact edits or force-accept decisions |
| Wall-clock time | run reports and command timestamps | faster completion for the same quality bar |
| Provider calls per completed block | run ledger provider/stage counts | fewer wasted calls without reducing quality |

Baseline rule: complete one planned baseline round before applying systemic fixes unless the run cannot continue safely because of provider outage, data corruption, source mismatch, or unexpected scope expansion.

Treatment rule: every treatment change must map to an observed baseline defect, a layer classification, and an expected metric movement before it is applied.

No-production rule: experiment output remains in isolated experiment vaults. It is not MoonRead content and is not production `05_Output` unless a later production publication gate explicitly approves it.

---

## Gap Analysis

Current state is strong enough for bounded production work, but not strong enough for long unattended runs. The main gaps are:

- The official experiment must sample across DSE, HGD, and IRS together from verified raw source, not from one novel or only from already translated chapters.
- The project needs one complete baseline experiment round before changing the pipeline, so the improvement can be measured instead of inferred.
- Recurrent issues still need clearer layer classification: multi-novel, language-level, novel-level, run-local, or MoonRead.
- Improvement must be proven by evidence: lower blocker/major defects, better glossary/name/pronoun consistency, cleaner formatting, fewer manual repairs, and smoother long-run execution.
- Research logs must be written per experiment round in `01_Research_Log/` using `RESEARCH_LOG_FORMAT.md`.

## Dependency Map

Sequential:

1. Lock experiment charter and metrics.
2. Verify/fetch raw source pools before sampling.
3. Generate reproducible cross-novel sample manifest.
4. Run one full baseline round without fixing mid-round.
5. Analyze defects and classify fix layer.
6. Apply surgical fixes.
7. Rerun treatment and compare against baseline.
8. Run out-of-sample generalization check.
9. Update docs and production recommendation.

Can run in parallel only after the manifest is locked:

- Read-only source-risk profiling for DSE/HGD/IRS.
- Report generation and metric extraction.
- Independent review of sampled output after each round.

Do not parallelize provider translation/refinement/QA as part of this plan unless a milestone explicitly approves a bounded benchmark.

---

## Milestone 1: Experiment Charter And Metrics Lock

**Goal**: Convert Libra - Pilot into a measurable research protocol before more execution happens.
**Dependencies**: none

| # | Task | Effort | Risk | Verification |
|:--|:-----|:------:|:----:|:-------------|
| 1.1 | Define the official V6.34 experiment question: which pipeline changes reduce cross-novel errors and improve sustainable long-run operation? | S | ✅ | `IMPLEMENT_PLAN.md` contains the experiment question and success metrics |
| 1.2 | Define metrics for baseline and treatment: blocker/major/minor Sentinel counts, glossary coverage failures, pronoun/name/title drift, English/CJK/Thai numeral leakage, paragraph-density failures, QA hard-fails, provider failures, manual repairs, wall-clock time, provider calls per completed block | M | ⚠️ | Metrics list exists and every metric has an evidence source |
| 1.3 | Define stop rule for research rounds: complete the planned round unless execution cannot continue safely because of provider outage, data corruption, source mismatch, or scope expansion | S | ✅ | Stop rule is documented in this plan |
| 1.4 | Define no-production rule: experiment output stays in isolated experiment vaults and is never published to MoonRead during V6.34 | S | ✅ | Plan states no MoonRead publication from experiment output |
| 1.5 | Create the first V6.34 research-log stub for the charter if no current log covers this refined protocol | S | ✅ | `01_Research_Log/<date>_novel_pipeline_v6_34_charter*.md` exists with 6 required sections |

**Milestone complete when**: The experiment has a written question, metrics, stop rule, no-production rule, and research-log evidence.

Status: complete. Evidence: `01_Research_Log/2026-06-30_novel_pipeline_v6_34_charter.md`.

---

## Milestone 2: Cross-Novel Raw Source And Sampling Gate

**Goal**: Build one reproducible sample manifest from raw source across all three novels before any translation round.
**Dependencies**: Milestone 1

| # | Task | Effort | Risk | Verification |
|:--|:-----|:------:|:----:|:-------------|
| 2.1 | Verify raw source pools for DSE, HGD, and IRS from `03_Raw/`, including min/max chapter, count, gaps, and unreadable files | M | ⚠️ | A source-pool audit report exists under `07_Reports/` |
| 2.2 | If any intended raw source pool is incomplete, fetch/prepare the missing scope before sampling; if upstream is unavailable, record the verified boundary | L | ⚠️ | Fetch report or boundary report exists; no silent sampling from partial unknown scope |
| 2.3 | Generate a fixed-seed stratified sample across all three novels: 20 chapters per novel, 10 in-sample and 10 out-of-sample, sampled from raw source only | M | ⚠️ | Sample manifest JSON/Markdown records seed, source pool, selected chapters, and strata |
| 2.4 | Validate that the sample is not hand-picked from previously translated or known-problem chapters, except where random selection naturally picked them | S | ✅ | Manifest includes selection method and exclusions |
| 2.5 | Create isolated experiment vaults/run IDs for all sampled chapters, separated from production `05_Output`, production MoonRead, and production ledger intent | M | ⚠️ | Experiment paths and run IDs are listed; production output is unchanged |

**Milestone complete when**: A reproducible cross-novel sample manifest exists and every sampled chapter comes from verified raw source.

Status: complete. Evidence: `07_Reports/v6_34_m2_source_pool_and_sample_manifest_20260701.md` and `01_Research_Log/2026-06-30_novel_pipeline_v6_34_source_pool_sampling.md`.

---

## Milestone 3: Full Baseline Round

**Goal**: Run one complete baseline round on the cross-novel in-sample set before applying fixes, so failure modes are measured honestly.
**Dependencies**: Milestone 2

| # | Task | Effort | Risk | Verification |
|:--|:-----|:------:|:----:|:-------------|
| 3.1 | Run scan-only and glossary classification/approval gates for the 30 in-sample chapters across DSE/HGD/IRS using isolated experiment state | L | ⚠️ | Each run has `fetched`, `glossary_scanned`, and `glossary_approved` evidence; no production glossary mutation unless explicitly approved |
| 3.2 | Run baseline translation/refine/QA/format/Sentinel for the 30 in-sample chapters without applying mid-round systemic fixes | XL | ⚠️ | Status reports show completed/failed state for every in-sample chapter |
| 3.3 | Record all failures as data, including provider failures, QA hard-fails, Sentinel blockers/majors, glossary coverage misses, formatting failures, and manual repair needs | M | ⚠️ | Baseline report contains all outcomes, not only passes |
| 3.4 | Run deterministic output guardrails and Sentinel on the experiment outputs only | M | ⚠️ | Guardrail/Sentinel reports exist and are scoped to experiment outputs |
| 3.5 | Write and push a research log for the baseline round | S | ✅ | `01_Research_Log/` log exists, has 6 sections, and git push succeeds |

**Milestone complete when**: The in-sample baseline round is complete or safely stopped with a documented unrecoverable reason, and all observed failures are recorded before fixes.

Status: safely stopped at gate. Scan-only and baseline glossary gates are complete. HGD baseline translation reached `ch037`, then stopped on Sentinel major findings for missing `Velora Art Museum` glossary coverage. Evidence: `01_Research_Log/2026-06-30_novel_pipeline_v6_34_m3_scan_glossary_gate.md`, `01_Research_Log/2026-06-30_novel_pipeline_v6_34_m3_hgd_baseline_stop.md`, and `07_Reports/v6_34_m3_baseline_glossary_gate_decisions_20260701.md`. This is sufficient baseline failure data to start Milestone 4 analysis without repairing the baseline output.

---

## Milestone 4: Defect Analysis And Layer Classification

**Goal**: Decide what to fix and where, based on baseline evidence instead of intuition.
**Dependencies**: Milestone 3

| # | Task | Effort | Risk | Verification |
|:--|:-----|:------:|:----:|:-------------|
| 4.1 | Classify every baseline defect by layer: Layer 0 multi-novel, Layer 1 language playbook, Layer 2 novel profile/vault, Layer 3 run-local recovery, Layer 4 MoonRead reader surface | M | ⚠️ | Defect table exists with one layer per defect |
| 4.2 | Identify which defects are repeated across novels versus novel-specific | M | ⚠️ | Cross-novel comparison table exists |
| 4.3 | Convert repeated defects into testable hypotheses with expected metric movement | M | ⚠️ | Each proposed fix states expected measurable improvement |
| 4.4 | Prioritize fixes by low effort and medium/high impact, avoiding changes that reduce translation quality | M | ⚠️ | Prioritization table exists with selected treatment set |
| 4.5 | Decide which fixes are allowed in the treatment round and which are deferred | S | ✅ | Treatment scope is explicitly listed |

**Milestone complete when**: There is a reviewed treatment plan that maps each selected fix to evidence, layer, expected metric improvement, and verification method.

Status: initial analysis complete, treatment selection pending. Evidence: `07_Reports/v6_34_m4_initial_defect_analysis_hgd_ch037_20260701.md` and `01_Research_Log/2026-06-30_novel_pipeline_v6_34_m4_initial_analysis.md`.

---

## Milestone 5: Treatment Implementation And Measured Rerun

**Goal**: Apply only selected fixes, rerun the same in-sample set, and prove whether the pipeline improved.
**Dependencies**: Milestone 4

| # | Task | Effort | Risk | Verification |
|:--|:-----|:------:|:----:|:-------------|
| 5.1 | Implement Layer 0 and Layer 1 fixes first when evidence shows defects are cross-novel or language-level | L | ⚠️ | Code/docs/tests identify affected layer and pass targeted verification |
| 5.2 | Implement Layer 2 novel-specific fixes only for defects proven novel-specific | M | ⚠️ | Novel profile/vault/glossary/playbook changes are scoped to the right novel |
| 5.3 | Keep run-local repairs out of shared policy unless repeated evidence justifies promotion | S | ✅ | Treatment report lists run-local items separately |
| 5.4 | Rerun the same 30 in-sample chapters under treatment conditions | XL | ⚠️ | Treatment status reports exist for all in-sample chapters |
| 5.5 | Compare baseline versus treatment using the locked metrics | M | ⚠️ | Comparison report shows numeric movement for every metric |
| 5.6 | Write and push a treatment research log | S | ✅ | Research log exists, follows format, and is pushed |

**Milestone complete when**: Treatment produces measurable evidence of improvement or clear evidence that the hypothesis failed.

---

## Milestone 6: Out-Of-Sample Generalization Check And Production Recommendation

**Goal**: Measure whether the treatment generalizes to untouched chapters across all three novels, then recommend the next production execution mode.
**Dependencies**: Milestone 5

| # | Task | Effort | Risk | Verification |
|:--|:-----|:------:|:----:|:-------------|
| 6.1 | Run scan/glossary gates for the 30 out-of-sample chapters across DSE/HGD/IRS in isolated experiment state | L | ⚠️ | OOS glossary reports and ledger records exist |
| 6.2 | Run OOS translation/refine/QA/format/Sentinel without tuning on OOS failures mid-round | XL | ⚠️ | OOS status reports cover every selected chapter |
| 6.3 | Compare OOS metrics against baseline and treatment expectations | M | ⚠️ | OOS report states pass/fail for each hypothesis |
| 6.4 | Produce a production recommendation: safe bounded sequential, safe bounded parallel slice, or not ready to scale | M | ⚠️ | Recommendation report lists evidence and remaining risks |
| 6.5 | Update `PROJECT_BRAIN.md` Current Verified State, Known Risks, and Next Safe Action | S | ✅ | `PROJECT_BRAIN.md` matches verified results |
| 6.6 | Update `ARCHITECTURE.md` only if stable layer/ownership rules changed | S | ✅ | Architecture diff is absent or contains only durable structure changes |
| 6.7 | Write and push final V6.34 research log and commit the plan/results | S | ✅ | Research log and docs are committed and pushed |

**Milestone complete when**: OOS evidence shows whether the treatment generalizes well enough, and the project has a clear next production mode backed by reports.

---

## Execution Notes

- **Blocked items**:
  - Production publication from experiment output is blocked by design.
  - Long unattended production translation remains blocked until V6.34 produces evidence that the pipeline can sustain it.
  - Any provider routing change remains blocked unless explicitly approved and measured.

- **Decision points**:
  - After Milestone 3: decide treatment hypotheses based on actual baseline evidence.
  - After Milestone 5: decide whether treatment improved enough to run OOS, needs revision, or should be rejected.
  - After Milestone 6: decide next production mode for DSE/HGD/IRS.

- **Risk checkpoints**:
  - After sampling: verify raw source boundaries and no accidental hand-picking.
  - After baseline: verify no fixes were applied before analysis.
  - After treatment: verify metric movement, not just anecdotal quality.
  - After OOS: verify no overfitting to in-sample chapters.

- **Operating model**:
  - Codex plans, reviews, verifies, and writes the worker prompts.
  - Workers execute bounded tasks only.
  - Worker reports are claims until disk state, tests, reports, and diffs verify them.
  - Every experiment round gets one research log in `01_Research_Log/` and must be pushed.

- **Standard verification**:
  - `git diff --check`
  - `python -m compileall novel_pipeline`
  - `python test_translation.py`
  - `novel-pipeline --config ".system/config.yaml" preflight`
  - scoped output guardrails for touched experiment outputs
  - scoped Sentinel for touched experiment outputs
  - MoonRead checks only if a separate production publication gate changes reader content

## Compatibility Notes Kept For Regression Tests

These notes preserve durable lessons that existing tests expect while the active roadmap stays focused on V6.34.

- V6.17 Incident Lessons: HGD Titles And Format
- HGD title fallback risk guarded by title sidecars.
- Completed Milestone: V6.17.1 HGD Title And Format Re-Audit.
- Completed Milestone: V6.18 Translation Speed Without Quality Loss.
- AI formatting remains primary; use `C:\Users\ASUS\Downloads\good format.md` as the style reference for paragraph spacing, dialogue, thoughts, sound effects, and UI/system formatting.
