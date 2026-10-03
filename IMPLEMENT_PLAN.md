# IMPLEMENT_PLAN.md

Last updated: 2026-10-03

## Overview

- **Start state**: The workspace has three active novels in the multi-novel system: Deep Sea Embers output and MoonRead are verified through `ch281`, Horror Game Developer is published through `ch270`, and Infinite Regressor Stories is published through clean `ch050`. V6.34 Cross-Novel Libra - Blind Pilot Gate is complete. The old implementation plan was archived to `Backup_IMPLEMENT_PLAN/01072026_IMPLEMENT_PLAN.md`.
- **End state**: The pipeline has measured evidence that a cross-novel Libra - Pilot research loop improves consistency, translation quality, and long-run sustainability. The experiment samples from raw source across all three novels, completes one full baseline round before changes, applies only evidence-backed fixes at the correct layer, reruns treatment, measures metric movement, records research logs, recommends the next production execution mode, and proves that the follow-up DSE production continuation can complete through `ch210` under the same gates.
- **Total milestones**: 7
- **Estimated total effort**: XL

V6.36 Lean Pipeline research is complete. V6.38 now makes the Lean engine the
selected production dispatch path for every registered novel. OOS and the full
Libra - Pilot Gate remain optional research methods when promoting a shared-layer
change; they are not mandatory setup steps for every novel.

## Current Session Work Order: Lean Runtime Replacement And Layer Separation

This session has three explicit scopes:

1. Make the root `novel_pipeline/` package the only canonical runtime and keep
   novel-local imports as compatibility shims only.
2. Enforce explicit selected-novel context for provider helpers, working
   directories, Sentinel, staging, and CLI commands; reject DSE/sibling
   fallback and legacy Lean stage commands.
3. Separate project-layer architecture from novel-layer configuration in the
   canonical architecture/control documents, then verify the migration without
   starting a paid translation or MoonRead publication.

Session gates:

- No provider-backed translation or publication is authorized by this migration
  milestone.
- A real Lean run must stage candidate output, stop on provider/QA/validation/
  Sentinel/manual/scope failure, and promote only after the blocking gate passes.
- Existing source, output, logs, reports, and dirty WIP remain untouched.
- The completed scope requires independent tests, control-document updates, and
  a commit/push of the intended changes.

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

- Clean & Simple phase completed on 2026-10-01: removed the unused local dashboard, employee aliases, dashboard-only docs/assets, CLI operator command, and obsolete dashboard tests. Direct pipeline CLI, reports, recovery, Sentinel/guardrails, and MoonRead remain. Historical dashboard reports were retained as evidence. Verification: compileall and full `test_translation.py` passed. Next: architecture convergence review.
- V6.36 started on 2026-10-02: added opt-in full provider-call tracing and an isolated lean-pipeline harness. The harness keeps block splitting for transport safety, projects approved chapter-relevant glossary terms into a source copy before literal translation, refines the assembled chapter once, runs chapter-level QA and formatting, and harvests glossary candidates as `proposed` only. The HGD `ch001` v4 smoke completed literal/refinement but stopped at blocking QA when refinement removed an approved term; no production output changed. The smallest cleaner repair passed regression tests, but HGD v5 stopped on an empty OpenRouter refinement response. Evidence: `01_Research_Log/2026-10-02_v6_36_lean_pilot_blocked_credit.md`, `01_Research_Log/2026-10-03_v6_36_lean_glossary_projection_smoke.md`, and `01_Research_Log/2026-10-03_v6_36_hgd_lean_followup_blocked.md`.
- Current session setup completed One Hit Kill Swordmaster as an isolated WNTL-backed vault and fetched/validated 95/95 raw chapters. Its fixed 10-chapter experiment sample was locked, but in-sample Lean stopped at QA provider empty output; OOS was not started. Evidence: `07_Reports/v6_36_one_hit_kill_swordmaster_setup_and_lean_pilot_20261003.md`.
- Current session recursive organization inventory covered every workspace subtree. Production/evidence/backups were preserved; generated-state ignore rules were added. Host deletion policy rejected recursive cache deletion, so no physical deletion is claimed. Evidence: `07_Reports/workspace_recursive_organization_20261003.md`.
- The V6.36 pilot scope was simplified on 2026-10-03: OHKS and HGD use a bounded pilot without OOS. OOS/Libra remains an optional cross-novel research method only for promoting shared-layer changes. The lean QA harness now exercises configured fallbacks and its regression test passes.

