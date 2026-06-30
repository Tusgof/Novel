# Implement Plan

Last updated: 2026-07-01

This is the active roadmap. It should answer: what is done, what is next, when to stop, and how to verify completion. Long history belongs in root-level `07_Reports/` or `01_Research_Log/`, not here.

## Finish Line

The product is complete when the user can:

- create or configure a new novel project
- research the novel and save a useful profile
- configure/fix source fetching through a playbook
- scan glossary candidates
- approve/reject glossary terms in the dashboard, including custom Thai terms
- translate bounded batches
- recover failed blocks
- generate reports
- publish verified output into MoonRead
- use the dashboard without Codex remembering every command

Quality bar: meaning preserved, terminology consistent, readable Thai, clean formatting, and auditable recovery.

## Current State

Completed:

- V3.7-V3.12: production rollout, reports, glossary hardening
- V4.0-V4.4: local operator product, multi-novel/genre/research foundations, preflight reliability
- V5.0-V5.4: product-complete review, doc cleanup, recovery/preflight hardening
- V6.0-V6.7: dashboard control surface and UX rebuild
- V6.8: OpenRouter provider replacement benchmark and routing update
- V6.9: MoonRead reader web
- V6.10: QA provider cost/quality benchmark
- V6.11: output quality stabilization and MoonRead publishing hygiene
- V6.12: current doc simplification pass applied locally in root docs
- V6.12.1: canonical doc recovery manifest added locally at `DOC_RECOVERY.md`
- V6.13: working-tree decision recorded; visible untracked glossary/report queue remains intentional
- V6.14: MoonRead publication check passed for current scope
- V6.15: dashboard usability follow-up closed for practical scope
- V6.16/V6.16.5/V6.17/V6.17.1: HGD title/format audit and repair gate closed for published scope
- V6.18: first narrow speed slice complete; formatting/openrouter concurrency=2 was benchmarked on ch051 and passed without enabling global concurrency by default
- V6.22: multi-novel / per-novel quality layer split introduced through `00_Config/novel_registry.json`, MoonRead registry import, and registry-driven output guardrails
- V6.31: root `ARCHITECTURE.md` created; architecture duplication was pruned from `PROJECT_BRAIN.md`, and `AGENTS.md` / `PROJECT_BRAIN.md` now reference the architecture source
- HGD pronoun consistency repair closed for published scope: Seth-dominant chapters now use `ผม` consistently, HGD has an Obsidian pronoun policy note, prompts/profile/QA include the rule, and output guardrails cover known high-risk chapters

Current production state:

- Deep Sea Embers `ch001-ch150` translated and repaired in `05_Output/`
- MoonRead contains Deep Sea Embers `ch001-ch160`
- MoonRead contains Horror Game Developer `ch001-ch250`; HGD local ids now match source chapter numbers after the source-number migration and the HGD fetch resolver now prefers `metadata.site_chapter` over manifest ordinal IDs.
- MoonRead app now lives at `D:\Fogust\Workspace\Novel\MoonRead`; `Deep Sea Embers\reader-web` is only a compatibility stub
- HGD `ch022` missing time-skip issue repaired and guarded
- HGD title fallback risk guarded by title sidecars for `ch001-ch080`
- HGD pronoun drift risk guarded by `Horror Game Developers/02_Database_Views/HGD Pronoun Policy.md`, HGD prompt/profile rules, and `scripts/check_output_quality_guardrails.py`
- HGD title/truncation repair closed for MoonRead `ch001-ch080`: titles normalized, `ch002`/`ch060`/`ch072` truncations repaired, and source-vs-output truncation guardrail added
- HGD continuation complete: `hgd-ch101-ch200` completed as translated output and MoonRead is regenerated through `ch200`
- V6.23 pipeline smoothness fixes were verified during `hgd-ch091-ch100-v1`: batch glossary approval, QA repair-safe reruns, and HGD title fail-fast normalization all worked in production.
- V6.24 control packet/pre-resume gate was applied to `hgd-ch101-ch110-v1`; two QA hard-fails were recovered with repair-safe `--no-auto-refine` flow (`ch103` missing sound effects, `ch109` missing poem lines/personified pronouns)
- V6.24 QA omission recovery automation was added and exercised during `hgd-ch111-ch120-v1`: after ordinary QA retries, omission hard-fails can restore literal-safe refined text once and rerun QA instead of forcing Codex to hand-edit JSON artifacts.
- V6.24 latest-refined-before-formatting fix was added during `hgd-ch121-ch130-v1`: after QA retry writes a newer refined artifact, formatting reloads that artifact instead of using stale in-memory refined text.
- `hgd-ch131-ch140-v1` completed with one bounded pronoun repair on `ch136`; QA passed after `--no-auto-refine`, output guardrails passed, and no current failed blocks remain.
- `hgd-ch141-ch150-v1` completed with bounded repairs for `ch142` glossary/pronoun drift, `ch143` Seth thought pronouns, `ch146` stale formatted artifact after local recovery, `ch148` quest-term confusion, `ch149` Seth dialogue pronouns, and `ch150` rank/unscary mistranslations. Status reports all 10 blocks complete, no current failed blocks, output guardrails passed, and checkpoint report exists at `Horror Game Developers/07_Reports/hgd_ch141_ch150_checkpoint.md`.
- `hgd-ch151-ch160-v1` completed with no current failed blocks and output guardrails passed. During this run, QA routing was corrected so normal HGD QA uses `openrouter_reasoning` + `deepseek/deepseek-v4-flash`; `deepseek/deepseek-v4-pro` was removed from the normal fallback path, and new QA ledger records include `metadata.model`.
- `hgd-ch161-ch170-v1` completed with no current failed blocks and output guardrails passed. QA used only V4 Flash reasoning or Qwen fallback; no V4 Pro QA route was used.
- `hgd-ch171-ch180-v1` completed with no current failed blocks and output guardrails passed. `ch176` needed bounded recovery for Seth pronoun drift plus missing Dreamwalker/Mirelle tail content; QA passed after repair. QA used only V4 Flash reasoning or Qwen fallback; no V4 Pro QA route was used.
- `hgd-ch181-ch190-v1` completed with no current failed blocks and output guardrails passed. Historical failed records came from Codex quota when QA fallback reached emergency fallback on `ch182`/`ch186`; bounded QA reruns recovered both. QA used only V4 Flash reasoning or Qwen fallback for completed QA records; no V4 Pro QA route was used.
- `hgd-ch191-ch200-v1` completed with no current failed blocks and output guardrails passed. `Shepherd Decree`/`Decree Shepherd` mojibake was repaired during the glossary gate, and title mappings were added through `ch200`. QA used only V4 Flash reasoning or Qwen fallback for completed QA records; no V4 Pro QA route was used.
- `dse-ch081-ch120-v1` completed with no current failed blocks and output guardrails passed. MoonRead registry now publishes Deep Sea Embers through `ch120`; `npm run generate:chapters`, `lint`, `build`, and `smoke` passed after publication.
- `dse-ch121-ch150-v1` completed with no current failed blocks and output guardrails passed. Duplicate title paragraphs under H1 headings were repaired before MoonRead publication.
- `hgd-ch201-ch220-v1` completed with no current failed blocks and output guardrails passed. Manual QA force-accept on repaired `ch206`/`ch211` exposed a status calculation bug; `ResumeState.next_pending_stage()` now treats `qa force_accepted` and `qa skipped` as QA-done states.
- HGD source-number migration completed: missing source chapters `29`, `30`, `54`, `55`, `91`, and `221` were inserted/translated; HGD `03_Raw`, `04_Work`, `05_Output`, and MoonRead generated content now use source-number ids through `ch236`. Evidence: `07_Reports/hgd_source_number_migration_20260622.md`.
- HGD English/glossary leakage repair completed after user report on `ch149`: `ทวิสเต็ดแมน` -> `ชายบิดเบี้ยว`, `อโนมาลี` / `(Anomaly)` -> `ความผิดปกติ`, `Squad Leader` -> `หัวหน้ากลุ่ม`, and related English parenthetical leakage variants were removed from HGD output and regenerated MoonRead content. Prevention is now in glossary notes, `scripts/check_output_quality_guardrails.py`, and regression tests.
- Full translated-output quality audit completed for current published scope: DSE `ch001-ch150`, HGD `ch001-ch220`, and MoonRead generated content pass deterministic guardrails. Hard artifact leaks found during the audit were repaired and promoted into guardrails/tests. Approved glossary entries are now treated as Thai-only product text by default: final output and MoonRead must not keep approved English originals/aliases as parentheticals or UI labels unless a future explicit glossary field allows bilingual display.
- V6.25 Sentinel Quality Gate initial slice completed: Sentinel report generation exists, current published scope was measured, 35 approved-glossary blockers were found and repaired, optimized runtime dropped from about 113 seconds to about 36 seconds, and latest result is blocker/major/minor/info `0/0/80/0`. The 80 minor English-token findings are a review queue, not publish blockers.
- MoonRead was regenerated, built, and smoked after DSE `ch150` / HGD `ch236` source-number migration publication.
- DSE `dse-ch151-ch160-v1` and HGD `hgd-ch237-ch250-v2` completed and published to MoonRead. Output guardrails passed for both touched ranges, Sentinel final reports passed with blocker/major/minor/info `0/0/0/0`, and MoonRead `generate:chapters`, `lint`, `build`, and `smoke` passed with 410 available chapters.
- Post-ch224 recurrence hardening added: HGD touched-scope cleanup repaired `ch091`, `ch222`, `ch235`, `ch236`, and `ch224` product-surface defects; MoonRead now has scoped `publish:verify` (`generate:chapters` -> scoped Sentinel -> lint -> build -> smoke); `run-sentinel-gate.mjs` refuses accidental full-workspace scans unless `SENTINEL_ALLOW_FULL=1`; generator validation rejects known fatal HGD product terms before reader import succeeds.
- no current failed blocks are known
- notable approved Deep Sea Embers terms include `实太阳神` -> `สุริยเทพที่แท้จริง` and `面具神` -> `เทพหน้ากาก`

## Planned Milestone: V6.32 IRS Parallel-Ready Translation Experiment

Goal: run a measured 20-chapter IRS translation experiment before committing to long parallel IRS batches. This gate is named **Libra - Pilot Gate**. It becomes the mandatory setup gate for every future novel: before a new novel is allowed to scale past pilot translation, it must randomly sample 20 chapters from fetched raw source, expose pipeline failure modes, classify each fix as multi-novel or novel-only, and prove that the improved workflow is faster and safer than the current manual recovery-heavy flow.

Execution status:

