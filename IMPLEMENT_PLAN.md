# Implement Plan

Last updated: 2026-06-17

This is the active roadmap. It should answer: what is done, what is next, when to stop, and how to verify completion. Long history belongs in `Deep Sea Embers/07_Reports/`, not here.

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
- HGD pronoun consistency repair closed for published scope: Seth-dominant chapters now use `ผม` consistently, HGD has an Obsidian pronoun policy note, prompts/profile/QA include the rule, and output guardrails cover known high-risk chapters

Current production state:

- Deep Sea Embers `ch001-ch080` translated and repaired in `05_Output/`
- MoonRead contains Deep Sea Embers `ch001-ch080`
- MoonRead contains Horror Game Developer `ch001-ch100`
- MoonRead app now lives at `D:\Fogust\Workspace\Novel\MoonRead`; `Deep Sea Embers\reader-web` is only a compatibility stub
- HGD `ch022` missing time-skip issue repaired and guarded
- HGD title fallback risk guarded by title sidecars for `ch001-ch080`
- HGD pronoun drift risk guarded by `Horror Game Developers/02_Database_Views/HGD Pronoun Policy.md`, HGD prompt/profile rules, and `scripts/check_output_quality_guardrails.py`
- HGD title/truncation repair closed for MoonRead `ch001-ch080`: titles normalized, `ch002`/`ch060`/`ch072` truncations repaired, and source-vs-output truncation guardrail added
- HGD continuation active: `hgd-ch101-ch180` completed as translated output toward `ch200`; MoonRead remains published through `ch100`
- V6.23 pipeline smoothness fixes were verified during `hgd-ch091-ch100-v1`: batch glossary approval, QA repair-safe reruns, and HGD title fail-fast normalization all worked in production.
- V6.24 control packet/pre-resume gate was applied to `hgd-ch101-ch110-v1`; two QA hard-fails were recovered with repair-safe `--no-auto-refine` flow (`ch103` missing sound effects, `ch109` missing poem lines/personified pronouns)
- V6.24 QA omission recovery automation was added and exercised during `hgd-ch111-ch120-v1`: after ordinary QA retries, omission hard-fails can restore literal-safe refined text once and rerun QA instead of forcing Codex to hand-edit JSON artifacts.
- V6.24 latest-refined-before-formatting fix was added during `hgd-ch121-ch130-v1`: after QA retry writes a newer refined artifact, formatting reloads that artifact instead of using stale in-memory refined text.
- `hgd-ch131-ch140-v1` completed with one bounded pronoun repair on `ch136`; QA passed after `--no-auto-refine`, output guardrails passed, and no current failed blocks remain.
- `hgd-ch141-ch150-v1` completed with bounded repairs for `ch142` glossary/pronoun drift, `ch143` Seth thought pronouns, `ch146` stale formatted artifact after local recovery, `ch148` quest-term confusion, `ch149` Seth dialogue pronouns, and `ch150` rank/unscary mistranslations. Status reports all 10 blocks complete, no current failed blocks, output guardrails passed, and checkpoint report exists at `Horror Game Developers/07_Reports/hgd_ch141_ch150_checkpoint.md`.
- `hgd-ch151-ch160-v1` completed with no current failed blocks and output guardrails passed. During this run, QA routing was corrected so normal HGD QA uses `openrouter_reasoning` + `deepseek/deepseek-v4-flash`; `deepseek/deepseek-v4-pro` was removed from the normal fallback path, and new QA ledger records include `metadata.model`.
- `hgd-ch161-ch170-v1` completed with no current failed blocks and output guardrails passed. QA used only V4 Flash reasoning or Qwen fallback; no V4 Pro QA route was used.
- `hgd-ch171-ch180-v1` completed with no current failed blocks and output guardrails passed. `ch176` needed bounded recovery for Seth pronoun drift plus missing Dreamwalker/Mirelle tail content; QA passed after repair. QA used only V4 Flash reasoning or Qwen fallback; no V4 Pro QA route was used.
- no current failed blocks are known
- notable approved Deep Sea Embers terms include `实太阳神` -> `สุริยเทพที่แท้จริง` and `面具神` -> `เทพหน้ากาก`

## Active Milestone: V6.24 Pipeline Smoothness V2

Goal: make HGD `ch101-ch200` continuation less dependent on Codex manually editing artifacts while keeping the same translation quality bar.

Why this milestone exists:

- The pipeline is currently safe but not smooth. It correctly stops on QA hard-fails, missing title mappings, provider failures, and validation risks, but the recovery flow still pushes Codex into repeated file inspection and artifact edits.
- V6.23 improved the worst problems, but `hgd-ch081-ch100` still required manual intervention for glossary decisions, QA repair, title sidecars, and final verification.
- The target behavior is not "never stop." The target is: when the pipeline stops, it should produce a clear diagnosis, a bounded recovery command, and a reportable next safe action.

Current verified HGD continuation state:

- latest completed run id: `hgd-ch171-ch180-v1`
- completed stages: all production stages through chapter assembly for `ch101-ch180`
- next stage: checkpoint commit, then scan-only gate for `ch181-ch190`
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

## Backlog

Use this order unless the user changes priorities:

1. Continue Deep Sea Embers from a new scan-only gate if the user approves production translation beyond ch050.
2. Decide whether formatting-only concurrency should remain benchmark-only or become an operator-approved option.
3. Improve provider QA reliability if false passes or parse failures recur.
4. Decide visible untracked glossary/report queue: resolve the `真实的太阳神` / `实太阳神` shared-Thai rendering question, then archive the 14 intermediate/probe reports if a cleaner report directory is needed; discard only by explicit decision.
5. Expand multi-novel support when a second full novel workflow is actively needed.
6. Polish dashboard UX only where it reduces operator errors.

## Acceptance Gates For Any Milestone

A milestone is not done until:

- relevant tests/checks pass
- generated output is inspected when UI or reader content changed
- provider calls are only made when the milestone explicitly needs them
- no forbidden files are modified
- `git diff` matches intended scope
- docs mention any new operational rule or recurring risk
- user-facing report is clear enough to resume later

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