- Milestone 1 complete: experiment charter, measurement contract, stop/no-production rules, and charter research log are in place.
- Milestone 2 complete: raw source pools were audited for DSE, HGD, and IRS; fixed-seed sample manifest was created from raw source only.
- Milestone 3 stopped at a valid baseline gate: HGD baseline reached `ch037`, then Sentinel found major glossary coverage failures in experiment output. The next step is Milestone 4 analysis, not manual repair.
- Milestone 4 initial analysis complete: HGD `ch037` failure is title sidecar/glossary inconsistency, not body translation loss.
- Milestone 4 treatment selected: add deterministic title/H1 glossary validation and correct the HGD `Velora Art Museum` title map to the approved glossary term. Milestone 5 treatment rerun is next.
- Milestone 5 started and safely stopped: HGD treatment vault reached `ch024`, then Sentinel blocked approved glossary English parenthetical leakage. This is new treatment evidence, not production output.
- Milestone 5 checkpoint passed through the original baseline stop point: `ch024` and `ch037` now both pass scoped Sentinel `0/0/0/0` in the HGD treatment vault.
- Milestone 5 HGD treatment slice completed: all 10 HGD in-sample chapters complete, latest scoped Sentinel `0/0/0/0` for every chapter, and current failed blocks none. This does not complete the whole cross-novel M5 treatment because DSE/IRS treatment slices still need a decision.
- Milestone 5 HGD comparison completed: baseline stopped after `ch037` with Sentinel `0/2/0/0`; treatment completed all 10 HGD in-sample chapters with latest scoped Sentinel `0/0/0/0`. Decision: continue DSE/IRS treatment measurement in isolated experiment vaults before out-of-sample M6, because output-surface defects improved but long-run smoothness is still unproven.
- Milestone 5 DSE treatment attempt stopped before valid measurement: copied experiment vault `v6_34_m5_dse_treatment_v1` contained stale/off-by-one raw source for all 10 sampled chapters. Added `scripts/verify_experiment_source_parity.py`; DSE treatment must be rebuilt from current production raw and pass parity before provider calls.
- Milestone 5 DSE treatment v2 completed validly: rebuilt from current production raw/title sidecars and manifest, source parity stayed at `0` mismatches, all 10 DSE in-sample chapters completed (`56/56` blocks), latest scoped Sentinel is `0/0/0/0` for every sampled chapter, and current failed blocks are none. One OpenRouter empty-assistant refining failure remains as historical recovered provider-risk evidence. Next: run IRS treatment measurement before OOS M6.
- Milestone 5 IRS treatment stopped at `ch020`: source parity passed, scan-only and glossary approval gate completed, and `ch020` completed 4/4 blocks, but scoped Sentinel found blocker `glossary_note_leakage` from provider-invented glossary/category notes after an empty source `Footnotes:` marker. Next: implement the smallest empty-footnote-marker prevention and ensure runtime Sentinel is enabled before rerunning `ch020`.
- Milestone 5 IRS `ch020` blocker repaired and prevention verified: non-CJK source block splitting strips only bare trailing `Footnotes:` markers, IRS config now includes blocking Sentinel, and rerun `ch020-block-004` passed QA retry 0 with runtime Sentinel `0/0/0/0`. Next: continue IRS treatment from `ch067`.
- Milestone 5 IRS treatment completed validly: all 10 IRS in-sample chapters completed (`32/32` blocks), current failed blocks none, manual actions none, source parity `0` mismatches, deterministic output checks passed, and final scoped Sentinel is `0/0/1/0`. Remaining evidence for comparison: CJK/Hanja parenthetical leakage caused two QA hard-fails, OpenRouter refining failed twice but recovered, and one `Complete Memory` minor glossary miss remains. Next: compare HGD + DSE + IRS treatment results before opening OOS Milestone 6.
- Milestone 5 cross-novel comparison completed: HGD/DSE/IRS treatment all reached current failed blocks `0` and no Sentinel blocker/major findings. Decision: before OOS, add one narrow non-CJK CJK/Hanja parenthetical annotation cleanup/guard because IRS repeated this hard-fail pattern; do not broaden glossary policy for the single `Complete Memory` minor miss yet.
- Milestone 5 pre-OOS CJK/Hanja parenthetical hardening completed: non-CJK `split_blocks()` now normalizes quoted source-script terms followed by English `meaning ...` and strips parenthetical source-script annotations. Targeted tests, compileall, `test_translation.py`, and raw IRS `ch080`/`ch261` probes passed. Next: open Milestone 6 OOS.
- Milestone 6.1 OOS scan/glossary gate completed: DSE/HGD/IRS experiment vaults passed source parity `0` mismatches, scan-only completed, candidate counts were DSE `34`, HGD `17`, IRS `155`, and `glossary_approved` records were committed for all 30 OOS chapters without approving new OOS terms. Next: prepare missing experiment-local IRS title sidecars, then run M6.2 OOS translation without tuning mid-round.
- Milestone 6.2 OOS translation started and stopped validly on HGD `ch131`: HGD OOS completed `ch015`, `ch046`, `ch060`, `ch101`, and `ch131`, then blocking Sentinel found major `glossary_coverage_missing` because output used `ภาคส่วนกักกัน` for source `Containment Department` while `Containment Department.md` requires `แผนกกักกัน`. Cause is a HGD glossary conflict with `Containment Sector.md`, not provider failure. Next: M6.3 analysis before any OOS repair/resume.
- Milestone 6.3 analysis completed: selected treatment is Layer 0 source-surface collision detection in `glossary-conflicts` plus Layer 2 HGD cleanup of `Containment Sector.md` aliases. No output patching or OOS resume until the treatment passes tests.
- Milestone 6.3 treatment implemented: `glossary-conflicts` now reports approved original/alias source-surface collisions with different Thai terms, HGD `Containment Sector.md` no longer aliases `Containment Department`, tests passed, and rerun `ch131-block-001` from refine cleared Sentinel (`0/0/0/0`). Next: resume HGD OOS from `ch153`.
- Milestone 6.2 HGD OOS resumed and stopped again at `ch184-block-001`: `ch153` completed, then QA hard-failed after retry 2 on missing `ปุ่ม Enter` and internal-thought mistranslation (`สะกดรอยตาม`). No force-accept or repair was applied. Next: analyze `ch184` before any rerun.
- Milestone 6.3 ch184 analysis completed: `ปุ่ม Enter` was a Layer 0 false glossary expectation caused by `_resolve_glossary_subset()` matching `Enter` inside `Entering`; `สะกดรอยตาม` was run-local semantic drift. Selected treatment: boundary-aware glossary subset matching plus rerun `ch184-block-001` from refine.
- Milestone 6.3 ch184 treatment implemented: glossary subset matching is now boundary-aware for alphabetic keys and tested; first rerun from refine false-passed on semantic drift, so `ch184-block-001` was rerun from translate and now passes QA retry `0`, Sentinel `0/0/0/0`, and spot-check for the drift phrase. Next: resume HGD OOS from `ch192`.
- Milestone 6.2 HGD OOS resumed and stopped at `ch192-block-001`: QA hard-failed after retry 2 because peer dialogue used `คุณ` where HGD policy expects casual `นาย`. No force-accept or repair was applied. Next: analyze `ch192` before any rerun.
- Milestone 6.3 ch192 treatment implemented: literal-safe omission recovery now applies a narrow HGD-only peer-address repair for observed high-confidence patterns; regression tests pass, `ch192-block-001` passed QA retry `2`, runtime Sentinel `0/0/0/0`, and bad phrase spot-checks are clear. Next: resume HGD OOS from `ch226`.
- Milestone 6.2 HGD OOS completed: all 10 locked HGD OOS chapters are complete, current failed blocks none, manual actions none, latest scoped Sentinel `0/0/0/0` for every chapter, and experiment-output checks found no Han Chinese body text, provider/meta leakage, or quote-only lines. Smoothness remains imperfect because the run required multiple treatment/recovery loops. Next: run DSE OOS.
- Milestone 6.2 DSE OOS safely stopped before valid measurement: `v6-34-m6-dse-oos-v1` completed 28 blocks through `ch088`, but final assembly exposed stale/off-by-one experiment raw source. Source parity against production raw now reports `10/10` mismatches for the locked DSE OOS chapters. Treat all partial DSE OOS output from this vault as invalid measurement data. Next: rebuild a fresh DSE OOS vault from current production raw/title sidecars, require source parity `0`, then restart DSE OOS from the beginning.
- Milestone 6.3 DSE `ch029-block-005` treatment implemented: rebuilt DSE OOS v2 passed source parity `0`, scan/glossary gate completed with no new OOS terms approved, then QA hard-failed on Chinese annotation leakage in an author promo (`[走进不科学]`). Added narrow output-side source-script annotation cleanup, tests passed, rerun from refine passed QA retry 2, and `ch029` output now exists with no Han Chinese. Next: resume DSE OOS v2 from `ch047`.
- Milestone 6.2 DSE OOS completed validly: `v6-34-m6-dse-oos-v2` completed all 10 locked DSE OOS chapters (`55/55` blocks), current failed blocks none, manual actions none, source parity `0`, output guardrails passed, and final outputs exist in the isolated experiment vault. During final verification, `ch174` exposed a provider-hallucinated title-like body paragraph; final assembly now removes standalone title-like paragraphs anywhere in the body when the H1 title is authoritative. Next: run IRS OOS.
- Milestone 6.2 IRS OOS completed validly: `v6-34-m6-irs-oos-v1` completed all 10 locked IRS OOS chapters (`33/33` blocks), current failed blocks none, manual actions none, source parity `0`, deterministic experiment-output checks passed, and latest scoped Sentinel is `0/0/0/0` for every sampled chapter. Smoothness remains imperfect: 2 OpenRouter empty-assistant refining failures recovered, 2 local recovery refinements occurred, QA used Gemini Flash fallback 3 times, and formatting used local fallback 4 times. Next: compare HGD + DSE + IRS OOS results and make the M6 production recommendation.
- Milestone 6.3-6.7 OOS comparison and production recommendation completed: HGD, DSE, and IRS OOS all finished with current failed blocks `0`, source parity `0` in final valid runs, deterministic output issues `0`, and latest Sentinel blocker/major `0/0`. Recommendation: proceed with bounded sequential production batches under existing gates; do not enable broad unattended parallel translate/refine/QA yet. Next: close V6.34 final documentation and verify git state before the requested DSE continuation.
- Post-V6.34 DSE continuation complete: `dse-ch181-ch185-v1`, `dse-ch186-ch190-v1`, `dse-ch191-ch195-v1`, `dse-ch196-ch200-v1`, `dse-ch201-ch205-v1`, and `dse-ch206-ch210-v1` completed and MoonRead publishes DSE through `ch210`. Do not start another production batch without a new explicit range.
- Post-V6.34 DSE follow-up continuation complete: `dse-ch231-ch235-v1`, `dse-ch236-ch240-v1`, `dse-ch241-ch245-v1`, `dse-ch246-ch250-v1`, and `dse-ch251-v1` completed and MoonRead publishes DSE through `ch251`. Checkpoint: `07_Reports/dse_ch231_ch251_production_checkpoint_20260709.md`.
- Milestone 7 complete: post-experiment production closure validated the V6.34 recommendation with bounded sequential DSE batches through `ch210`, documented checkpoints, scoped Sentinel, output guardrails, MoonRead publish verification, and clean git push.