- 2026-06-29: In-sample treatment iteration failed gate before out-of-sample. Report: `Infinite Regressor Stories/07_Reports/v6_32_irs_experiment_iteration_20260629.md`.
- Completed evidence before stop: isolated experiment vault created, baseline/sample report generated, IRS source-risk normalization added, embedded CJK gloss normalization added, rejected glossary variant repair/check added, IRS block size reduced from 1500 to 900 words, and tests passed.
- Failed evidence: `irs-v6-32-insample-treatment-v2` completed 8/34 in-sample blocks and stopped at `ch019-block-002` QA after fallback chain reached Codex quota; Qwen fallback also hung once and required manual child-process cleanup.
- 2026-06-29: V6.32.1 QA fallback hardening applied. Report: `Infinite Regressor Stories/07_Reports/v6_32_1_qa_fallback_hardening_20260629.md`.
- Completed evidence in V6.32.1: Codex and qwen were removed from automatic QA fallback; provider timeout now kills process trees; source footnote marker preservation was added; `ch019-block-002` recovered from QA; compile and tests passed.
- Failed evidence after V6.32.1: `irs-v6-32-insample-treatment-v3` progressed to 12 completed blocks / 3 completed chapters, then stopped at `ch006-block-003` QA because both `deepseek/deepseek-v4-flash` reasoning and `deepseek/deepseek-v4-pro` reasoning returned empty assistant messages.
- 2026-06-29: Provider isolation showed reasoning-enabled OpenRouter Flash/Pro returned empty assistant messages on the full `ch006-block-003` QA prompt, while non-reasoning `deepseek/deepseek-v4-flash` and `google/gemini-3-flash-preview` returned usable PASS output.
- 2026-06-29: V6.32 IRS experiment completed for IRS. In-sample `irs-v6-32-insample-treatment-v3` completed 34/34 blocks; out-of-sample `irs-v6-32-oos-v1` completed 32/32 blocks; current failed blocks are none; scoped deterministic output audit passed for all 20 sampled chapters. Completion report: `Infinite Regressor Stories/07_Reports/v6_32_irs_experiment_completion_20260629.md`.
- Current decision: V6.32 passed as a mandatory setup experiment for IRS, but did not approve long unmonitored parallel production. Next IRS work should be a bounded sequential production pilot unless a dedicated parallelism milestone implements stronger concurrency controls.
- 2026-06-29: V6.32G DSE repeat completed. DSE raw pool was fetched through `ch160`; sample seed `632160`; in-sample `dse-libra-pilot-insample-v1` completed 54/54 blocks; out-of-sample `dse-libra-pilot-oos-v1` completed 56/56 blocks; current failed blocks are none; output guardrails and Sentinel passed for all 20 sampled chapters. Completion report: `Deep Sea Embers/07_Reports/libra_pilot_gate_dse_completion_20260629.md`.
- Current decision: DSE passed Libra - Pilot Gate, but the run confirmed translate/refine/QA throughput is still too slow under serial execution. Keep DSE production work bounded; treat broader parallelism as a dedicated milestone.
- 2026-06-29: V6.32G HGD repeat completed. HGD raw pool was verified through `ch250`; sample seed `632250`; in-sample `hgd-libra-pilot-insample-v1` completed 10/10 chapters; out-of-sample was split into two 5-chapter glossary batches (`hgd-libra-pilot-oos-a-v1`, `hgd-libra-pilot-oos-b-v1`) and completed 10/10 chapters; current failed blocks are none; output guardrails and aggregate Sentinel passed for all 20 sampled chapters. Completion report: `Horror Game Developers/07_Reports/libra_pilot_gate_hgd_completion_20260629.md`.
- Current decision: IRS, DSE, and HGD have all passed Libra - Pilot Gate. Production continuation may proceed only as bounded batches with glossary batch size 5, blocking Sentinel, and post-run guardrails. Long unmonitored parallel production remains unapproved.

Why this exists:

- IRS is the first English-source novel with unusual paragraph pacing, footnotes, Constellation/system messages, Korean names, and distorted/Zalgo sound effects.
- The current IRS pilot exposed slow recovery paths: title sidecar requirements, glossary/title setup, provider timeouts, CJK/name leakage, English parenthetical leakage, runaway sound effects, local-recovery truncation, and manual artifact repair.
- We should not scale to long parallel runs until the pipeline can survive representative IRS chapters without Codex repeatedly hand-editing artifacts.

Experiment principle:

- Treat this as a controlled pipeline experiment, not production publication.
- Treat this as a required new-novel setup stage, not an optional optimization. The purpose is to tune the pipeline for the novel before long production batches begin.
- Use isolated run IDs and reports so failed attempts do not pollute the intended production continuation.
- Do not publish experiment output to MoonRead unless a later production gate explicitly approves it.
- Preserve IRS source pacing by default; formatting changes must be minimal and must not collapse paragraphs.

### V6.32A: Baseline And Hypotheses

Baseline:

- Use existing IRS pilot evidence from `ch001-ch015` and the interrupted `irs-ch016-ch020-v1` work as the current baseline.
- Record current baseline metrics before changing runtime behavior:
  - wall-clock time per chapter and per block
  - provider calls per stage
  - retry count by stage
  - QA hard-fail count
  - provider timeout / empty-output / mojibake count
  - manual artifact repair count
  - Sentinel blocker/major/minor count
  - output guardrail failures
  - MoonRead publish-readiness status, if generated

Hypotheses to test:

1. **Pre-normalizing source risk tokens improves reliability.**
   - If Zalgo/distorted sound effects are normalized before provider calls, translation/refinement should stop producing runaway repeated characters and truncation.
   - Expected measurable result: zero runaway-repeat failures and no local-recovery truncation in the 20-chapter test.

2. **Risk-aware block splitting improves completion rate.**
   - If long/high-risk blocks are split before translation or recovery, provider omission and empty-output rates should fall.
   - Expected measurable result: lower QA omission hard-fails versus baseline, and no block requiring manual full-artifact rewrite.

3. **Scoped Libra context improves glossary consistency without bloating prompts.**
   - If each block receives only relevant glossary terms plus high-priority constants, approved-term coverage should improve without increasing provider failures.
   - Expected measurable result: no blocker-level missing glossary coverage on character/entity/title/system terms.

4. **Parallelism must start at the safest stages.**
   - Formatting-only parallelism is already benchmarked; translation/refinement/QA parallelism should be tested only after source normalization and scoped glossary are stable.
   - Expected measurable result: any enabled parallel slice improves wall-clock time by at least 25% while keeping blocker/major findings at zero.

5. **Deterministic pre-QA checks reduce wasted provider calls.**
   - If obvious failures are caught before provider QA, rerun loops should be shorter and cheaper.
   - Expected measurable result: fewer provider QA calls per completed block without reducing final quality.

### V6.32B: Sample Design

Total experiment size: 20 IRS chapters.

Sampling rule:

- Libra - Pilot Gate requires the intended source scope to be fetched into `03_Raw/` before sampling. If the site cannot provide every chapter, record the verified fetchable scope first, then sample only from that complete fetchable scope.
- Libra - Pilot Gate samples from fetched `03_Raw/` source chapters, not from only chapters that were already translated, already touched, or already known to be problematic.
- The sample must be selected with a recorded fixed seed and must be reproducible from the raw-source chapter list.
- Previously translated/problem chapters may appear only if the random raw-source sample selects them, or if they are explicitly added as a separate diagnostic add-on outside the 20-chapter gate.
- This prevents the setup experiment from overfitting to old incidents and makes it reveal real source-distribution problems for the novel.

In-sample set: 10 chapters used to tune and validate the fixes.

- Choose 10 chapters from the recorded raw-source sample. Prefer stratified random sampling when metadata/risk tags are available, so the set includes representative risk types such as:
  - distorted/Zalgo monster sounds
  - footnotes
  - Constellation/system bracket messages
  - dense glossary use
  - title sidecar requirements
  - prior QA recovery incidents, if randomly selected
- Candidate pool: fetched `03_Raw/` chapters only. For IRS that means the currently fetched source scope, not only the early pilot chapters.
- These chapters must run under experiment run IDs; do not overwrite production-approved output without an explicit repair gate.

Out-of-sample set: 10 held-back chapters used only after the in-sample fixes pass.

- Choose the 10 held-back chapters from the same recorded raw-source sample process, excluding the in-sample chapters.
- Selection seed, raw-source pool, exclusions, and final chapter IDs must be saved in the experiment report.
- Do not tune rules after looking at out-of-sample failures unless the run is explicitly marked as a failed iteration and a new out-of-sample set is selected.

Sample stratification:

- At least 2 chapters with action/sound-effect-heavy content.
- At least 2 chapters with system/Constellation/UI-style messages.
- At least 2 chapters with heavy named-character or organization glossary usage.
- At least 1 chapter with footnotes or translator-note risk.
- At least 1 normal low-risk chapter to measure overhead.

### V6.32C: Experiment Protocol

Step 1: Freeze the baseline.

- Save current IRS state report:
  - fetched source scope
  - existing translated scope
  - current failed blocks
  - current provider routing
  - known IRS glossary/title sidecars
  - known unresolved artifacts such as `ch019-block-002`, if still present
- Generate a baseline report under `Infinite Regressor Stories/07_Reports/`.

Step 2: Build preflight analyzers before running providers.

- Add read-only analyzers first:
  - source risk scanner: long block, Zalgo/distorted text, footnotes, bracket messages, repeated characters, likely title sidecar need
  - block split recommender: report-only until approved
  - glossary context preview: terms Libra would pass to each block
  - parallel safety planner: which stages can safely run in parallel for the selected sample
- Done when analyzers can run without provider calls and produce a per-chapter risk table.

Step 3: Run in-sample baseline or baseline-equivalent pass.

- Use bounded experiment run IDs, for example `irs-v6-32-insample-baseline-v1`.
- Stop on manual QA prompt, provider failure, command length failure, validation failure, unexpected scope expansion, or artifact truncation.
- Record every stop reason as a data point, not just as an operational blocker.

Step 4: Implement the smallest fixes that address measured failures.

Classify every fix by layer:

- **Layer 0 multi-novel:** safe for all novels, such as repeated-character runaway detection, provider empty-output detection, stage timing metrics, scoped report generation, and no-token-leak logging.
- **Layer 1 language:** English-to-Thai rules, such as parenthetical English leakage, bracketed system-message translation, and English sound-effect normalization.
- **Layer 2 IRS novel:** IRS pacing preservation, IRS title style, Constellation term policy, and story-specific Korean/name rules.
- **Layer 3 run/batch:** one-off recovery decisions for a specific block.

Rule: implement at the lowest layer that catches the failure safely. Promote upward only after the same failure class appears outside IRS or outside English-source novels.

Step 5: Rerun in-sample after fixes.

- Use a new run ID, for example `irs-v6-32-insample-treatment-v1`.
- Compare against baseline metrics.
- Do not proceed to out-of-sample unless in-sample has:
  - zero current failed blocks
  - zero Sentinel blocker/major findings
  - zero runaway/truncation findings
  - no manual artifact rewrite required
  - at least 25% wall-clock improvement if parallelism was enabled

Step 6: Run out-of-sample.

- Use the held-back out-of-sample chapters selected from the recorded fetched `03_Raw/` source pool.
- Use a new run ID, for example `irs-v6-32-outsample-v1`.
- No rule tuning during the run except emergency stop/recovery.
- If out-of-sample fails, write a failure analysis before changing rules.

Step 7: Decide production readiness.

- Production IRS continuation can resume only if out-of-sample meets the acceptance gates below.
- If not, loop back with a new hypothesis and rerun a smaller experiment; do not scale to long parallel batches.

### V6.32D: Metrics And Acceptance Gates

Primary metrics:

- completion rate: target 20/20 chapters complete in experiment scope
- current failed blocks: target 0
- manual artifact rewrites: target 0; deterministic artifact regeneration is allowed only if scripted and verified
- Sentinel blocker/major: target 0/0
- output guardrail blockers: target 0
- glossary coverage blockers: target 0
- runaway repeated-character findings: target 0
- source-vs-output truncation findings: target 0
- provider timeout/empty-output rate: must be lower than baseline or have automatic safe retry/fallback
- wall-clock speed: at least 25% faster than sequential baseline if any parallelism is enabled