Current scope: V6.38 Lean runtime replacement and layer separation. V6.35 Re:Zero production remains paused; it is not the active migration work order.

## V6.35: Re:Zero Chapter-Isolated Parallel Pilot

**Goal**: Publish verified Re:Zero fanfic chapters through `ch010`, while proving that at most two chapter-isolated Luna workers can reduce wall time without shared-state corruption or quality-gate regression.
**Dependencies**: Re:Zero setup/pilot complete; `ch001-ch002` published; shared ledger locking and timing telemetry verified.

| # | Task | Effort | Risk | Verification |
|:--|:-----|:------:|:----:|:-------------|
| 35.1 | Complete: finish and independently accept `ch003`; rerun the earliest broken stage for the observed formatter reintroduction before publication | L | ⚠️ | All 11 blocks complete, output guardrail passes, Sentinel blocker/major `0/0`, spot-check passes |
| 35.2 | Complete: review and approve glossary/title inputs for `ch005-ch010` sequentially, then freeze glossary mutation before parallel work | M | ⚠️ | Each chapter run has fetched/scanned/approved evidence and a title sidecar; no translation starts before approval |
| 35.3 | In progress: run at most two Luna panes on separate chapters and run IDs with disjoint artifacts | XL | ⚠️ | Concurrent append regression test stays green; ledger decodes; no duplicate/missing records or path collisions |
| 35.4 | In progress: inspect, gate, and publish completed chapters strictly in chapter order, one chapter per MoonRead update | XL | ⚠️ | Per chapter: no current failure/manual prompt, guardrail + Sentinel + spot-check pass, MoonRead publish checks pass |
| 35.5 | Record wall/provider/stage timing and compare sequential `ch003` against chapter-isolated pairs | M | ✅ | Status/checkpoint reports include timing coverage, stage/provider seconds, retries, failures, and wall time |
| 35.6 | Decide whether two-pane chapter isolation becomes a stable production option or falls back to sequential | S | ⚠️ | Evidence report states quality, collision, provider-failure, and wall-time result |

**Milestone complete when**: `ch003-ch010` are published and production URLs verified, every chapter passes blocking gates, timing evidence exists, and the parallelism decision is recorded without enabling stage-level concurrency.

Status: blocked on provider availability. Tasks 35.1 and 35.2 are complete; `ch008` is live at commit `5e3fbfc`. `ch009` is `5/12` with block `006` failed at `translate`; `ch010` is `1/19` with block `002` failed at `qa`. Neither incomplete chapter has final output or publication. Resume from the recorded failed stages after OpenRouter can fund the configured 12,000-token route and Codex CLI fallback authentication is restored. Parallel artifacts and ledger writes remained isolated, but provider exhaustion prevents further execution.

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

Status: complete. Evidence: `07_Reports/v6_34_m4_initial_defect_analysis_hgd_ch037_20260701.md`, `07_Reports/v6_34_m4_treatment_selection_title_glossary_20260701.md`, `01_Research_Log/2026-06-30_novel_pipeline_v6_34_m4_initial_analysis.md`, and `01_Research_Log/2026-07-01_novel_pipeline_v6_34_m4_treatment_selection.md`.

---

## Milestone 5: Treatment Implementation And Measured Rerun

**Goal**: Apply only selected fixes, rerun the same in-sample set, and prove whether the pipeline improved.
**Dependencies**: Milestone 4