Secondary metrics:

- average provider calls per block
- QA retry count per block
- formatting validation fallback rate
- prompt glossary term count per block
- average block size and split count
- report generation time
- false-positive count in deterministic checks

Acceptance gates:

- In-sample treatment passes all primary quality metrics before out-of-sample starts.
- Out-of-sample passes all primary quality metrics before any production parallel batch is approved.
- Any speed improvement is rejected if it increases blocker/major findings, truncation, glossary misses, or manual repair count.
- If the result is faster but less reliable, the milestone fails and the change stays disabled.
- If the result is reliable but not faster, keep the quality improvements and defer parallelism.

### V6.32E: Feedback Loop

For each failed block or rejected output:

1. Identify the earliest broken stage: source/fetch, split, glossary, translate, refine, QA, format, Sentinel, or MoonRead.
2. Record the failure class:
   - provider timeout
   - empty output
   - command length
   - mojibake
   - runaway repeated characters
   - omission/truncation
   - glossary miss
   - title sidecar miss
   - English leakage
   - formatting/pacing drift
   - false positive guardrail
3. Decide the layer for the fix: multi-novel, language, IRS novel, or run-local.
4. Add the smallest deterministic check or scripted recovery that prevents recurrence.
5. Add or update a test/fixture when the failure class can recur.
6. Rerun only the affected sample, then rerun the full in-sample gate.
7. Promote to out-of-sample only after the in-sample gate is clean.

Feedback loop stops only when:

- out-of-sample passes acceptance gates, or
- the same provider/infrastructure blocker repeats three times and requires user decision, or
- measured quality degrades versus the current safe sequential workflow.

### V6.32F: Parallel Batch Readiness Decision

Parallelism levels:

1. **Level P0: no runtime parallelism.**
   - Only analyzers and report generation may run independently.
   - Use this if provider instability dominates.

2. **Level P1: formatting-only parallelism.**
   - Already benchmarked as the safest speed slice.
   - Can be reused if AI formatting validation remains strict.

3. **Level P2: chapter-level pipeline parallelism with stage locks.**
   - Different chapters may run in parallel only if provider rate limits, ledger writes, artifact paths, and report generation are isolated.
   - Must preserve append-only ledger safety and chapter output assembly order.

4. **Level P3: block-level translation/refinement/QA parallelism.**
   - Highest risk. Only consider after P2 works.
   - Requires provider concurrency limits, per-block locks, deterministic merge order, and clear resume semantics.

Initial recommendation:

- Start V6.32 with P0/P1 only.
- Use experiment evidence to decide whether P2 is worth implementing.
- Do not attempt P3 until IRS out-of-sample passes cleanly with P2 or until a dedicated concurrency design milestone is approved.

Done when:

- `IMPLEMENT_PLAN.md` contains this experiment protocol.
- `ARCHITECTURE.md` records the 20-chapter randomized experiment as a mandatory new-novel setup gate before scaled production translation.
- An experiment report exists with baseline, in-sample, out-of-sample, metrics, failures, fixes, and production recommendation. IRS evidence: `Infinite Regressor Stories/07_Reports/v6_32_irs_experiment_completion_20260629.md`.
- Any implemented fixes are classified by layer and verified by tests or deterministic checks.
- The final recommendation says one of:
  - safe to run IRS production sequentially only
  - safe to run IRS with formatting-only parallelism
  - safe to implement/test chapter-level parallelism next
  - not safe to continue until a specific blocker is fixed

Current IRS recommendation: safe to run IRS production sequentially only. Long unmonitored parallel production is not approved because retries/recoveries, timeout cleanup, reasoning-QA empty output, and a repeated-character truncation incident still require stronger shared guardrails.

Stop conditions:

- experiment output would overwrite production-approved chapters without explicit approval
- provider output contains token/API key or meta text
- current failed block is unresolved
- manual QA prompt appears
- source range expands beyond the selected 10 chapters
- MoonRead publication is attempted before production approval

### V6.32G: Repeat Experiment For Existing Novels

After IRS passes V6.32 in-sample and out-of-sample gates, repeat the same 20-chapter randomized experiment on the existing production novels to prove the pipeline improvements generalize.

Order:

1. Deep Sea Embers - complete, report `Deep Sea Embers/07_Reports/libra_pilot_gate_dse_completion_20260629.md`
2. Horror Game Developer - complete, report `Horror Game Developers/07_Reports/libra_pilot_gate_hgd_completion_20260629.md`

Rules:

- Use each novel's own vault/profile/glossary/source quirks.
- Use 10 in-sample chapters and 10 out-of-sample chapters.
- Sample from each novel's fetched `03_Raw/` source pool with a recorded seed. Already translated chapters may appear only if selected by the raw-source sample, or as a clearly separate diagnostic add-on outside the 20-chapter gate.
- Do not publish experiment output to MoonRead unless a separate publication gate approves it.
- Classify every finding by layer: multi-novel, language, novel, or run-local.

Done when:

- IRS, DSE, and HGD each have a V6.32 experiment report.
- All three reports show zero current failed blocks, zero Sentinel blocker/major findings, and no manual artifact rewrite requirement.
- Any recurring cross-novel failure has a shared guardrail or documented rule in the correct layer.

Current status:

- IRS: complete.
- DSE: complete.
- HGD: complete.

## Active Milestone: V6.33 Post-Pilot Production Continuation

Goal: continue production translation after all three active novels have passed Libra - Pilot Gate, without mixing experiment artifacts into production output.

Current status as of 2026-07-01:

- HGD `ch251-ch270` translation output is complete and published to MoonRead. Sentinel final report `07_Reports/sentinel_quality_hgd-v6-33-ch251-ch270-final_20260629_200006.md` reports blocker/major/minor/info `0/0/0/0`; publish Sentinel report `07_Reports/sentinel_quality_moonread-hgd-ch251-ch270-publish_20260630_172638.md` reports `0/0/0/0`.
- DSE `ch161-ch180` translation output is complete and published to MoonRead. Sentinel final report `07_Reports/sentinel_quality_dse-v6-33-ch161-ch180-final_20260630_005304.md` reports blocker/major/minor/info `0/0/0/0`; publish Sentinel report `07_Reports/sentinel_quality_moonread-dse-ch161-ch180-publish_20260630_172640.md` reports `0/0/0/0`.
- IRS clean `ch001-ch050` translation output is complete and published to MoonRead. All 10 clean 5-chapter batch statuses report current failed blocks: none and manual actions needed: none. Blocking Sentinel report `07_Reports/sentinel_quality_irs-clean-ch001-ch050-final-after-leakage-rule_20260630_101639.md` reports `0/0/0/0`. Advisory report `07_Reports/sentinel_quality_irs-clean-ch001-ch050-final-advisory-review-after-leakage-rule_20260630_101829.md` reports `0/0/80/0` minor suspicious-English review items. Publish Sentinel report `07_Reports/sentinel_quality_moonread-irs-ch001-ch050-publish_20260630_172648.md` reports `0/0/0/0`. Completion report: `Infinite Regressor Stories/07_Reports/irs_clean_retranslate_ch001_ch050_completion_20260630.md`.
- A new Sentinel regression prevents glossary/category note tails from leaking into final output after IRS ch020 exposed that failure mode.
- MoonRead `generate:chapters` produced 3 books / 500 available chapters / 0 missing / 0 rejected; `lint`, `build`, and `smoke` passed after publication.

Requested scope:

1. Horror Game Developer: translate 20 additional source-number chapters after the current published scope.
2. Deep Sea Embers: translate 20 additional chapters after the current published scope.
3. Infinite Regressor Stories: discard old translation attempts for production purposes and start a clean retranslation from `ch001-ch050`.

Hard rules:

- Use glossary batches of 5 chapters for all three novels.
- Do not reuse experiment run IDs for production.
- Do not publish a range until output guardrails, aggregate Sentinel, and MoonRead publish verification pass for that touched range.
- Keep production sequential/bounded unless a later parallelism milestone explicitly approves broader concurrency.

V6.33A: Production Planning

- Confirm available raw source scope for each novel before choosing exact ranges.
- For HGD, do not assume chapters beyond `ch250` are fetched or available; fetch/verify the next source scope first.
- For DSE, fetch/verify the next 20-chapter raw scope before glossary scan.
- For IRS, define a clean production run family for `ch001-ch050`; isolate or archive old pilot outputs so production status is not confused.

Done when:

- exact chapter ranges and run IDs are written in a short production command packet
- source sequence/fetch checks pass for those ranges
- no run starts before glossary batch 1 is defined

V6.33B: Batch Execution Pattern

For each novel:

1. Run scan-only for 5 chapters.
2. Review/approve glossary decisions.
3. Translate/refine/QA/format/Sentinel for those 5 chapters.
4. Run output guardrails and aggregate Sentinel for the touched range.
5. Repeat until the requested scope completes.

Done when:

- HGD requested continuation scope completes or the available source scope is exhausted and documented: done for `ch251-ch270`
- DSE requested continuation scope completes or the available source scope is exhausted and documented: done for `ch161-ch180`
- IRS `ch001-ch050` clean production retranslation completes: done
- MoonRead publication is updated only after each novel's verification passes: done for DSE through `ch180`, HGD through `ch270`, and IRS through `ch050`

V6.33 Stop Conditions:

- source range is missing or source numbering diverges
- glossary approval is incomplete
- current failed block exists
- manual QA prompt appears
- provider timeout/empty output repeats for the same stage
- Sentinel blocker/major appears
- MoonRead publish verification fails

## Active Milestone: V6.34 Cross-Novel Libra - Blind Pilot Gate

Goal: run a new Libra - Pilot experiment across Deep Sea Embers, Horror Game Developer, and Infinite Regressor Stories using raw-source sampling that is not limited to previously translated or previously problematic chapters. The purpose is to improve the whole translation pipeline: skills, code, prompts, glossary workflow, provider routing, guardrails, reports, and operator policy.

Why this exists:

- Earlier Libra - Pilot evidence is useful, but it still overrepresents ranges that were already translated or already operationally familiar.
- Production bugs kept recurring after local fixes because some rules were not promoted to the correct multi-novel/language/novel layer.
- Glossary quality cannot be proven from early translated ranges only; it needs pressure from late, unseen, and story-distribution-wide source chapters.

Current source-pool audit as of 2026-07-01:

| Novel | Fetched raw source pool | Continuity | Published/translated scope |
| --- | --- | --- | --- |
| Deep Sea Embers | `03_Raw/ch001-ch180` (`180` chapters) | no gaps detected | MoonRead through `ch180` |
| Horror Game Developer | `03_Raw/ch001-ch270` (`270` chapters) | no gaps detected | MoonRead through `ch270` |
| Infinite Regressor Stories | `03_Raw/ch001-ch394` (`394` chapters) | no gaps detected | MoonRead through `ch050` |

Important limitation: DSE source has more chapters upstream than the current local raw pool. V6.34 may sample only from the verified local `03_Raw` pool unless Ferryman first fetches and validates a broader DSE source scope. If broader fetch fails, record the verified fetchable scope and sample only from that scope.

### V6.34A: Research Log And Sampling Manifest

Status: complete for the first source-pool/sampling round. Evidence: `01_Research_Log/2026-06-30_novel_pipeline_libra_blind_pilot_source_pool.md`.

Rules:

- Every V6.34 experiment round must create or update a log using `RESEARCH_LOG_FORMAT.md`.
- Store logs in `01_Research_Log/`.
- One experiment round equals one research log. Do not merge multiple experiment rounds into one reconstructed summary.
- Raw data paths, sample seed, source pool, selected chapters, metrics, fixes, and decisions must be recorded.

Sampling design:

- Use only chapters that exist in each novel's `03_Raw/` source pool.
- Use seed `634001` for the first cross-novel blind pilot.
- Use 10 strata per novel across the verified raw-source range.
- From each stratum, pick 1 in-sample chapter and 1 out-of-sample chapter.
- Total first-round sample: 60 chapters: 20 per novel, 10 in-sample and 10 out-of-sample per novel.
- Previously translated chapters are allowed only if selected by the raw-source sample. They must not be hand-picked.

First-round selected sample:

| Novel | In-sample chapters | Out-of-sample chapters |
| --- | --- | --- |
| DSE | `ch008,ch033,ch051,ch061,ch077,ch098,ch110,ch143,ch150,ch176` | `ch016,ch027,ch044,ch072,ch089,ch099,ch125,ch132,ch154,ch180` |
| HGD | `ch005,ch046,ch059,ch083,ch131,ch155,ch187,ch205,ch239,ch262` | `ch027,ch041,ch067,ch097,ch124,ch160,ch186,ch204,ch242,ch252` |
| IRS | `ch009,ch076,ch086,ch157,ch183,ch201,ch252,ch300,ch338,ch381` | `ch030,ch073,ch093,ch133,ch165,ch236,ch244,ch278,ch348,ch361` |

Done when:

- source-pool audit is recorded
- sample seed and selected chapters are recorded
- research log exists for the source-pool/sampling round
- no provider calls or production translation are started during the sampling-only round

### V6.34B: Baseline Read-Only Analysis

For the 60 selected chapters, run read-only analyzers before any provider call:

- source length and block-risk estimate
- title-sidecar risk
- glossary candidate density
- approved glossary coverage prediction
- bracket/system-message density
- sound-effect/repeated-character risk
- footnote/author-note risk
- raw-source language leakage risk

Done when:

- a per-chapter risk table exists
- each finding is classified by layer: multi-novel, language, novel, or run-local
- the research log is updated with measured baseline data

### V6.34C: In-Sample Treatment

Run only the 30 in-sample chapters first, bounded by novel and glossary batch:

1. DSE in-sample as isolated experiment runs.
2. HGD in-sample as isolated experiment runs.
3. IRS in-sample as isolated experiment runs.

Rules:

- Use glossary batches of 5 chapters.
- Do not publish experiment output to MoonRead.
- Stop on provider failure, manual QA prompt, command length failure, Sentinel blocker/major, output guardrail failure, source mismatch, or unexpected scope expansion.
- Any fix must be classified by layer before rerun.

Done when:

- all in-sample runs have zero current failed blocks
- output guardrails pass for the touched experiment outputs
- Sentinel blocker/major is `0/0`
- no manual artifact rewrite is required
- every fix has a test, guardrail, prompt rule, skill rule, or documented novel-layer policy

### V6.34D: Out-Of-Sample Proof

Run the 30 held-back out-of-sample chapters only after V6.34C passes.

Rules:

- No tuning after seeing out-of-sample failures unless the run is marked failed and a new OOS sample is selected.
- OOS is the proof that fixes generalize beyond the tuned sample.
- If OOS fails, write a failure log before implementing fixes.

Done when:

- OOS has zero current failed blocks
- Sentinel blocker/major is `0/0`
- output guardrails pass
- glossary coverage blockers are zero
- the research log includes metrics comparing baseline, in-sample, and OOS

### V6.34E: Pipeline Improvement Decision

After OOS:

- Promote recurring safe fixes to Layer 0 shared guardrails or registry policy.
- Put language-specific rules into language playbooks.
- Put story-specific terminology/voice rules into the relevant novel vault/profile.
- Update skills only when the workflow should be reusable across future novels.
- Update code only when deterministic validation or automation can prevent recurrence.
- Update prompts only when the provider instruction itself caused or failed to prevent the issue.

Acceptance:

- V6.34 report/log explains what improved, what did not, and what must remain bounded.
- Any production-routing change is backed by measured improvement and does not reduce quality.
- Long unmonitored parallel translation remains disabled unless the experiment proves it is safe.

## Active Milestone: V6.25 Sentinel Quality Gate

Goal: add a measurable post-output quality gate before MoonRead publication so repeated translation defects are caught by deterministic checks instead of by user spot checks after publishing.

Why this milestone exists:

- Recent HGD issues (`ทวิสเต็ดแมน`, `อโนมาลี`, English parentheticals, broken Markdown, dense formatting, and title fallback) were real product defects even when provider stages had passed.
- Existing guardrails are useful but scattered and mostly pass/fail. The operator needs one report that says whether a range is safe to publish and why.
- The first implementation should avoid adding another always-on AI worker. Deterministic checks are faster, cheaper, repeatable, and easier to regression-test. AI audit can be added later only for high-risk chapters.

### V6.25A: Sentinel Actor And Report

Add `008 Sentinel` as the post-output quality gate.

Responsibilities:

- inspect final Markdown and MoonRead generated content after translation/repair
- classify findings as `blocker`, `major`, `minor`, or `info`
- write both JSON and Markdown reports under `07_Reports/`
- recommend publish/no-publish based on blocker count

Done when:

- a Sentinel report command exists
- the report includes scope, counts, findings, and next action
- current DSE/HGD published scopes can be checked without provider calls

### V6.25B: Deterministic Quality Signals

Initial signals:

- reuse existing output guardrail results
- generic approved glossary enforcement across registered novels
- glossary note health check for unusable `thai_term` values
- suspicious English token/parenthetical scan as advisory signal
- MoonRead generated content scan for the same product-surface issues

Done when:

- approved glossary English leakage is a blocker
- mojibake/placeholder approved glossary Thai terms are blockers
- advisory English leakage is reported without blocking by default
- known bad fixtures prove the Sentinel catches recurring issues

### V6.25C: Measurement And Feedback Loop

Metrics:

- blocker count for current publish scope
- major/minor count by issue type
- known-regression fixture detection rate
- false-positive review notes for advisory English leakage
- recurrence count for issues already promoted into guardrails

Feedback loop:

1. Run Sentinel after each multi-chapter batch or broad repair.
2. If blocker > 0, stop publish and repair the full affected pattern.
3. If major > 0, inspect sampled chapters before publish.
4. If a user-reported issue recurs, add a fixture and promote the rule.
5. Re-run Sentinel and MoonRead validation before deploy.
6. For MoonRead publication, prefer scoped `npm run publish:verify` with `SENTINEL_NOVEL` and `SENTINEL_CHAPTERS` set to the touched range. Do not run unscoped full-workspace Sentinel as the default until the historical backlog is intentionally cleaned.

Done when:

- current published scope has blocker = 0
- report records the validation commands used
- regression tests include Sentinel fixture coverage

### V6.25D: Libra - Glossary Bot Coverage

Goal: make glossary consistency permanent by checking source glossary usage against final translated output, not only by searching for known wrong variants after the fact.

Libra role:

- `Libra` remains the glossary librarian before translation.
- `Libra - Glossary Bot` is the deterministic coverage sub-check inside Sentinel after translation.
- It is not a new always-on AI provider. Use algorithms first; optional AI review can be added later only for high-risk unresolved findings.

Sentinel layer model:

- Level 0, multi-novel: generic product-surface checks that should apply to every novel. Examples: provider/meta leakage, bad encoding, unintended source-language body text, quote-only lines, missing MoonRead generated files, truncation, approved-glossary English leakage, and source-vs-output approved glossary coverage.
- Level 1, per-novel: rules that depend on a specific novel's voice, glossary, title policy, source quirks, or known false positives. Examples: HGD Seth pronouns, HGD Kaelen/Kyle near-miss names, HGD English-title normalization, and DSE Chinese title sidecar requirements.
- Add a new rule at the lowest layer that safely catches the defect. Promote Level 1 rules to Level 0 only after the defect class is proven to recur across novels and the false-positive risk is low.
- Every new rule must document: layer, severity, trigger evidence, repair action, false-positive risk, and whether it blocks publish or only creates a review queue item.

Coverage rule:

- Load approved glossary terms and aliases for the novel.
- For each chapter/block source, find approved originals/aliases that appear in the source.
- In the final output and MoonRead output for that chapter, verify that the approved `thai_term` appears.
- If source contains an approved glossary term but output has no approved Thai term, report `glossary_coverage_missing`.
- Category severity:
  - `blocker`: character, entity, title, system, skill, rank
  - `major`: organization, location, item, technique, event
  - `minor`: generic/common terms or terms explicitly marked context-sensitive
- Do not require equal occurrence counts. Thai may legitimately use pronouns after first mention.
- If source count is high but Thai count is very low, report a major ratio warning instead of exact-count failure.

Near-miss rule:

- If expected Thai is missing and a known wrong variant appears, report it as blocker evidence.
- Start with deterministic prior incidents (`ไคลน์` for `Kaelen`, `ทวิสเต็ดแมน`, `อโนมาลี`) before adding fuzzy matching.
- Add fuzzy Thai-name matching only if deterministic variants are insufficient; keep false positives below 10% for blocker findings.

Glossary scan/context budget policy:

- Glossary scan should run per bounded batch, but candidate extraction should be chunked by source size instead of feeding a whole large range at once.
- Initial practical chunk limits:
  - Chinese source: about 3,000-5,000 Han characters per scan chunk
  - English source: about 4,000-7,000 words or roughly 20,000-35,000 characters per scan chunk
  - Prefer chapter/block boundaries; do not split inside dialogue/UI snippets when avoidable.
- The scan artifact should record chunk id, chapter ids, source size, candidate count, and removed noise count.
- If candidate count is unusually low for a large chunk, rerun scan or flag for human review.

Glossary context selection for providers:

- Do not pass the entire growing glossary to translate/refine/QA.
- Before each provider stage, Libra should build a scoped glossary subset:
  - terms found in the current source block
  - aliases/substrings that match the block
  - recently active chapter-level terms from the same batch
  - high-priority novel constants such as protagonist names, system names, core ranks, and recurring organizations
- Keep the provider glossary context bounded and relevant. If the subset is too large, prioritize character/entity/system/skill/rank first.
- The selected subset should be saved or reportable so later failures can prove whether the provider saw the needed term.

Done when:

- Sentinel reports source-vs-output glossary coverage findings.
- A fixture proves `source: Kaelen`, glossary `Kaelen -> เคเลน`, output `ไคลน์` is caught as a blocker.
- Current HGD `ch164-ch166` pass the coverage check after repair.
- Future batches have a documented rule: Libra selects relevant glossary context; providers should not receive the whole glossary blindly.

Stop conditions:

- Sentinel reports blocker findings in current product output
- report generation mutates source/artifacts unexpectedly
- advisory scanner creates noisy blocker-level false positives

### V6.25E: Runtime Blocking Stage

Goal: make Sentinel a real pipeline gate, not only a report that Codex remembers to run later.

Implementation:

- Add `execution.sentinel.mode` and `execution.sentinel.fail_on` to config parsing.
- Production DSE/HGD configs use `mode: blocking` and `fail_on: major`.
- After a chapter output is assembled, run Sentinel scoped to that chapter and novel.
- Append a `sentinel` ledger record with status `completed` or `failed`.
- Stop the run when scoped Sentinel reports blocker/major findings.
- Skip advisory English-token findings at runtime; keep them for manual feedback reports.
- Keep MoonRead postgenerate Sentinel manual/scoped for now. Do not run whole-workspace Sentinel automatically until historical backlog outside the touched range is intentionally cleaned.