| # | Task | Effort | Risk | Verification |
|:--|:-----|:------:|:----:|:-------------|
| 5.1 | Implement Layer 0 and Layer 1 fixes first when evidence shows defects are cross-novel or language-level | L | ⚠️ | Code/docs/tests identify affected layer and pass targeted verification |
| 5.2 | Implement Layer 2 novel-specific fixes only for defects proven novel-specific | M | ⚠️ | Novel profile/vault/glossary/playbook changes are scoped to the right novel |
| 5.3 | Keep run-local repairs out of shared policy unless repeated evidence justifies promotion | S | ✅ | Treatment report lists run-local items separately |
| 5.4 | Before every treatment resume, verify experiment raw source parity against production raw for the exact sampled chapters | S | ⚠️ | `scripts/verify_experiment_source_parity.py` reports zero mismatches |
| 5.5 | Rerun the same 30 in-sample chapters under treatment conditions | XL | ⚠️ | Treatment status reports exist for all in-sample chapters |
| 5.6 | Compare baseline versus treatment using the locked metrics | M | ⚠️ | Comparison report shows numeric movement for every metric |
| 5.7 | Write and push a treatment research log | S | ✅ | Research log exists, follows format, and is pushed |

**Milestone complete when**: Treatment produces measurable evidence of improvement or clear evidence that the hypothesis failed.

Status: complete. Layer 0 title/H1 glossary validation, Layer 0 BOM-tolerant glossary parsing, Layer 0 redacted-rank repair, Layer 2 HGD title-map corrections, Layer 2 HGD rejected-variant notes, deterministic approved-glossary parenthetical cleanup, source-parity validation for copied experiment vaults, empty trailing `Footnotes:` stripping for non-CJK sources, and pre-OOS CJK/Hanja parenthetical annotation cleanup for non-CJK source are implemented and unit-tested where code changed. HGD treatment rerun completed all 10 HGD in-sample chapters with current failed blocks none and latest scoped Sentinel `0/0/0/0` for every chapter. HGD baseline-vs-treatment comparison found real improvement in measured product-surface defects, but long-run smoothness remains unproven because treatment still needed historical failures, QA hard-fails, and five QA omission recoveries. DSE treatment v2 completed all 10 DSE in-sample chapters after rebuilding from current production raw/source title sidecars and requiring source parity `0` mismatches. IRS treatment completed all 10 IRS in-sample chapters with source parity `0` mismatches, no current failed blocks, deterministic output checks passed, and final scoped Sentinel `0/0/1/0`. Cross-novel comparison says output-surface quality is improved enough to move toward OOS after the CJK/Hanja parenthetical hardening. Evidence: `07_Reports/v6_34_m5_hgd_treatment_early_stop_20260701.md`, `07_Reports/v6_34_m5_hgd_treatment_checkpoint_ch024_ch037_20260701.md`, `07_Reports/v6_34_m5_hgd_treatment_ch132_bom_glossary_repair_20260701.md`, `07_Reports/v6_34_m5_hgd_treatment_completion_20260701.md`, `07_Reports/v6_34_m5_hgd_baseline_vs_treatment_comparison_20260701.md`, `07_Reports/v6_34_m5_dse_treatment_source_mismatch_stop_20260701.md`, `07_Reports/v6_34_m5_dse_treatment_v2_completion_20260701.md`, `07_Reports/v6_34_m5_irs_treatment_ch020_stop_20260701.md`, `07_Reports/v6_34_m5_irs_footnote_marker_prevention_20260701.md`, `07_Reports/v6_34_m5_irs_treatment_completion_20260701.md`, `07_Reports/v6_34_m5_cross_novel_treatment_comparison_20260701.md`, `07_Reports/v6_34_m5_pre_oos_cjk_parenthetical_hardening_20260701.md`, `01_Research_Log/2026-07-01_novel_pipeline_v6_34_m5_hgd_treatment_early_stop.md`, `01_Research_Log/2026-07-01_novel_pipeline_v6_34_m5_hgd_treatment_checkpoint.md`, `01_Research_Log/2026-07-01_novel_pipeline_v6_34_m5_hgd_ch132_bom_glossary_repair.md`, `01_Research_Log/2026-07-01_novel_pipeline_v6_34_m5_hgd_treatment_completion.md`, `01_Research_Log/2026-07-01_novel_pipeline_v6_34_m5_hgd_baseline_vs_treatment_comparison.md`, `01_Research_Log/2026-07-01_novel_pipeline_v6_34_m5_dse_source_mismatch_stop.md`, `01_Research_Log/2026-07-01_novel_pipeline_v6_34_m5_dse_treatment_v2_completion.md`, `01_Research_Log/2026-07-01_novel_pipeline_v6_34_m5_irs_treatment_ch020_stop.md`, `01_Research_Log/2026-07-01_novel_pipeline_v6_34_m5_irs_footnote_marker_prevention.md`, `01_Research_Log/2026-07-01_novel_pipeline_v6_34_m5_irs_treatment_completion.md`, `01_Research_Log/2026-07-01_novel_pipeline_v6_34_m5_cross_novel_treatment_comparison.md`, and `01_Research_Log/2026-07-01_novel_pipeline_v6_34_m5_pre_oos_cjk_parenthetical_hardening.md`. Next action: open Milestone 6 OOS with locked out-of-sample chapters and no mid-round tuning.

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

Status: complete. M6.1 scan/glossary gate is complete. M6.2 HGD, DSE, and IRS OOS all completed. M6.3-6.4 comparison/recommendation is complete: production can proceed as bounded sequential batches with existing gates, but broad unattended parallel translate/refine/QA remains not recommended. M6.5-6.7 documentation, research log, and plan updates are complete. Evidence: `07_Reports/v6_34_m6_oos_scan_glossary_gate_20260701.md`, `07_Reports/v6_34_m6_hgd_oos_completion_20260701.md`, `07_Reports/v6_34_m6_dse_oos_source_parity_stop_20260701.md`, `07_Reports/v6_34_m6_dse_oos_ch029_source_script_treatment_20260701.md`, `07_Reports/v6_34_m6_dse_oos_completion_20260701.md`, `07_Reports/v6_34_m6_irs_oos_completion_20260701.md`, `07_Reports/v6_34_m6_cross_novel_oos_comparison_20260701.md`, and matching research logs. Next action: keep production work bounded and start no further batch without a new explicit range.

---

## Milestone 7: Post-Experiment Production Closure

**Goal**: Validate the V6.34 recommendation in real production by finishing the requested DSE continuation through `ch210` with bounded sequential batches, scoped verification, MoonRead publication, and clean git state.
**Dependencies**: Milestone 6

| # | Task | Effort | Risk | Verification |
|:--|:-----|:------:|:----:|:-------------|
| 7.1 | Run DSE continuation only as 5-chapter scan/glossary/translation batches from `ch181` through `ch210` | XL | ⚠️ | Checkpoint reports exist for `ch181-ch185`, `ch186-ch190`, `ch191-ch195`, `ch196-ch200`, `ch201-ch205`, and `ch206-ch210` |
| 7.2 | Keep runtime Sentinel, deterministic output guardrails, and major-run spot-checks active for every production batch | M | ⚠️ | Each checkpoint records output guardrail and scoped Sentinel results |
| 7.3 | Publish each verified batch to MoonRead and run scoped `publish:verify` | M | ⚠️ | MoonRead reports show DSE through `ch210`, scoped Sentinel `0/0/0/0`, lint/build/smoke passed |
| 7.4 | Update `PROJECT_BRAIN.md`, `IMPLEMENT_PLAN.md`, and stable architecture notes if rules changed | S | ✅ | Root docs reflect DSE through `ch210` and no automatic next batch |
| 7.5 | Commit and push glossary and publication changes in clean, reviewable commits | S | ✅ | Git history contains glossary/publish commits through `ch210`, and `git status` is clean after push |

**Milestone complete when**: DSE is published through `ch210`, all scoped verification gates pass, docs no longer point at stale `ch180/ch200` production state, and no next production batch is started automatically.

Status: complete. Evidence: `07_Reports/dse_ch181_ch185_production_checkpoint_20260701.md`, `07_Reports/dse_ch186_ch190_production_checkpoint_20260701.md`, `07_Reports/dse_ch191_ch195_production_checkpoint_20260701.md`, `07_Reports/dse_ch196_ch200_production_checkpoint_20260701.md`, `07_Reports/dse_ch201_ch205_production_checkpoint_20260701.md`, `07_Reports/dse_ch206_ch210_production_checkpoint_20260701.md`, final scoped Sentinel reports, MoonRead `publish:verify`, and pushed git commits through current HEAD.

---

---

## Milestone 8: V6.36 Lean Pipeline A/B Experiment

**Goal**: Determine whether a simpler chapter-aware pipeline reduces provider calls and cost while preserving semantic fidelity, glossary consistency, and reader formatting quality.
**Dependencies**: Milestone 7; provider health check; locked sample and experiment vault

| # | Task | Effort | Risk | Verification |
|:--|:-----|:------:|:----:|:-------------|
| 8.1 | Lock a small cross-novel sample from verified raw source and record source hashes, arm assignment, and seed | S | ⚠️ | Manifest proves both arms use identical raw inputs and no production output is selected as source |
| 8.2 | Run the current production-shaped pipeline as the baseline in an isolated experiment vault | L | ⚠️ | Baseline artifacts, ledger, guardrails, Sentinel, and full provider trace exist; no treatment changes occur before baseline closes |
| 8.3 | Run the lean harness with longest-first glossary projection, block-safe literal translation, chapter-level refinement, chapter-level QA, formatting, and proposed glossary harvest | L | ⚠️ | Lean report and per-call trace files exist for every stage; failures stop and remain recorded |
| 8.4 | Compare calls, measured usage/cost, wall/provider time, QA hard-fails, Sentinel findings, omissions, glossary consistency, and formatting defects | M | ⚠️ | A comparison report has numeric values or explicitly says `not measured` for each metric |
| 8.5 | Review transcript artifacts: prompt template hash, system prompt, user prompt, input/output hashes and full local content, response usage, and failure details | S | ✅ | Every provider call is inspectable without exposing credentials; trace directory is experiment-local |
| 8.6 | Complete the bounded novel-specific pilot and compare quality, usage, timing, provider recovery, guardrails, Sentinel, and spot-check evidence | L | ⚠️ | Pilot report has numeric metrics or explicitly says `not measured`; no production output is published |
| 8.7 | Decide whether the lean pipeline is suitable for this novel and whether any shared-layer change merits separate cross-novel research | M | ⚠️ | Decision separates novel-specific refine findings from shared-layer adoption claims |