Done when:

- `run`, `resume`, `rerun-block`, and batch final assembly all pass through the same Sentinel gate.
- Sentinel failures are visible in the ledger and include report paths.
- Unit tests still pass.
- A known clean scoped range passes Sentinel with blocker/major/minor/info `0/0/0/0`.

## Completed Milestone: V6.24 Pipeline Smoothness V2

Goal: make HGD `ch101-ch200` continuation less dependent on Codex manually editing artifacts while keeping the same translation quality bar.

Why this milestone exists:

- The pipeline is currently safe but not smooth. It correctly stops on QA hard-fails, missing title mappings, provider failures, and validation risks, but the recovery flow still pushes Codex into repeated file inspection and artifact edits.
- V6.23 improved the worst problems, but `hgd-ch081-ch100` still required manual intervention for glossary decisions, QA repair, title sidecars, and final verification.
- The target behavior is not "never stop." The target is: when the pipeline stops, it should produce a clear diagnosis, a bounded recovery command, and a reportable next safe action.

Current verified HGD continuation state:

- latest completed run id: `hgd-ch191-ch200-v1`
- completed stages: all production stages through chapter assembly for `ch101-ch200`
- reader status: MoonRead generated/linted/built/smoked with HGD `ch001-ch200` available
- next stage: no continuation task remains under this goal; future work should start as a new bounded milestone
- rule: reuse the V6.24 control packet and pre-resume gate pattern for each following increment before provider stages

### V6.24A: Standard Batch Control Packet

Create a compact control packet for each 10-chapter HGD increment before translation resumes.

Packet must include:

- run id and chapter range
- current ledger stage counts
- glossary candidate decisions and rejected noise terms
- expected title mappings/sidecars for the range
- provider route and known fallback policy
- stop conditions
- exact next safe command

Done when:

- `Horror Game Developers/07_Reports/hgd_ch101_ch110_control_packet.md` exists
- the packet proves `ch101-ch110` is still pre-translation
- no providers are called while creating the packet

### V6.24B: Recovery Command Patterns

Convert the common manual repair paths into documented operator commands and, where practical, CLI helpers.

Required patterns:

- QA omission after retry: inspect literal/refined/QA, preserve source beats, run QA with `--no-auto-refine`
- force-accept current repaired artifact: require explicit reason and write recovery metadata
- title mapping miss: stop before assembly, add title mapping/sidecar, rerun from assembly or chapter output gate
- formatting validation failure: rerun formatting first; only use local cleanup for deterministic Markdown issues, not dialogue/thought detection
- provider timeout/nonzero output: retry bounded stage once, then switch to configured fallback or stop with provider evidence

Done when:

- a report lists the exact command sequence for each pattern
- `inspect-block`, `qa --no-auto-refine`, `rerun-block`, and `force-accept-current` usage is unambiguous
- no guidance tells Codex to silently patch final Markdown

### V6.24C: Pre-Resume Gate For HGD ch101-ch110

Before continuing `hgd-ch101-ch110-v1`, run a pre-resume gate.

Gate checks:

- glossary scan artifact exists and has decisions
- glossary approval ledger records exist for `ch101-ch110`
- HGD title sidecar/mapping coverage is known for `ch101-ch110`
- status has no current failed blocks
- MoonRead remains published only through `ch100`
- provider preflight is ready or any provider warning is documented

Done when:

- gate report exists
- the next safe command is either a bounded resume or an explicit blocker
- translation has not started until the gate is green

### V6.24D: Dashboard/CLI Smoothness Backlog

These are implementation tasks after the current batch control packet is proven useful:

- dashboard should show the same control packet fields: current stage, blocker, recovery command, and next safe action
- dashboard buttons must call real bounded CLI actions or be visibly disabled with the reason
- add a "Recover failed block" surface that loads the QA/literal/refined artifacts side by side
- add a "Generate control packet" action for future batches
- add one command that summarizes latest-state status instead of making the operator reason from append-only failed records

Done when:

- the user can understand why the run stopped without reading raw JSON
- Codex can continue a stopped batch by following one packet and one recovery report instead of reconstructing state from memory

V6.24 stop conditions:

- any provider call is needed before the user approves resuming translation
- scope expands beyond HGD `ch101-ch110`
- a fix would weaken QA or skip final-output guardrails
- dashboard changes become broad UI redesign instead of targeted control-flow smoothness

### V6.24E: QA Omission Auto-Recovery

Problem:

- HGD `ch112`, `ch114`, and `ch117` showed the same failure pattern: refinement retries could omit poems, thoughts, sound effects, or required source beats. QA caught the issue, but Codex still had to inspect artifacts and manually restore missing content.

Implemented mechanism:

- `_run_qa_with_retries` now classifies QA feedback/findings for omission markers after normal retries are exhausted.
- If the failure is omission-like, the pipeline creates one `local_recovery` refined artifact from the literal translation, commits recovery metadata, and reruns QA once.
- If that final QA does not pass, the existing manual escalation path remains unchanged.

Acceptance evidence:

- `python -m compileall novel_pipeline` passed.
- `python test_translation.py` passed.
- `hgd-ch111-ch120-v1` completed 10/10 blocks with no current failed blocks.
- `python scripts\check_output_quality_guardrails.py --config "D:\Fogust\Workspace\Novel\Horror Game Developers\.system\config.yaml" --chapters ch111-ch120` passed.
- checkpoint report: `Horror Game Developers/07_Reports/hgd_ch111_ch120_checkpoint.md`.

### V6.24F: Latest Refined Artifact Before Formatting

Problem:

- `hgd-ch121-ch130-v1` exposed a state bug on `ch126`: QA retry wrote a newer refined artifact, but the downstream formatting step could still use an older in-memory refined draft. The ledger then showed a stale completed output plus a later formatting failure.

Implemented mechanism:

- `_process_block` now reloads the latest refined artifact from disk after QA and before formatting.
- This keeps formatted output aligned with the refined draft that actually passed the latest QA attempt.

Acceptance evidence:

- `ch126-block-001` was recovered with `rerun-block --from-stage formatting`.
- `hgd-ch121-ch130-v1` completed 10/10 blocks with no current failed blocks.
- `python scripts\check_output_quality_guardrails.py --config "D:\Fogust\Workspace\Novel\Horror Game Developers\.system\config.yaml" --chapters ch121-ch130` passed.
- checkpoint report: `Horror Game Developers/07_Reports/hgd_ch121_ch130_checkpoint.md`.

### Completed Milestone: V6.23 Pipeline Smoothness Before HGD ch091-ch100

Goal: make the next HGD increment controllable through bounded commands instead of repeated ad hoc manual edits.

Problem found during `hgd-ch081-ch090-v1`:

- batch glossary approval still pushed the operator toward repeated per-chapter action
- QA retries could re-refine after a manual artifact repair, overwriting the repaired content
- HGD source titles are English; without a title sidecar/mapping, final assembly could publish English headings silently
- recovery was technically possible, but the control flow was not smooth enough for routine production

Required fixes:

- add a batch `approve-terms --batch --run-id ...` path that commits reviewed `glossary_approved` records for all chapters in the batch scan artifact
- add QA repair-safe controls: run QA without auto re-refine, and force-accept the current repaired refined artifact only with an explicit reason
- add HGD title assembly protection: known English source titles auto-normalize to Thai sidecars, unknown English title mappings stop final assembly
- cover all three behaviors with deterministic tests

Done:

- `hgd-ch091-ch100-v1` completed and MoonRead availability is now 100 HGD chapters.
- `python -m compileall novel_pipeline` passed.
- `python test_translation.py` passed.
- output guardrails passed.
- MoonRead `generate:chapters`, `lint`, `build`, and `smoke` passed.
- Checkpoint: `Horror Game Developers/07_Reports/hgd_ch091_ch100_checkpoint.md`.

### V6.17 Incident Lessons: HGD Titles And Format

Why this matters:

- HGD source chapter titles are English. If a rerun does not have a Thai title artifact/sidecar, the reader can fall back to English titles even when the body translation is Thai.
- HGD formatting drift can hide real semantic misses. The confirmed example was `ch022-block-001`, where the source beat "Like that, four days passed." was omitted from refined/formatted/final output even though QA passed.
- HGD paragraph spacing must be checked against both the source rhythm and `C:\Users\ASUS\Downloads\good format.md`; formatting must not be judged only by whether Markdown looks clean.

Prevention now in place:

- HGD title sidecars exist for `ch001-ch080` so single-block reruns do not silently fall back to English titles.
- `scripts/check_output_quality_guardrails.py` contains the HGD `ch022` required-beat guard.
- `test_translation.py` covers the HGD `ch022` regression.
- MoonRead generation/build/smoke must be rerun after reader-facing output changes.

Rule for future HGD work:

- Before claiming HGD output is ready, verify Thai titles, paragraph spacing, and required source beats for the touched range.
- If HGD formatting looks dense or unlike `good format.md`, inspect the source and formatted Markdown before making broad repairs.
- Do not publish HGD `ch036+` as available until its titles, formatting, and final-output guardrails pass for the explicit range.

### HGD Pronoun Incident Lesson

Why this happened:

- HGD did not have an Obsidian-style durable pronoun policy like Deep Sea Embers.
- The HGD research profile, style profile, refinement prompt, and QA prompt preserved horror tone and system UI, but did not pin Seth Thorne's Thai voice.
- QA did not explicitly reject Seth `ผม`/`ฉัน` drift or Kyle/Seth address drift.

Prevention now in place:

- HGD has a local Obsidian vault at `D:\Fogust\Workspace\Novel\Horror Game Developers` and `02_Database_Views/HGD Pronoun Policy.md`.
- HGD research/style profiles and refinement/QA prompts now specify: Seth uses `ผม/ของผม/ตัวผม`; Kyle/Seth casual peer address usually uses `นาย`; `คุณ` is for system, strangers, or formal context.
- `scripts/check_output_quality_guardrails.py` checks known high-risk published HGD chapters for Seth `ฉัน` drift.
- `test_translation.py` covers the HGD pronoun guardrail.
- repair evidence is at `Deep Sea Embers/07_Reports/hgd_pronoun_consistency_repair_20260616.md`.

Rule for future HGD work:

- Do not claim HGD chapters are ready if Seth's point-of-view flips between `ผม` and `ฉัน`.
- Do not bulk-replace every `ฉัน` in HGD; female speakers and child voices can legitimately use other forms.
- For new HGD ranges, inspect pronoun counts and run output guardrails before MoonRead publication.

### New Novel Folder Rule

- Create or select the Obsidian vault folder before adding pipeline data for a new novel.
- Keep `00_Templates`, `01_Glossary`, `02_Database_Views`, `03_Raw`, `04_Work`, `05_Output`, `06_Logs`, `07_Reports`, `.system`, `prompts`, `scripts`, and profiles inside that vault folder.
- Obsidian is useful as the human/operator memory layer: glossary notes, database views, templates, style policy, pronoun policy, and source/research notes stay inspectable outside the CLI.
- Runtime scripts may use the same folder as project root, but should not overwrite `.obsidian` settings/plugins.

### V6.22 Multi-Novel / Per-Novel Layer Split

Goal: stop fixing recurring quality bugs only inside one novel path.

Layer model:

- Multi-novel layer: `00_Config/novel_registry.json` and shared scripts. This owns reader inclusion, source/output paths, generic Markdown checks, title fallback policy, truncation thresholds, and MoonRead import metadata.
- Per-novel layer: each registry entry plus that novel's Obsidian/prompt/profile notes. This owns story-specific title normalization, pronoun policy, required source beats, forbidden variants, and genre voice.

Current implementation:

- MoonRead `scripts/generate-chapters.mjs` reads enabled books from `00_Config/novel_registry.json` instead of a hardcoded DSE/HGD list.
- `scripts/check_output_quality_guardrails.py` reads the same registry for shared title fallback and truncation checks.
- Reader-facing synopsis/description/teaser text is also owned by the registry. A novel becomes eligible for source-backed MoonRead blurb translation after 60 translated/published chapters.
- DSE keeps a per-novel rule requiring translated title sidecars for named Chinese source titles.
- HGD keeps per-novel title normalization, English-title marker rejection, truncation threshold, and pronoun/required-beat checks.

Rule for future bugs:

- If the failure pattern can affect multiple novels, add the detection/prevention to the multi-novel layer.
- If the failure depends on character voice, local terminology, source-site quirks, or genre style, add only that detail to the per-novel layer.
- If a novel reaches the 60-chapter reader blurb gate, find the official/source-site synopsis where possible, adapt it into Thai using the novel glossary/style evidence, and record both the adapted text and source URL/note in the registry.

Done when:

- registry-driven MoonRead generation passes
- registry-driven output guardrail passes
- tests cover the registry contract
- docs explain where future novel settings belong

### V6.22.1 Reader Blurb Maturity Rule

Goal: prevent MoonRead home pages from using placeholder descriptions after enough translated chapters exist to adapt source-backed descriptions reliably.

Rule:

- At 60 translated/published chapters, a novel is considered to have enough glossary and style evidence for a Thai synopsis, description, or teaser.
- The source should come from the original/fetch site when available. If the fetch chapter URL does not expose a synopsis, use a reliable official listing and record that choice in `synopsis_source_note`.
- The adapted Thai blurb must live in `00_Config/novel_registry.json`, not inside MoonRead code.
- MoonRead generated manifests may expose `synopsisSourceUrl` and `synopsisSourceNote` for auditability, but the reader UI does not need to show source links unless explicitly requested.

Current application:

- Deep Sea Embers has 80 published MoonRead chapters, so the registry now uses a Thai adaptation of the official WeRead/Qidian-style blurb.
- Horror Game Developer has 80 published MoonRead chapters, so the registry now uses a Thai adaptation of the RoliaScan novel-page blurb.

Done when:

- both registry entries include non-empty `synopsis`, `synopsis_source_url`, and `synopsis_source_note`
- registry contract tests cover the 60-chapter threshold
- MoonRead generated library includes the updated Thai blurbs
- MoonRead generate/lint/build/smoke passes

Current repository state:

- tracked `Deep Sea Embers` git state is clean after commit `8ac0d72`
- root docs live outside the nested git repo and must be managed as local canonical workspace files
- `DOC_RECOVERY.md` records current hashes and backup/restore steps for the canonical root docs; latest snapshot is `99_Adhoc_Scripts/canonical_docs_backup_20260616_121900`
- visible untracked glossary/report queue remains partly undecided: 46 glossary notes and 14 intermediate/probe reports remain visible; 5 durable provider/glossary evidence reports were committed at `0d3187d`. Queue classification is at `Deep Sea Embers/07_Reports/v6_13_untracked_queue_classification_20260616.md`; glossary queue review is at `Deep Sea Embers/07_Reports/v6_13_glossary_queue_review_20260616.md`; alias overlap proposal is at `Deep Sea Embers/07_Reports/v6_13_glossary_alias_overlap_proposal_20260616.md`; glossary cleanup execution proposal is at `Deep Sea Embers/07_Reports/v6_13_glossary_queue_cleanup_execution_proposal_20260616.md`; report queue review is at `Deep Sea Embers/07_Reports/v6_13_report_queue_review_20260616.md`; report cleanup proposal is at `Deep Sea Embers/07_Reports/v6_13_report_queue_cleanup_proposal_20260616.md`; do not commit/delete the remaining queue blindly
- latest readiness reports are at `Deep Sea Embers/07_Reports/preflight_report_20260616_after_v6_18_gate.md`, `Deep Sea Embers/07_Reports/recovery_drill_20260616_after_v6_18_gate.md`, and `Deep Sea Embers/07_Reports/preflight_recovery_readiness_note_20260616.md`
- latest DSE product review reports are at `Deep Sea Embers/07_Reports/product_review_deep-sea-embers-retranslate-ch001-ch050-v2_20260616.md`, `Deep Sea Embers/07_Reports/provider_usage_deep-sea-embers-retranslate-ch001-ch050-v2_20260616.md`, and `Deep Sea Embers/07_Reports/product_review_readiness_note_20260616.md`; degraded status is due to documented untracked queue, while outputs and run state pass

## Work Policy

- Codex plans, verifies, reviews, and owns architecture.
- Worker models only implement bounded tasks.
- Worker completion reports are claims until checked against files, tests, reports, and `git diff`.
- Keep changes surgical.
- Stop on unclear scope, risky provider change, manual QA prompt, validation failure, or unexpected artifact mutation.
- Commit/push after stable repo milestones.

## Completed Milestone: V6.17.1 HGD Title And Format Re-Audit

Goal: resolve the user-reported HGD reader issues before any more V6.18 speed work.

Why this is reopened:

- HGD chapter titles are still suspicious because some reader titles appear in English. The expected product surface is Thai titles.
- HGD body text still had narrow English leakage in published output, including `Horror Developer System`, `Developer Seth Thorne`, `Jump Scare`, `Scenario`, `Section Chief`, and selected sound effects in `ch022`.
- HGD formatting may not match the source rhythm or `C:\Users\ASUS\Downloads\good format.md`.
- The first read of `good format.md` showed mojibake-like Thai corruption under UTF-8, so the example file itself must be decoded/verified before using it as a formatting authority.
- MoonRead UX/UI handoff arrived in `Deep Sea Embers/07_Reports/v6_19_moonread_ux_handoff_20260616.md`; reader generation, lint, build, smoke, and output guardrails passed after the HGD repair.

### V6.17.1A: HGD Thai Title Audit

Check:

- inspect HGD source titles and current title sidecars for the published range `ch001-ch035`
- verify MoonRead-visible titles are Thai, not English fallback
- verify title translation uses the same title policy as body text: literal meaning first, then refinement, with glossary consistency
- identify whether the English title problem comes from missing sidecars, stale generated MoonRead metadata, or title assembly fallback

Fix only after cause is known:

- if sidecars are missing/wrong, repair sidecars for the affected range
- if MoonRead metadata is stale, regenerate reader chapters
- if assembly fallback is wrong, add a guard/test so English fallback cannot silently publish for HGD

Done when:

- `ch001-ch035` MoonRead HGD titles are Thai
- no English source title remains visible for published HGD chapters unless explicitly intended as a proper noun
- a deterministic check or test guards the title fallback path

### V6.17.1A2: HGD English Leakage Repair

Status:

- repaired in HGD `05_Output` for the known leakage set
- guardrail added in `scripts/check_output_quality_guardrails.py` for both HGD output and generated HGD reader chapters
- MoonRead regeneration/build/smoke completed after the Claude handoff and HGD leakage repair

Known repaired terms:

- `Horror Developer System` -> `ระบบนักพัฒนาเกมสยองขวัญ`
- `Developer Seth Thorne` -> `นักพัฒนาเซธ ธอร์น`
- `Jump Scare` -> `ฉากสะดุ้ง`
- `[Scenario]` -> `[ฉาก]`
- `[Section Chief]` / `(Section Chief)` -> `หัวหน้าแผนก`
- `*Click!*`, `*Takakakakaka—*`, `*Tak!*`, `*To Tok—*` -> Thai sound effects
- `[Seth's USB stick]` -> `[แฟลชไดรฟ์ USB ของเซธ]`

### V6.17.1B: HGD Format Source Audit

Check:

- inspect original HGD source formatting for representative chapters, starting with `ch001`, `ch022`, and at least one dense later chapter
- inspect current final Markdown and MoonRead rendering for the same chapters
- decode/verify `C:\Users\ASUS\Downloads\good format.md` before using it; if UTF-8 read shows mojibake, find the correct encoding or ask for a clean reference
- compare paragraph spacing, dialogue lines, system messages, thoughts, sound effects, skill/status brackets, and scene separators

Rules:

- do not use local formatting as the sole authority for dialogue/thought/sound-effect detection
- AI formatting remains preferred for semantic layout, but deterministic validation must catch corruption, missing source beats, excessive density, provider/meta leakage, and unintended Chinese body text
- do not bulk-reformat all HGD output until the source/example comparison is understood

Done when:

- `Deep Sea Embers/07_Reports/v6_17_1_hgd_title_format_reaudit_20260616.md` records the title/format audit findings
- the affected published range has either been repaired or has an explicit bounded repair plan
- `good format.md` is documented as not safe to use as direct authority until a clean reference is supplied
- MoonRead generate/lint/build/smoke passes after reader-facing regeneration

### V6.17.1 Stop Conditions

Stop and report before continuing if:

- source and current output disagree on content, not just spacing
- `good format.md` cannot be decoded cleanly
- title repair would require changing glossary/title policy
- repair scope expands beyond HGD `ch001-ch035`
- MoonRead generated metadata differs from final Markdown in a way that is not understood

V6.17.1 is done only when:

- HGD title cause is known and fixed for the published range: title sidecars and generated MoonRead metadata publish Thai titles
- HGD formatting cause is known and either fixed or converted into a bounded repair milestone: known English leakage was repaired; broad paragraph-density reflow is deferred until a clean formatting reference is available
- tests/guardrails cover the recurrence path: HGD English leakage and required source-beat checks are in `scripts/check_output_quality_guardrails.py`
- docs record the prevention mechanism: this section and `PROJECT_BRAIN.md`

## Completed Milestone: V6.18 Translation Speed Without Quality Loss

Goal: reduce wall-clock time for bounded translation runs without weakening glossary approval, semantic QA, AI formatting quality, or Codex review.

Current status:

- complete for the first narrow runtime slice
- runtime concurrency remains disabled by default
- runtime cache skip remains disabled
- runtime Pre-QA blocking remains disabled
- read-only run planning, cache benchmark, concurrency benchmark, approval protocol, command packet, minimal design, runtime-slice reports, and actual ch051 benchmark evidence exist
- the smallest formatting-only runtime slice now exists and is proven behind explicit execution config; default runtime concurrency remains disabled
- test coverage now guards that configured stage concurrency remains inert unless `execution.concurrency_enabled` is explicitly true
- actual benchmark evidence: `Deep Sea Embers/07_Reports/v6_18_ch051_actual_formatting_parallel_benchmark_20260616.md`
- benchmark result: 5 QA-ready blocks formatted with `parallel_limit: 2`; wall-clock `143.167s` versus same-run sequential-duration estimate `253.188s`, about `43.5%` reduction
- `ch051` output exists and passed cleanliness/output guardrails; this does not approve a new production batch

Current config must remain conservative unless explicitly changed for an approved benchmark:

```yaml
execution:
  concurrency_enabled: false
  artifact_cache:
    mode: report_only
  pre_qa_guardrail:
    mode: report_only
```