**Experiment design**:

- Hypothesis H1: assembling one chapter before refinement reduces refinement calls and improves continuity without increasing omission or semantic-drift findings.
- Hypothesis H2: projecting chapter-relevant approved terms into the source copy preserves term consistency with fewer prompt characters than attaching a glossary list to the literal call.
- Hypothesis H3: deterministic structure preservation plus AI formatting only at the chapter boundary reduces formatting defects without reducing dialogue/thought/sound-effect fidelity.
- Hypothesis H4: post-chapter glossary harvest has useful precision when candidates are required to exist in both source and final Thai output, but candidates must remain `proposed` until reviewed.
- Pass rule: treatment must show measured improvement in at least one cost/speed metric, no regression in blocking quality metrics, and no unacceptable regression in sampled human/Inspector review. A provider failure or missing metric is not a pass.

**Transcript policy**:

- Set `NOVEL_PIPELINE_TRACE_DIR` only for an isolated experiment. The trace records full system/user prompt and full provider response locally, plus hashes, model, timing, failure kind, and provider-reported usage when available.
- API keys, bearer tokens, environment values, and provider command secrets are redacted before writing.
- Transcript files stay outside production output and MoonRead. The research log stores paths and aggregate metrics; it does not duplicate the full copyrighted chapter text.
- If the provider does not return cost or token usage, the report must say `provider_did_not_report_cost` or `not measured`; do not infer cost from character counts.

**Milestone complete when**: the bounded novel-specific pilot is complete or safely stopped with evidence; every provider interaction is traceable; quality and cost metrics are compared; and a documented decision is made without publishing experiment output. OOS is not required for this milestone.

Status: complete as an experiment-only evaluation. HGD `ch001` completed the minimal pipeline smoke with 4 provider calls, 0 provider failures, and Sentinel `0/0/0/0`. One Hit Kill Swordmaster setup fetched/validated `ch001-ch095`, and the locked 10-chapter sample completed across `pilot_v6`, `pilot_v9`, and `pilot_v10`; final deterministic checks and Sentinel passed `0/0/0/0`. The valid QA fallback adjudication change is regression-tested. No experiment output was published to MoonRead, and no OOS run was required. Evidence: `07_Reports/v6_36_lean_pipeline_experiment_completion_20261003.md`, `07_Reports/v6_36_lean_pipeline_metrics_20261003.json`, and the isolated experiment vaults.

## Milestone 9: V6.37 OHKS Checkpoint And Review Follow-up

**Goal**: Test recovery/checkpoint behavior, targeted QA adjudication, evidence-reviewed glossary harvesting, and retry-inclusive measurement on five additional OHKS raw chapters.
**Dependencies**: Milestone 8 complete; verified OHKS raw chapters.

| # | Task | Effort | Risk | Verification |
|:--|:-----|:------:|:----:|:-------------|
| 9.1 | Run the checkpointed lean pipeline on five new OHKS raw chapters | L | ⚠️ | All five chapter outputs and per-stage checkpoints exist |
| 9.2 | Verify resume reuses completed stages without new provider calls | S | ✅ | Trace count is unchanged on a second `--resume` run |
| 9.3 | Run blocking and advisory Sentinel plus deterministic output scans | M | ⚠️ | Blocking counts are `0/0/0/0`; advisory findings are classified |
| 9.4 | Compare cost, calls, provider time, failures, and spot-check quality with the prior slice | S | ✅ | Numeric comparison report exists |
| 9.5 | Decide next profile/title work without publishing experiment output | S | ✅ | Report records the title/profile gap and next bounded action |

**Milestone complete when**: checkpoint reuse is independently verified, all five chapters have evidence-backed quality results, and the comparison distinguishes recoverability gains from cost/speed gains.

Status: complete after the v2 rerun. All five chapters passed blocking Sentinel `0/0/0/0`; advisory Sentinel found `33` minor English/title or game/UI findings. The first v2 attempt stopped safely on truncated `ch090` literal output, then resume reran only the broken chapter. A second complete resume added zero provider calls and reused all five stages for all five chapters. Metrics were `25` calls, `4` failures, `1,122.728s`, `182,904` tokens, and `$0.286459146`; cost/speed did not improve versus the prior slice. No experiment output was published. Evidence: `07_Reports/v6_37_ohks_five_chapter_checkpoint_review_v2_20261003.md`, `07_Reports/sentinel_quality_experiment_20261003_024140.md`, and the isolated experiment vault.

---

## Milestone 10: V6.38 Lean Runtime Replacement And Layer Separation

**Goal**: Make Lean the canonical bounded translation runtime for all registered novels and enforce a strict project-layer/novel-layer boundary without starting a provider-backed batch.
**Dependencies**: Milestones 8-9; architecture review

| # | Task | Effort | Risk | Verification |
|:--|:-----|:------:|:----:|:-------------|
| 10.1 | Move the canonical runtime and shared helpers to the workspace root | L | ⚠️ | Root package compiles, package metadata is present, and the DSE-local import shim resolves submodules to root |
| 10.2 | Set every registered novel config to Lean and route provider helpers/cwd to the selected vault or root shared scripts only | M | ⚠️ | Routing tests load all five configs and reject sibling/absolute helper escapes |
| 10.3 | Add staged output, selected-novel Sentinel, and atomic promotion for production Lean runs | L | ⚠️ | Provider-free tests prove pass promotes and Sentinel failure preserves an existing product file |
| 10.4 | Prevent Lean CLI commands from silently invoking legacy block stages or mutating novel identity | M | ✅ | CLI rejects unsupported legacy options/stages and `--novel` mismatch |
| 10.5 | Update architecture/brain/plan/recovery documentation to match verified ownership and runtime boundaries | S | ✅ | Control docs describe root project layer, isolated novel layer, staging gate, and migration limits |
| 10.6 | Run verification without paid provider calls and record the result | S | ✅ | compileall, routing tests, DSE regression suite, scoped guardrails/Sentinel, and novel dry-run pass |

**Milestone complete when**: Root runtime ownership, selected-novel routing, staged quality gate, CLI boundary, and documentation are all verified; no existing product output is changed by the migration.

Status: complete on 2026-10-03. No provider-backed translation or MoonRead publication was run. Evidence: `07_Reports/v6_38_lean_runtime_migration_20261003.md`, root regression suite, existing DSE suite through the compatibility shim, scoped quality checks, and the control-document updates. Shared prompt rendering, local formatting, checkpoint reuse, staged Sentinel isolation, path confinement and new-novel Lean selection have provider-free regression coverage.

## Execution Notes

- **Blocked items**:
  - Production publication from experiment output is blocked by design.
  - Long unattended production translation remains blocked; V6.34 and the IRS Pilot support bounded sequential execution only, not hands-off parallel scaling.
  - Any provider routing change remains blocked unless explicitly approved and measured.
  - V6.38 migration does not itself authorize a provider-backed batch or MoonRead publication; each future Lean run still needs its own bounded production gate.
  - HGD and One Hit Kill Lean pilot resumption uses the configured fallback chain; current empty `finish_reason=length` failures remain recorded, and the run stops only if all configured routes fail.
  - Recursive cache deletion is blocked by the host command policy; generated paths are ignored and documented instead.

- **Decision points**:
  - After Milestone 3: decide treatment hypotheses based on actual baseline evidence.
  - After Milestone 5: decide whether treatment improved enough to run OOS, needs revision, or should be rejected.
  - After Milestone 6: decide next production mode for DSE/HGD/IRS.
  - After Milestone 7: stop and wait for a new explicit production range.

- **Risk checkpoints**:
  - After sampling: verify raw source boundaries and no accidental hand-picking.
  - After baseline: verify no fixes were applied before analysis.
  - After treatment: verify metric movement, not just anecdotal quality.
  - After OOS: verify no overfitting to in-sample chapters.
  - After each pilot arm: verify trace completeness, redaction, and that production `05_Output`, glossary, ledger, and MoonRead remain unchanged.

- **Operating model**:
  - Codex plans, reviews, verifies, and writes the worker prompts.
  - Workers execute bounded tasks only.
  - Worker reports are claims until disk state, tests, reports, and diffs verify them.
  - Every experiment round gets one research log in `01_Research_Log/` and must be pushed.

- **Standard verification**:
  - `git diff --check`
  - `python -m compileall novel_pipeline`
  - `python -m unittest -v test_workspace_routing.py`
  - From `Deep Sea Embers/`: `python test_translation.py`
  - `python -m novel_pipeline.lean --help`
  - `novel-pipeline --config "<Novel>\.system\config.yaml" preflight`
  - scoped output guardrails for touched experiment outputs
  - scoped Sentinel for touched experiment outputs
  - MoonRead checks only if a separate production publication gate changes reader content

## Compatibility Notes Kept For Regression Tests

These notes preserve durable lessons that existing tests expect while the active roadmap stays focused on V6.34.

- V6.17 Incident Lessons: HGD Titles And Format
- HGD title fallback risk guarded by title sidecars.
- Completed Milestone: V6.17.1 HGD Title And Format Re-Audit.
- Completed Milestone: V6.18 Translation Speed Without Quality Loss.
- Historical AI-formatting routes are compatibility evidence only. Lean uses local Markdown normalization after chapter refinement and QA.