### V6.18A: Limited Parallel Block Execution

Purpose: reduce waiting time by running safe stage/provider work in limited parallel.

Current evidence:

- read-only concurrency benchmark reports exist
- provider-separated report shows `formatting/openrouter` is the only row ready for a small benchmark
- global runtime concurrency is not enabled
- runtime implementation gap has been closed for formatting-ready blocks in bounded resume only

Next allowed implementation:

- do not broaden runtime concurrency beyond formatting-ready blocks
- do not run the benchmark until the user chooses the benchmark target
- if enabling this slice in normal operations later, require an explicit config change and one more bounded production confirmation

Stop conditions:

- provider failure
- command too long
- QA hard-fail
- manual prompt
- formatting validation failure
- output guardrail failure
- scope expands beyond the approved chapter
- any unapproved chapter is processed

Done when:

- benchmark report compares baseline vs benchmark timing: done in `v6_18_ch051_actual_formatting_parallel_benchmark_20260616.md`
- final output passes guardrails: done for `ch051`
- no QA/formatting regression occurs: done; no hard-fail or formatting validation failure
- runtime concurrency remains disabled after benchmark unless separately approved: done

### V6.18B: Artifact Hash Cache And Stage Skip

Purpose: avoid repeated provider calls when source, prompt, glossary, provider/model, and prior artifact hash are unchanged.

Current evidence:

- literal translation cache skip exists behind explicit config only
- `.system/config.yaml` remains `artifact_cache.mode: report_only`
- current cache benchmark decision is `not_ready` because clean timing baseline is insufficient

Next allowed implementation:

- keep cache report-only
- improve read-only evidence if needed
- do not enable cache skipping without separate approval and benchmark evidence

Done when:

- cache decisions are visible
- hash invalidation covers source, prompt, glossary, provider/model, style/research profile, and prior artifact
- no stale-cache incident is found by guardrails
- user approves enabling a specific cache stage

### V6.18C: Deterministic Pre-QA Guardrail

Purpose: catch obvious bad refined text before expensive AI QA.

Current evidence:

- runtime blocking exists only behind `execution.pre_qa_guardrail.mode: blocking`
- default config remains `report_only`
- preview scans refined artifacts and reports hard errors/warnings

Next allowed implementation:

- keep report-only by default
- only promote narrow, high-confidence checks after real user-reported issues
- do not replace semantic QA

Done when:

- blocking rules are explainable and narrow
- report-only evidence shows low false-positive risk
- if blocking is enabled later, it stops before QA only for obvious bad output

### V6.18D: Codex-Controlled Routing And Checkpoint Assistant

Purpose: make planning faster while keeping final decisions human/Codex-controlled.

Current evidence:

- `novel-pipeline report run-plan --run-id <run-id>` exists
- report includes provider readiness, routing/fallbacks, timing baseline, cache readiness, pre-QA preview, benchmark scope plan, and suggested commands
- report is read-only and does not execute providers or change routing

Done when:

- Codex can use the report to approve/reject a bounded run faster
- recommendations remain advisory
- no provider route changes happen automatically

### V6.18 Benchmark Approval Gate

Benchmark scope approved and executed:

```text
V6.18 formatting/openrouter concurrency=2 benchmark on ch051.
```

Protocol reports:

- `Deep Sea Embers/07_Reports/v6_18_benchmark_approval_protocol_20260616.md` (pushed at `1a969b0`)
- `Deep Sea Embers/07_Reports/v6_18_current_gate_status_20260616.md` (pushed at `7241c4a`)
- `Deep Sea Embers/07_Reports/v6_18_benchmark_command_packet_20260616.md` (pushed at `38cc6b8`)
- `Deep Sea Embers/07_Reports/v6_18_minimal_formatting_parallel_design_20260616.md` (pushed at `de28003`)
- `Deep Sea Embers/07_Reports/v6_18_completion_gate_recheck_20260616.md` (current workspace; records why V6.18 cannot close yet)
- `Deep Sea Embers/07_Reports/v6_18_formatting_parallel_runtime_slice_20260616.md` (current workspace; records the guarded runtime slice)

The benchmark passed. Keep this section as historical proof, not as approval to enable broader concurrency.

V6.18 is done only when:

- an approved benchmark proves speed improvement
- reports show timing, provider calls, failures, retries, and output guardrail results
- AI formatting remains primary and follows `C:\Users\ASUS\Downloads\good format.md`
- rollback path exists for concurrency/cache/pre-QA blocking

## Completed Milestone: V6.19 MoonRead UX/UI Cleanup

Goal: remove internal jargon from the reader, rewrite synopses from actual chapter content, and convert the homepage from a single-novel focus to a library-first design.

Completed by: Claude (Opus 4.6 session, 2026-06-16)

Changes:

- `scripts/generate-chapters.mjs`: rewrote DSE and HGD synopses from chapter content, fixed thaiTitle/author/tags, removed translator field
- `app/page.js`: replaced DSE-focused hero with library-first "ชั้นนิยาย" page showing all novels equally
- `app/book/page.js`: removed "ที่มา" (source) field, "Private Thai translation pipeline" text, simplified eyebrow/status
- `app/books/[bookSlug]/page.js`: same jargon removal as book/page.js
- `components/SiteHeader.js`: nav labels updated ("ชั้นนิยาย", "Deep Sea Embers")
- `lib/chapters.js`: fallback thaiTitle/author updated, translator removed
- `app/globals.css`: added .library-hero, .library-thai-title styles
- `scripts/smoke-reader.mjs`: fixed `horrorBookTitle` scope bug in page.evaluate, updated homepage assertions for library-first layout

Verification: lint clean, build 92 pages, smoke `ok: true`

## Completed Milestone: V6.19.1 MoonRead UX/UI Polish And Cover Art

Goal: fix 13 remaining UX/UI issues identified after V6.19, integrate Codex-generated cover art for both novels.

Completed by: Claude (Opus 4.6 session, 2026-06-16)

Changes:

- `app/chapters/page.js`: eyebrow "Table of contents" → "สารบัญ", removed technical jargon from description
- `app/books/[bookSlug]/chapters/page.js`: same jargon fix as DSE chapters page
- `components/ReaderShell.js`: theme labels "Paper/Sepia/Night" → "กระดาษ/ซีเปีย/กลางคืน", localStorage key migrated from `dse-reader-settings` to `moonread-reader-settings` with backward-compatible read
- `components/NavLinks.js` (new): client component using `usePathname()` for active nav link highlighting
- `components/SiteFooter.js` (new): site-wide footer with brand, nav links, and tagline
- `components/SiteHeader.js`: refactored to use NavLinks client component for active state
- `app/page.js`: swapped primary/secondary action buttons, added `library-synopsis` class for line-clamping
- `app/layout.js`: metadata description changed to Thai
- `app/book/page.js`, `app/books/[bookSlug]/page.js`, `app/chapters/page.js`, `app/books/[bookSlug]/chapters/page.js`: added SiteFooter to all site-shell pages
- `app/books/[bookSlug]/page.js`: made `logo-cover` class conditional based on cover path
- `app/globals.css`: nav active state, library-hero border, status-band gold numbers, logo-cover placeholder, library-synopsis line-clamp, drawer using CSS variable, footer styles, mobile library-cover sizing
- `scripts/generate-chapters.mjs`: HGD cover changed from logo fallback to `/images/horror-game-developer-cover.png`
- `scripts/smoke-reader.mjs`: updated for Thai theme labels, new localStorage key, scoped nav link selector for footer disambiguation
- Cover art: Codex-generated `deep-sea-embers-cover-v1.png` and `horror-game-developer-cover-v1.png` copied to `public/images/`

Verification: lint clean, build 92 pages, smoke `ok: true`

## Completed Milestone: V6.20 MoonRead Nav And Homepage Improvement

Goal: fix nav overlap, remove hardcoded DSE-only nav links, improve homepage card spacing for multi-book scalability.

Completed by: Claude (Opus 4.6 session, 2026-06-16)

Changes:

- `components/NavLinks.js`: reduced from 3 hardcoded links to 1 ("หน้าแรก" → `/`); removed DSE-only "Deep Sea Embers" (`/book`) and "สารบัญ" (`/chapters`) links; removed unused `BookOpen`/`List` imports
- `components/SiteFooter.js`: replaced 2 footer links ("ชั้นนิยาย", "สารบัญ") with single "หน้าแรก" link; removed DSE-only `/chapters` reference
- `app/globals.css`: added `min-width: 0` to `.site-nav` to prevent grid blowout/overlap with logo; changed mobile nav grid from `repeat(3, ...)` to `repeat(auto-fit, ...)` to adapt to any link count; added `.library-grid` class for 20px gap between book cards
- `app/page.js`: wrapped book cards in `.library-grid` div for proper spacing
- `scripts/smoke-reader.mjs`: replaced nav "สารบัญ" click with direct `page.goto(/chapters)`; added `hasHomeNavLink` check for "หน้าแรก" in primary nav; added to `result.ok` conjunction

Verification: generate:chapters (2 books, 85 available), lint clean, build 92 pages, smoke `ok: true`

Handoff report: `Deep Sea Embers/07_Reports/v6_20_nav_homepage_handoff_20260616.md`

### V6.20.1: MoonRead UX/UI Enhancement — Images, 404, OG ✅

Completed: 2026-06-17

Goal: integrate user-provided artwork into the MoonRead reader for a more polished, branded experience — hero banner, Open Graph / Twitter Card metadata, custom 404 page with illustration, and apple-touch-icon.

Changes:

- `app/layout.js`: added `metadataBase`, `icons.apple`, full `openGraph` and `twitter` metadata
- `app/not-found.js`: updated from text-only to illustration + Thai copy + link to `/`
- `app/page.js`: added `has-banner` class to `.library-hero` for CSS background-image
- `app/globals.css`: hero banner background styles, 404 illustration styles, responsive rules (shrink at 960px, hide at 680px)
- `scripts/smoke-reader.mjs`: OG evidence checks, 404 page evidence checks, console error splitting for intentional 404 navigation, 404 screenshot
- Placeholder 1×1 transparent PNGs created for `hero-banner.png`, `og-image.png`, `404-cat.png`, `apple-touch-icon.png` — user replaces with actual processed images

Verification: generate:chapters (2 books, 160 available), lint clean, build 167 pages, smoke `ok: true`

Handoff report: `Deep Sea Embers/07_Reports/v6_20_1_ux_images_handoff_20260617.md`

User action required: replace 4 placeholder PNGs in `MoonRead/public/images/` with actual processed images.

### V6.21: Continue Deep Sea Embers Beyond ch050

Goal: continue translation only after V6.18 decision or explicit user priority change.

Required before starting:

- confirm source availability after `ch050`
- choose bounded range and run ID
- run scan-only gate
- approve glossary
- generate run-plan report
- confirm provider routing and stop conditions

Do not start this milestone without explicit user approval.

## Planned Milestone: V6.30 Language Playbooks

Goal: create reusable language-level operating notes so a new novel in a known source language starts with fewer repeated mistakes.

Why this exists:

- The project has now handled Chinese-to-Thai and English-to-Thai production output.
- Some recurring failures are language-specific, not only novel-specific: Chinese chapter-title sidecars and named terms; English UI/game terms, parenthetical leakage, pronoun voice, and sound effects.
- A language playbook should sit between the multi-novel policy layer and each novel profile. It should reduce setup risk without becoming a long history file.

Scope:

- Create `00_Config/language_playbooks/chinese_to_thai.md`.
- Create `00_Config/language_playbooks/english_to_thai.md`.
- Link both files from the new-novel setup flow and documentation.
- Keep novel-specific glossary, pronoun policy, title mappings, and source-site quirks in the novel profile/vault, not in the language playbook.

Each playbook must include:

- title translation rules
- pronoun and register risks
- name transliteration risks
- glossary candidate policy
- dialogue, thought, UI, skill, and sound-effect formatting expectations
- common false positives and false negatives
- QA/Sentinel checks that should be enabled for that language
- short examples of bad output -> preferred output

Language-specific starting points:

- Chinese-to-Thai: require translated title sidecars for named Chinese chapter titles; watch for compact proper nouns, honorific/title terms, cultivation/lore terms, and source-language leakage in body text.
- English-to-Thai: watch for English original leakage, parenthetical bilingual leftovers, game/system UI terms, rank/role drift, sound-effect translation, markdown emphasis, and first-person pronoun consistency.

Done when:

- both playbook files exist and are short enough to be read during setup
- `PROJECT_BRAIN.md` mentions language playbooks as part of the multi-novel operating model
- `IMPLEMENT_PLAN.md` and setup docs explain that new novel setup should choose a language playbook before glossary scan
- no provider routing, translation artifacts, ledger, glossary notes, or MoonRead generated content are changed
- deterministic verification passes: `git diff --check`, doc UTF-8 read, and working tree contains only intended docs/playbook files

Feedback loop:

1. When a language-specific issue recurs, add a compact rule or example to the relevant playbook.
2. If the rule is actually novel-specific, record it in that novel's profile/vault instead.
3. If the rule is safe across all languages, promote it to the multi-novel Sentinel or registry layer.
4. After every new-novel setup, note which playbook was used and whether it prevented or missed any setup defects.

## Completed Milestone: V6.31 Architecture Map

Completed: 2026-06-23

Goal: create one compact architecture document that explains how the whole translation product works today, where each source of truth lives, and how future agents should reason about boundaries before editing.

Why this exists:

- The system now spans pipeline code, provider routing, language/novel policy, glossary workflow, Sentinel, dashboard, MoonRead, reports, and recovery.
- `PROJECT_BRAIN.md` should not carry the entire architecture. It should stay focused on current state, risks, and guardrails.
- `IMPLEMENT_PLAN.md` should not become an architecture manual. It should describe milestones and acceptance gates.
- Future workers need a stable map so they do not accidentally fix the wrong layer, duplicate policy, or treat generated reader files as source of truth.

Primary artifact:

- Create `ARCHITECTURE.md` at `D:\Fogust\Workspace\Novel\ARCHITECTURE.md`.

Document shape:

1. System Purpose
   - what the product does
   - what it explicitly does not do
   - who uses it: user, Codex architect, bounded worker, dashboard operator

2. Source Of Truth Map
   - `AGENTS.md`: work policy
   - `PROJECT_BRAIN.md`: current state, risks, guardrails
   - `IMPLEMENT_PLAN.md`: roadmap and milestone acceptance
   - `ARCHITECTURE.md`: system structure and boundaries
   - `DOC_RECOVERY.md`: canonical doc recovery hashes
   - `00_Config/novel_registry.json`: registered novels, reader scope, shared quality metadata
   - `00_Config/language_playbooks/*.md`: reusable language-level translation rules
   - `.system/config.yaml` and `.system/providers.yaml`: pipeline and provider routing for the current runtime
   - `03_Raw/`: fetched source
   - `04_Work/`: intermediate artifacts
   - `05_Output/`: final translated Markdown product
   - `06_Logs/run_ledger.jsonl`: append-only execution history
   - `07_Reports/`: evidence and handoff reports
   - `MoonRead/content/generated/`: generated reader copy, not translation source of truth

3. Layer Model
   - Layer 0: multi-novel shared policy, registry, shared guardrails, Sentinel base rules
   - Layer 1: language playbook, such as Chinese-to-Thai and English-to-Thai
   - Layer 2: novel profile/vault, glossary, pronoun policy, title policy, source-site quirks
   - Layer 3: run/batch artifacts, ledger, reports, recovery state
   - Layer 4: MoonRead reader surface and generated content
   - rule: fix a recurring issue at the lowest layer that catches it safely; promote only after evidence proves the rule is general

4. Pipeline Flow
   - setup/fetch
   - source validation and chapter numbering check
   - split/blocking
   - glossary scan
   - glossary approval
   - literal translation
   - refinement
   - QA
   - AI formatting
   - deterministic output validation
   - Sentinel
   - final assembly
   - report generation
   - MoonRead generation and scoped publish verification

5. Actor / Employee Map
   - Ferryman: setup, fetch, project entry
   - Libra: glossary scan/approval and glossary coverage
   - Quill: literal translation
   - Vesper: refinement
   - Corvus: QA
   - Loom: formatting
   - Sentinel: post-output quality gate
   - Archivist: reports and output records
   - Warden: recovery and rerun flow
   - note that employee names are dashboard/docs aliases; ledger/config stage names remain authoritative

6. Provider Routing Map
   - role -> provider/model -> fallback chain
   - note which routes are production, fallback, benchmark-only, or explicitly banned
   - document that provider routing changes require explicit user approval and tests

7. Guardrail Stack
   - provider output validation
   - QA stage
   - output quality guardrail
   - Libra glossary coverage
   - Sentinel report/gate
   - MoonRead generator validation
   - MoonRead scoped `publish:verify`
   - major-run spot-check checklist

8. Failure And Recovery Model
   - provider failure
   - command length failure
   - QA hard-fail
   - formatting validation failure
   - Sentinel blocker/major finding
   - source chapter numbering mismatch
   - MoonRead generation/build/smoke failure
   - rule: stop, inspect, repair from earliest broken stage, rerun scoped verification, then record cause/prevention

9. New Novel Setup Flow
   - create/open novel vault
   - register novel
   - choose language playbook
   - research novel and save profile
   - configure/fix fetch adapter
   - run source/fetch validation
   - scan glossary
   - approve glossary terms
   - run bounded translation
   - publish verified MoonRead output

10. Boundaries And Non-Goals
   - MoonRead does not edit translation artifacts
   - ledger is append-only
   - generated reader content is disposable/regenerable
   - worker reports are claims until verified
   - do not store cross-novel durable policy inside one novel folder
   - do not add provider calls to docs-only or architecture-only tasks

Implementation steps:

1. Read `AGENTS.md`, `PROJECT_BRAIN.md`, `IMPLEMENT_PLAN.md`, `DOC_RECOVERY.md`, `00_Config/novel_registry.json`, `MoonRead/package.json`, and current provider config.
2. Draft `ARCHITECTURE.md` with the sections above.
3. Keep it compact enough for Codex/workers to read before work. Target about 150-250 lines.
4. Prune architecture duplication from `PROJECT_BRAIN.md` after `ARCHITECTURE.md` exists:
   - move durable structure into `ARCHITECTURE.md`
   - leave only current verified state, current risks, short current routing summary, active guardrails, and next safe action in `PROJECT_BRAIN.md`
   - replace removed sections with a short pointer to `ARCHITECTURE.md`
   - do not remove current incidents or risks that still affect operations
5. Add a short reference to `ARCHITECTURE.md` in `PROJECT_BRAIN.md` and `AGENTS.md`.
6. Do not move files, change runtime behavior, edit generated MoonRead content, or change provider routing in this milestone.

Done when:

- `ARCHITECTURE.md` exists at repo root
- it clearly separates source of truth, layers, pipeline flow, actors, provider routing, guardrails, recovery, and new-novel setup
- architecture-level duplication is removed from `PROJECT_BRAIN.md` after being preserved in `ARCHITECTURE.md`
- `PROJECT_BRAIN.md` and `AGENTS.md` reference it as the architecture source
- `PROJECT_BRAIN.md` remains compact and current-state focused, not a second architecture manual
- no code/config/runtime artifacts are modified
- deterministic verification passes: `git diff --check`, UTF-8 read of all touched docs, and `git status --short --untracked-files=all`

Feedback loop:

1. When a future incident shows confusion about layer/source-of-truth ownership, update `ARCHITECTURE.md` with the smallest clarifying rule.
2. If the update is about current state, put it in `PROJECT_BRAIN.md` instead.
3. If the update is about future work, put it in `IMPLEMENT_PLAN.md` instead.
4. If the update is about agent behavior, put it in `AGENTS.md` instead.

## Backlog

Use this order unless the user changes priorities:

1. Implement V6.30 Language Playbooks before onboarding another novel in Chinese or English.
2. Continue Deep Sea Embers from a new scan-only gate if the user approves production translation beyond ch050.
3. Decide whether formatting-only concurrency should remain benchmark-only or become an operator-approved option.
4. Improve provider QA reliability if false passes or parse failures recur.
5. Decide visible untracked glossary/report queue: resolve the `真实的太阳神` / `实太阳神` shared-Thai rendering question, then archive the 14 intermediate/probe reports if a cleaner report directory is needed; discard only by explicit decision.
6. Expand multi-novel support when a second full novel workflow is actively needed.
7. Polish dashboard UX only where it reduces operator errors.

## Acceptance Gates For Any Milestone

A milestone is not done until:

- relevant tests/checks pass
- generated output is inspected when UI or reader content changed
- major translation/repair/publication runs pass the major-run spot-check checklist
- provider calls are only made when the milestone explicitly needs them
- no forbidden files are modified
- `git diff` matches intended scope
- docs mention any new operational rule or recurring risk
- user-facing report is clear enough to resume later

Major-run spot-check checklist:

- Applies to multi-chapter translation batches, broad repair passes, and MoonRead publication updates.
- Sample at least 5 chapters: first, last, one early-middle, one late-middle, and one chapter with known recovery/provider incident if any.
- For each sample, inspect H1 title, first paragraphs, one middle section, ending, paragraph density, dialogue/thought formatting, glossary/name consistency, and obvious omission/truncation.
- Run deterministic output guardrails for the touched range.
- If MoonRead content changed, run `npm.cmd run generate:chapters`, `npm.cmd run lint`, `npm.cmd run build`, and `npm.cmd run smoke`.
- If the sample exposes a repeated pattern, repair the full affected range, add or extend a deterministic guardrail, regenerate MoonRead if needed, and record cause/prevention in the run report.

## Do Not Do Without Explicit Approval

- start a new production translation batch
- change provider routing
- force-accept semantic QA failure
- delete untracked backups/reports/glossary files
- manually rewrite source artifacts
- publish incomplete chapters as available in MoonRead
- enable runtime concurrency/cache/Pre-QA blocking
- run the V6.18 benchmark
- use Elephant or Nemotron for state-changing work

## Standard Verification Commands

Pipeline:

```powershell
cd "D:\Fogust\Workspace\Novel\Deep Sea Embers"
$env:PYTHONIOENCODING='utf-8'
python -m compileall novel_pipeline
python test_translation.py
novel-pipeline --config ".system/config.yaml" preflight
python scripts\check_output_quality_guardrails.py
```

MoonRead:

```powershell
cd "D:\Fogust\Workspace\Novel\MoonRead"
npm.cmd run generate:chapters
npm.cmd run lint
npm.cmd run build
npm.cmd run smoke
```

Git:

```powershell
cd "D:\Fogust\Workspace\Novel\Deep Sea Embers"
git status --short
git diff --check
```
