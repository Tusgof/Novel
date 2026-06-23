# Project Brain: Novel Translation System

Last updated: 2026-06-22

This is the durable memory for the workspace. Keep it compact. Put long evidence, experiments, and historical detail in `Deep Sea Embers/07_Reports/`.

## Purpose

Build a practical Chinese/English-to-Thai novel translation system that can:

- fetch/source chapters through configurable adapters
- scan and approve glossary terms before translation
- translate bounded batches with auditable artifacts
- keep names, titles, pronouns, glossary, and style consistent
- recover failed blocks without corrupting prior work
- publish verified Markdown into MoonRead
- support multiple novels and genres without relying on Codex memory

Codex is the architect, reviewer, and verifier. Worker models may implement bounded tasks, but their reports are claims until files, tests, reports, and diffs prove them.

## Canonical Files

Project-level control files live at `D:\Fogust\Workspace\Novel`:

- `AGENTS.md`: work policy and behavior rules
- `PROJECT_BRAIN.md`: durable project memory and guardrails
- `IMPLEMENT_PLAN.md`: active roadmap and next milestones
- `DOC_RECOVERY.md`: integrity hashes and recovery steps for the canonical docs

Novel-specific folders may keep compatibility stubs, reports, artifacts, and runtime files. Do not put durable cross-novel planning content inside a single-novel folder.

## Architecture

Pipeline:

```text
source adapter
  -> source validation
  -> block splitting
  -> glossary scan
  -> glossary approval
  -> literal translation
  -> refinement
  -> QA
  -> formatting
  -> chapter assembly
  -> reports
  -> MoonRead import
```

Important paths:

- `D:\Fogust\Workspace\Novel\00_Config\novel_registry.json`: shared multi-novel registry plus per-novel reader/title/quality policy
- `D:\Fogust\Workspace\Novel\Deep Sea Embers\novel_pipeline\`: Python package and CLI
- `D:\Fogust\Workspace\Novel\Deep Sea Embers\.system\`: config, providers, style profiles
- `D:\Fogust\Workspace\Novel\Deep Sea Embers\01_Glossary\`: glossary notes
- `D:\Fogust\Workspace\Novel\Deep Sea Embers\03_Raw\`: fetched source cache
- `D:\Fogust\Workspace\Novel\Deep Sea Embers\04_Work\`: block and batch artifacts
- `D:\Fogust\Workspace\Novel\Deep Sea Embers\05_Output\`: final translated Markdown
- `D:\Fogust\Workspace\Novel\Deep Sea Embers\06_Logs\run_ledger.jsonl`: append-only ledger
- `D:\Fogust\Workspace\Novel\Deep Sea Embers\07_Reports\`: reports and evidence
- `D:\Fogust\Workspace\Novel\MoonRead\`: workspace-level MoonRead reader app
- `D:\Fogust\Workspace\Novel\Deep Sea Embers\reader-web\`: compatibility stub for older MoonRead commands only

Ledger rule: historical failed records remain. Current status must be inferred from latest valid state, not raw failed-record counts.

Layering rule:

- Multi-novel layer: generic policies that should apply to every novel live in `00_Config\novel_registry.json` and shared scripts. Examples: MoonRead import range/source root, final Markdown validation, generic title fallback detection, truncation thresholds, and provider/meta/encoding leakage checks.
- Novel layer: story-specific policy lives in each novel entry and its vault notes. Examples: DSE Chinese title sidecar requirement, HGD English-title normalization, Seth pronoun policy, required source beats, and known forbidden variants.
- If a bug pattern can recur across novels, fix it in the multi-novel layer first, then add only the narrow story-specific details to the novel layer.
- Reader blurb rule: after a novel has at least 60 translated/published chapters, its glossary and style evidence are considered sufficient to translate/adapt the official synopsis, description, or teaser for MoonRead. Store the adapted Thai blurb plus `synopsis_source_url` and `synopsis_source_note` in `00_Config\novel_registry.json`.

Sentinel layer policy:

- Level 0, multi-novel Sentinel: checks every novel with rules that are always product-safe. Add rules here only when they do not depend on a specific story voice or glossary choice. Examples: provider/meta leakage, bad encoding/mojibake, Han leakage in Thai body text, quote-only lines, missing generated MoonRead files, obvious truncation, approved-glossary English original leakage, and source-vs-output approved glossary coverage.
- Level 1, novel Sentinel: checks one novel using that novel's policy, glossary, aliases, pronouns, title rules, known false positives, and source-site quirks. Examples: HGD Seth pronoun policy, HGD `Kaelen`/`Kyle` near-miss variants, HGD English title normalization, DSE named Chinese chapter-title sidecars.
- Rule promotion policy: start a recurring user-reported defect at Level 1 if it depends on one novel's vocabulary or voice. Promote to Level 0 only after the same defect class is proven novel-agnostic and has low false-positive risk.
- Rule addition policy: every new Sentinel rule must record scope, severity, evidence path, false-positive risk, and repair action. If a rule can lower translation quality by over-constraining style, keep it advisory until measured.

## Current Verified State

Deep Sea Embers:

- latest full retranslation run: `deep-sea-embers-retranslate-ch001-ch050-v2`
- `ch001-ch050` translated and repaired under `05_Output/`
- latest product review evidence: `Deep Sea Embers/07_Reports/product_review_deep-sea-embers-retranslate-ch001-ch050-v2_20260616.md`; degraded only because preflight sees the documented untracked queue
- no current failed blocks are known
- final-output checks have covered missing output, Han Chinese body text, provider/meta leakage, quote-only lines, known user-reported variants, paragraph density, and HGD required source beat
- notable approved terms include `实太阳神` -> `สุริยเทพที่แท้จริง` and `面具神` -> `เทพหน้ากาก`
- DSE title fallback incident closed for MoonRead `ch052-ch080`: source titles existed in Chinese, but no `04_Work/ch052-ch080/title.json` sidecars had been created, so final assembly silently fell back to generic `บทที่ N` headings. Prevention: final assembly now refuses named Chinese source titles without a translated title sidecar, and `scripts/check_output_quality_guardrails.py` rejects generic DSE headings when the source title has a real named Chinese title.
- `dse-ch081-ch120-v1` completed: Deep Sea Embers `ch081-ch120` translated/refined/QA-passed/formatted/assembled, no current failed blocks remain, output guardrails passed, and MoonRead now publishes DSE through `ch120`. `ch110-block-004` needed a final format-stage ledger repair because a valid formatted artifact existed but the latest ledger record was a stale formatting failure. `ch120` displays `บทที่ 121` because the source file `ch120/source.json` itself is titled `第121章 救援`.
- `dse-ch121-ch150-v1` completed: Deep Sea Embers `ch121-ch150` translated/refined/QA-passed/formatted/assembled, no current failed blocks remain, output guardrails passed, duplicate title paragraphs were removed, and MoonRead now publishes DSE through `ch150`.
- `dse-ch151-ch160-v1` completed: Deep Sea Embers `ch151-ch160` translated/refined/QA-passed/formatted/assembled, no current failed blocks remain, output guardrails passed, Sentinel blocker/major/minor/info `0/0/0/0`, and MoonRead now publishes DSE through `ch160`.

Horror Game Developer:

- MoonRead published scope is `ch001-ch250`, with HGD local ids now matching source chapter numbers
- active continuation goal: HGD `ch201-ch220` translation and MoonRead publication is complete; keep future work as new bounded goals
- `hgd-ch101-ch110-v1` completed: all 10 blocks translated/refined/QA-passed/formatted/assembled, outputs exist, output guardrails passed, and no current failed blocks remain. This range is not yet published to MoonRead.
- `hgd-ch111-ch120-v1` completed: all 10 blocks translated/refined/QA-passed/formatted/assembled, outputs exist, output guardrails passed, and no current failed blocks remain. This range is not yet published to MoonRead. QA omission hard-fails in this range confirmed the root cause: refinement can still drop poems, thoughts, or sound-effect/source-beat blocks after ordinary retries.
- `hgd-ch121-ch130-v1` completed: all 10 blocks translated/refined/QA-passed/formatted/assembled, outputs exist, output guardrails passed, and no current failed blocks remain. This range is not yet published to MoonRead. `ch126` exposed a pipeline smoothness bug: QA retry wrote a newer refined artifact, but formatting could still use an older in-memory refined draft; prevention now reloads the latest refined artifact after QA before formatting.
- `hgd-ch131-ch140-v1` completed: all 10 blocks translated/refined/QA-passed/formatted/assembled, outputs exist, output guardrails passed, and no current failed blocks remain. This range is not yet published to MoonRead. `ch136` needed a bounded pronoun repair from `เรา` to `ผม` in Seth internal monologue, then QA passed with `--no-auto-refine`.
- `hgd-ch141-ch150-v1` completed: all 10 blocks translated/refined/QA-passed/formatted/assembled, outputs exist, output guardrails passed, and no current failed blocks remain. This range is not yet published to MoonRead. Repairs during the run exposed recurring smoothness issues: glossary conflict (`Team Leader Soran` needed `หัวหน้ากลุ่มโซแรน`), Seth pronoun drift (`เรา`/`ฉัน` -> `ผม` only in Seth POV), quest-term confusion (`Chain Quest Activated` vs `Continuation Quest Activated`), rank mistranslation (`ระดับ A` where source meant a ranked gate), and stale formatted artifact after local recovery on `ch146`.
- `hgd-ch151-ch160-v1` completed: all 10 blocks translated/refined/QA-passed/formatted/assembled, outputs exist, output guardrails passed, and no current failed blocks remain. This range is not yet published to MoonRead. QA routing was corrected before completion: normal QA now uses `openrouter_reasoning` with `deepseek/deepseek-v4-flash`; `deepseek/deepseek-v4-pro` is no longer in the normal HGD QA fallback path, and new QA ledger records include model metadata.
- `hgd-ch161-ch170-v1` completed: all 10 blocks translated/refined/QA-passed/formatted/assembled, outputs exist, output guardrails passed, and no current failed blocks remain. This range is not yet published to MoonRead. QA audit used only `deepseek/deepseek-v4-flash` via `openrouter_reasoning` or `qwen deepseek-reasoner` fallback; no V4 Pro QA route was used.
- `hgd-ch171-ch180-v1` completed: all 10 blocks translated/refined/QA-passed/formatted/assembled, outputs exist, output guardrails passed, and no current failed blocks remain. This range is not yet published to MoonRead. `ch176` needed bounded recovery for Seth pronoun drift plus missing Dreamwalker/Mirelle tail content; QA passed after repair. QA audit used only `deepseek/deepseek-v4-flash` via `openrouter_reasoning` or `qwen deepseek-reasoner` fallback; no V4 Pro QA route was used.
- `hgd-ch181-ch190-v1` completed: all 10 blocks translated/refined/QA-passed/formatted/assembled, outputs exist, output guardrails passed, and no current failed blocks remain. This range is not yet published to MoonRead. Historical failed records came from Codex quota when QA fallback reached emergency fallback on `ch182`/`ch186`; bounded QA reruns recovered both. QA audit used only `deepseek/deepseek-v4-flash` via `openrouter_reasoning` or `qwen deepseek-reasoner` for completed QA records; no V4 Pro QA route was used.
- `hgd-ch191-ch200-v1` completed: all 10 blocks translated/refined/QA-passed/formatted/assembled, outputs exist, output guardrails passed, and no current failed blocks remain. This range is not yet published to MoonRead. `Shepherd Decree`/`Decree Shepherd` mojibake was repaired during the glossary gate, and title mappings were added through `ch200`. QA audit used only `deepseek/deepseek-v4-flash` via `openrouter_reasoning` or `qwen deepseek-reasoner` for completed QA records; no V4 Pro QA route was used.
- `hgd-ch201-ch220-v1` completed: all 20 blocks translated/refined/QA-passed/formatted/assembled, outputs exist, output guardrails passed, and no current failed blocks remain. `ch206` and `ch211` used manual QA force-accept after deterministic repair, which exposed a status bug: `qa force_accepted` was not treated as terminal QA success for pending-stage calculation. Prevention: `ResumeState.next_pending_stage()` now treats `qa force_accepted` and `qa skipped` as QA-done states.
- HGD `ch201-ch220` post-publication quality incident closed: user found Seth voice drift in `ch203` (`กู`) and English/glossary leakage in `ch206`. Cause: Sentinel was available as a post-run/report gate but was not yet a mandatory blocking pipeline/publish stage for this historical published range, and the deterministic forbidden-output list did not include these exact variants. Repair: `ch203`, `ch206`, and related Sentinel findings in `ch202`, `ch208`, `ch210`, `ch211`, `ch212`, `ch214`, `ch216`, `ch217`, `ch218`, and `ch219` were corrected in final output/MoonRead. Prevention: HGD output guardrail now rejects `กู`, common English parenthetical leftovers, approved glossary leakage such as `A Twisted Game`, and observed Thai encoding corruption patterns; Sentinel glossary coverage now uses longest-match overlap handling so terms like `Conductor Quest` do not falsely require both the long system term and its shorter subterm. Latest strict report: `07_Reports/sentinel_quality_hgd-ch201-ch220-final-clean_20260622_233211.md` with blocker/major/minor/info `0/0/0/0`.
- HGD source titles are English; Thai reader titles are protected by HGD title normalization and title sidecars
- HGD source-sequence incident closed: local ids were migrated to source chapter numbers, missing source chapters `29`, `30`, `54`, `55`, `91`, and `221` were inserted/translated, `ch172` now correctly points to source `Chapter 172` after the full renumbering, and MoonRead publishes HGD through `ch236`. Prevention: run `Deep Sea Embers/scripts/check_source_chapter_sequence.py` after HGD fetch/repair/publish work.
- `04_Work/ch001/title.json` through `ch080/title.json` exist to prevent single-block reruns from falling back to English titles
- HGD project folder is now `D:\Fogust\Workspace\Novel\Horror Game Developers`; it has the user-created Obsidian vault and durable pronoun policy at `Horror Game Developers/02_Database_Views/HGD Pronoun Policy.md`
- V6.17 title/format incident is closed for published scope: `ch022-block-001` dropped the source beat "Like that, four days passed."; it was restored as `*และแล้ว สี่วันก็ผ่านไป*`
- V6.17.1 found and repaired narrow English leakage in HGD output: `Horror Developer System`, `Developer Seth Thorne`, `Jump Scare`, `Scenario`, `Section Chief`, selected sound effects in `ch022`, and `Seth's USB stick`
- HGD `ch149` terminology leakage incident closed: user found `ทวิสเต็ดแมน`, `อโนมาลี`, and English parentheticals such as `(Twisted Man)` / `(Anomaly)` in published output even though earlier chapters had used natural Thai. Cause: `The Anomaly.md` approved a transliteration, `Squad Leader.md` had mojibake, and the HGD forbidden-output guardrail did not yet include these variants. Prevention: glossary notes now use `ความผิดปกติ` and `หัวหน้ากลุ่ม`, HGD output/MoonRead generated chapters were repaired for the repeated leakage set, `HGD_FORBIDDEN_ENGLISH_OUTPUT` rejects the known variants, and `test_translation.py` covers the regression. Repair report: `Horror Game Developers/07_Reports/hgd_english_leakage_repair_20260621.md`
- Full translated-output audit after the HGD `ch149` report closed additional hard failures across the current published scope: leaked category labels such as `(character)`, `(entity)`, `(rank)`, `(system)`, `(term)`, DSE English explanatory leftovers `(Anomaly)` / `(Vision)`, and broken UI Markdown in HGD `ch208`/`ch219`. Prevention: output guardrails now reject leaked metadata labels and broken UI bracket wrappers. Audit report: `07_Reports/full_translated_output_quality_audit_20260621.md`
- Glossary policy clarified after the HGD leakage audit: approved glossary entries are not soft bilingual display. Final output and MoonRead must use the approved `thai_term`; approved English originals/aliases must not remain as parentheticals or UI labels unless a future explicit glossary field allows bilingual display. Prevention: HGD approved-glossary leakage guardrail now scans final output and MoonRead generated chapters, and regression tests cover English alias leakage plus unusable `thai_term` placeholders.
- V6.25 Sentinel Quality Gate initial slice completed: `scripts/sentinel_quality_report.py` now produces JSON/Markdown blocker/major/minor reports, reuses existing guardrails, enforces approved glossary leakage across registered novels, and records advisory English-token findings for feedback review. First strict run exposed 35 HGD approved-glossary blockers; deterministic repair removed them from final output/formatted artifacts, MoonRead was regenerated/deployed, and optimized Sentinel now reports blocker/major/minor/info `0/0/80/0` for current published scope. Latest report: `07_Reports/sentinel_quality_current-published-optimized_20260621_165359.md`
- Sentinel is now a blocking production pipeline stage for DSE and HGD via `execution.sentinel.mode: blocking` and `fail_on: major`. After a chapter output is assembled, the pipeline runs scoped Sentinel for that chapter, writes a `sentinel` ledger record, and blocks the run on blocker/major findings. Runtime Sentinel skips advisory English-token review so only product-safety failures stop translation. Do not wire Sentinel as an unscoped MoonRead postgenerate hook until historical backlog outside the touched range is intentionally cleaned.
- HGD Decree/Conductor terminology drift closed for published output: user found `ประกาศิต` / `โองการ` / `บัญญัติ` and `คอนดักเตอร์` / `ผู้บงการ` / `วาทยกร` drift around `ch208-ch210`. Cause: older glossary notes disagreed (`Temporal Decree` and `Mender Decree` used `โองการ...` while most Decree terms used `ประกาศิต...`), and old output used both `วาทยากร` misspelling and `คอนดักเตอร์` for the entity. Repair: final/MoonRead product text now uses `ประกาศิต` for Decree-family terms, `วาทยกร` for The Conductor entity, keeps `เควสต์คอนดักเตอร์` only for `Conductor Quest`, and leaves `ผู้บงการ` only for `The Orchestrator`. Prevention: HGD guardrail now rejects `โองการ`, `บัญญัติ`, `วาทยากร`, and standalone `คอนดักเตอร์`; regression test covers the allowed `เควสต์คอนดักเตอร์` exception.
- HGD Squad/Team Leader title drift closed for published output: user found `หัวหน้ากลุ่ม` and `หัวหน้าหน่วย` used for the same `Squad Leader` / `Team Leader` role. Canonical is `หัวหน้ากลุ่ม` for the HGD gate-team role, including `Team Leader Soran` -> `หัวหน้ากลุ่มโซแรน`. Repair: final output, formatting artifacts, and MoonRead generated chapters were normalized from `หัวหน้าหน่วย` to `หัวหน้ากลุ่ม`. Prevention: `Squad Leader.md` documents `หัวหน้าหน่วย` as a rejected older variant, and HGD guardrail/regression now rejects `หัวหน้าหน่วย`.
- HGD `ch223` role confusion closed: source has `Section Chief` and `Guild Master`, but output drifted to `หัวหน้ากลุ่ม` and `ท่านเจ้าสำนัก`, making the `หัวหน้าแผนก` disappear. Repair: `ch223` final/artifact/MoonRead text now uses `หัวหน้าแผนก` for `Section Chief`, `หัวหน้ากิลด์` for `Guild Master`, and `หัวหน้ากลุ่มโซแรน` for `Team Leader Soran`. Prevention: HGD guardrail/regression now rejects `เจ้าสำนัก` and `โซรัน`; Sentinel glossary coverage should be run on touched chapters after role/name repairs.
- HGD `ch224` placeholder corruption closed: source uses `Guild Master`, but final/MoonRead output contained repeated `?????????????` placeholders where the title should appear. Repair: `ch224` final/artifact/MoonRead text now uses `หัวหน้ากิลด์`. Prevention: HGD guardrail/regression now rejects repeated question-mark placeholders (`?????`) in output.
- HGD `ch164` Kaelen/Kyle name drift closed: source has distinct characters `Kaelen` and `Kyle`, and the approved glossary says `Kaelen Jacobs` -> `เคเลน เจคอบส์`, but output used `ไคลน์`, which was visually too close to `ไคล์` and confused speakers. Repair: changed `ไคลน์` to `เคเลน` in ch164 final/formatted/refined product path and regenerated MoonRead. Prevention: HGD output guardrail now rejects `ไคลน์`, and `test_translation.py` covers the regression.
- Libra - Glossary Bot coverage added to Sentinel after the HGD `ch164` name drift: Sentinel now compares approved glossary originals/aliases found in `03_Raw/chXXX/source.json` against final output and MoonRead, so missing approved Thai terms are caught even when no known wrong variant is listed yet. Character full-name entries may pass with the approved Thai first name in prose, but wrong near-miss variants such as `ไคลน์` remain blockers. The first scoped run also caught `Sarah` -> `ซาร่า` and `Kaelen` -> `เคลเลน`/`คาเลน` drift across `ch164-ch166`; repair changed them to approved `ซาราห์` and `เคเลน`. Prevention: run Sentinel coverage for touched ranges after major translation/repair/publish work, and keep provider glossary context scoped by Libra rather than passing the entire growing glossary blindly.
- HGD pronoun incident closed for published scope: Seth-dominant chapters had drifted between `ผม` and `ฉัน`, and Kyle/Seth peer address drifted between `นาย`, `คุณ`, and `เธอ`. Cause: HGD had no durable pronoun policy, and prompts/profile/QA did not pin Seth's Thai voice. Prevention: HGD Obsidian policy note, HGD research/style/prompt/QA pronoun rules, and `scripts/check_output_quality_guardrails.py` Seth-pronoun checks for known high-risk published chapters. Repair report: `Deep Sea Embers/07_Reports/hgd_pronoun_consistency_repair_20260616.md`
- prevention: `scripts/check_output_quality_guardrails.py` checks the HGD `ch022` required source beat, known HGD English leakage terms, and HGD Seth pronoun drift; `test_translation.py` covers the `ch022` and HGD pronoun regressions
- HGD title/truncation incident closed for MoonRead `ch001-ch080`: `ch036-ch080` lacked title sidecars and new title mappings, while `ch002`, `ch060`, and `ch072` had truncation risks from earlier recovery paths. Prevention: HGD title sidecars through `ch080`, `Horror Game Developers/scripts/normalize_hgd_titles.py`, source-vs-output truncation guardrail, and MoonRead title fallback checks. Repair report: `Horror Game Developers/07_Reports/hgd_title_truncation_repair_20260617.md`
- HGD formatting audit closed for MoonRead `ch001-ch200`: `ch177` exposed a broader layout problem where refinement/formatting collapsed dialogue, thoughts, UI text, and action beats into dense paragraphs. Prevention: QA now strips common Markdown wrappers before detecting fail lines, `scripts/check_output_quality_guardrails.py` checks HGD paragraph density beyond `ch001-ch035` while respecting `--chapters`, catches malformed Markdown residue in both HGD output and MoonRead generated chapters, and truncation checks normalize runaway repeated characters before length comparison. Repairs: validated layout projection was applied to safe chapters, `ch047` was retranslated/repaired after runaway scream text masked truncation, and `ch072` was rerun through literal-safe QA recovery after a truncated refined artifact. Follow-up repair also removed marker residue such as `]**`, `***`, `:*`, and lone `*` lines from affected HGD chapters after `ch177` review.
- HGD `ch081-ch090` completed under run `hgd-ch081-ch090-v1`; ch089 required deterministic recovery because QA retry repeatedly re-refined away source beats. Prevention for this batch: title normalizer covers `ch036-ch090`, and the recovery metadata records why ch089 used literal-safe manual QA acceptance before AI formatting.
- HGD `ch091-ch100` completed under run `hgd-ch091-ch100-v1` and published to MoonRead. V6.23 smoothness fixes were exercised in production: batch glossary approval worked, HGD title gate stopped missing title mappings before publishing English titles, and QA repair-safe mode recovered ch091/ch093/ch095/ch097 without retry refinement overwriting repairs. Checkpoint: `Horror Game Developers/07_Reports/hgd_ch091_ch100_checkpoint.md`.
- `hgd-ch237-ch250-v2` completed and published to MoonRead. `hgd-ch237-ch250-v1` was abandoned because HGD fetch resolved local `ch237` by manifest ordinal and fetched source Chapter 253; prevention now prefers `metadata.site_chapter` in fetch resolution and `check_source_chapter_sequence.py` fails when local id and source chapter number differ. During v2, bounded repairs fixed Seth pronoun drift, hallucinated ranks, Team Leader/Squad Leader title drift, and approved-glossary English leakage. Output guardrails and Sentinel final report pass with blocker/major/minor/info `0/0/0/0`.

MoonRead:

- current reader library includes Deep Sea Embers `ch001-ch160` and Horror Game Developer `ch001-ch250`
- both current novels now pass the 60-chapter reader blurb gate; MoonRead registry includes source-backed Thai synopsis text for both books
- canonical MoonRead app path is `D:\Fogust\Workspace\Novel\MoonRead`; it is no longer owned by the Deep Sea Embers folder
- MoonRead imports novels from `00_Config\novel_registry.json`; adding a future novel should start by adding a registry entry, not by hardcoding paths in `MoonRead\scripts\generate-chapters.mjs`
- MoonRead reads verified Markdown only
- MoonRead must not call providers, edit glossary/source/artifacts, or modify ledger
- latest relevant checks: `generate:chapters`, `lint`, `build`, and `smoke` passed after V6.19.1 UX/UI polish and cover art integration
- V6.19 handoff report: `Deep Sea Embers/07_Reports/v6_19_moonread_ux_handoff_20260616.md`
- V6.19.1 completed: Thai UI labels, active nav, SiteFooter, synopsis line-clamp, localStorage key migration, cover art for both novels, conditional logo-cover class
- V6.20 completed: nav simplified to single "หน้าแรก" link (removed DSE-only "Deep Sea Embers" and "สารบัญ" links); footer DSE-only link removed; nav overlap fix (`min-width: 0`); homepage card spacing via `.library-grid`; mobile nav grid adapts to any link count
- V6.20.1 completed: hero banner (CSS background-image, hidden on mobile), Open Graph / Twitter Card metadata with `metadataBase`, custom 404 page with illustration, apple-touch-icon; placeholder 1×1 PNGs in place — user replaces with actual processed images
- V6.20.1 handoff report: `Deep Sea Embers/07_Reports/v6_20_1_ux_images_handoff_20260617.md`
- cover art source: `00_Assets/cover_art/20260616/` (Codex-generated, painterly style, no baked-in text)

V6.18 speed work:

- current config keeps runtime speed changes disabled:
  - `execution.concurrency_enabled: false`
  - `execution.artifact_cache.mode: report_only`
  - `execution.pre_qa_guardrail.mode: report_only`
- read-only reports exist for run planning, cache benchmark, concurrency benchmark, benchmark approval, and current gate status
- current gate report: `Deep Sea Embers/07_Reports/v6_18_current_gate_status_20260616.md`
- benchmark command packet: `Deep Sea Embers/07_Reports/v6_18_benchmark_command_packet_20260616.md`
- minimal formatting parallelism design: `Deep Sea Embers/07_Reports/v6_18_minimal_formatting_parallel_design_20260616.md`
- latest completion gate recheck: `Deep Sea Embers/07_Reports/v6_18_completion_gate_recheck_20260616.md`
- guarded runtime slice: `Deep Sea Embers/07_Reports/v6_18_formatting_parallel_runtime_slice_20260616.md`
- implementation status: `_resume_chapter()` can now format consecutive QA-ready blocks with limited parallelism when `execution.concurrency_enabled` is explicitly true; default config remains disabled
- actual benchmark complete: `Deep Sea Embers/07_Reports/v6_18_ch051_actual_formatting_parallel_benchmark_20260616.md`
- benchmark target: `ch051`, fetched/prepared after `ch050` for the approved V6.18 gate
- result: 5 QA-ready blocks formatted by `openrouter` with `parallel_limit: 2`; wall-clock `143.167s` versus same-run sequential-duration estimate `253.188s`, about `43.5%` reduction
- `ch051` output exists and passed cleanliness/output guardrails, but this does not approve a new production batch
- do not enable global concurrency/cache/Pre-QA blocking silently; formatting-only concurrency remains the only proven runtime slice

Working tree:

- Git repo root: `D:\Fogust\Workspace\Novel`
- GitHub: `https://github.com/Tusgof/Novel`
- branch: `main`
- commit identity: `Tusgof <124960571+Tusgof@users.noreply.github.com>`
- latest pushed commit before V6.23 pipeline smoothness work: `3b4808f`
- latest readiness reports: `Deep Sea Embers/07_Reports/preflight_report_20260616_after_v6_18_gate.md`, `Deep Sea Embers/07_Reports/recovery_drill_20260616_after_v6_18_gate.md`, and `Deep Sea Embers/07_Reports/preflight_recovery_readiness_note_20260616.md`
- remaining visible untracked queue is intentional: 46 glossary notes and 14 intermediate/probe reports. The 5 durable provider/glossary evidence reports were committed at `0d3187d`. Classification report: `Deep Sea Embers/07_Reports/v6_13_untracked_queue_classification_20260616.md`. Glossary queue review: `Deep Sea Embers/07_Reports/v6_13_glossary_queue_review_20260616.md`. Alias overlap proposal: `Deep Sea Embers/07_Reports/v6_13_glossary_alias_overlap_proposal_20260616.md`. Glossary cleanup execution proposal: `Deep Sea Embers/07_Reports/v6_13_glossary_queue_cleanup_execution_proposal_20260616.md`. Report queue review: `Deep Sea Embers/07_Reports/v6_13_report_queue_review_20260616.md`. Report cleanup proposal: `Deep Sea Embers/07_Reports/v6_13_report_queue_cleanup_proposal_20260616.md`. Do not delete, hide, or commit the remaining queue without a dedicated decision.

## Provider Routing

Current intended routing:

- setup/fetch authority: Codex / GPT-5.4 via Ferryman
- glossary scan: OpenRouter `google/gemini-3-flash-preview`
- glossary option suggestion: OpenRouter `deepseek/deepseek-v4-flash`
- literal translation: OpenRouter `google/gemini-3-flash-preview`
- refinement: OpenRouter `deepseek/deepseek-v4-flash`
- QA primary: OpenRouter `deepseek/deepseek-v4-flash` with reasoning enabled
- QA fallback: Qwen `deepseek-reasoner`, then Codex emergency fallback. Do not use OpenRouter `deepseek/deepseek-v4-pro` in normal HGD QA routing unless a future benchmark explicitly re-approves it.
- formatting primary: OpenRouter `deepseek/deepseek-v4-flash`
- formatting fallback/cleanup: local deterministic formatter

Provider warning: the cost-priority QA route did not fully clear the original benchmark gate. Inspect QA artifacts closely on the next bounded production run.

Do not use Elephant or Nemotron for state-changing work.

## Guardrails

Never:

- rewrite or delete ledger history
- silently force-accept QA hard-fails
- commit provider quota/error/meta output as successful content
- trust a worker report without checking files and tests
- commit API keys or bearer tokens
- let MoonRead mutate translation artifacts

Always:

- use UTF-8 for reads/writes
- keep runs bounded by explicit chapter/block ranges
- stop on manual QA prompt, provider failure, command length failure, validation failure, or unexpected scope expansion
- validate final outputs for provider/meta text, unintended Chinese body text, wrong glossary variants, quote-only lines, paragraph density, and formatting drift
- after any major run or MoonRead publication, run the major-run spot-check checklist before claiming done
- preserve exact source meaning over style polish
- record recurring quality issues and prevention mechanisms here or in `IMPLEMENT_PLAN.md`

Major-run spot-check checklist:

- Applies to multi-chapter translation batches, broad repair passes, and MoonRead publication updates.
- Sample at least 5 chapters: first, last, one early-middle, one late-middle, and one chapter with known recovery/provider incident if any.
- For each sample, inspect H1 title, first paragraphs, one middle section, ending, paragraph density, dialogue/thought formatting, glossary/name consistency, and obvious omission/truncation.
- Run deterministic guardrails for the touched chapter range, then run MoonRead `generate:chapters`, `lint`, `build`, and `smoke` if reader content changed.
- If a sampled issue is systematic, repair the full affected range, add or extend a deterministic guardrail, regenerate MoonRead if needed, and record the cause/prevention in the relevant report.
- A worker or provider QA report does not satisfy this checklist by itself; Codex must verify disk output and reader behavior.

Requires explicit user approval:

- starting a new production translation batch
- force-accepting a QA hard-fail
- changing production provider routing
- manually modifying final outputs/source artifacts
- enabling runtime concurrency, cache skipping, or Pre-QA blocking
- running the V6.18 benchmark
- deleting untracked reports, glossary notes, backups, or artifacts

## Known Risks

| Risk | Prevention |
| --- | --- |
| Ledger confusion from historical failures | use latest-state status/inspect commands |
| Provider crash, timeout, quota, malformed output | bounded run, fallback chain, stop and report if unsafe |
| QA false pass | add deterministic guardrails after confirmed misses; inspect risky QA artifacts |
| Pronoun/name/title drift | add deterministic known-variant checks after user reports |
| DSE generic title fallback | final assembly requires `title.json` for named Chinese source titles; output guardrail rejects `บทที่ N` when source has a real title |
| Same bug recurring in another novel | promote the generic part into `00_Config\novel_registry.json` and shared guardrail code, then keep only story-specific details in the novel layer |
| HGD Seth pronoun drift | keep HGD Obsidian pronoun policy, prompt/profile rules, and published-scope guardrail checks aligned |
| New novel setup without vault | create/open the novel Obsidian vault first, then add profile/glossary/source/output folders inside it |
| Dense or broken formatting | AI formatting plus deterministic validation; use `C:\Users\ASUS\Downloads\good format.md` as style reference |
| HGD English title fallback | keep HGD title normalization and title sidecars through the published range |
| HGD English/glossary leakage in final output | keep approved glossary notes natural Thai, reject known leakage variants with output guardrails, and add regression tests whenever a user reports a repeated term leak |
| HGD final output truncation after force-accept/retry | compare output length against source and reject dangling endings before MoonRead publication |
| HGD local chapter id diverging from source chapter number | run `python "Deep Sea Embers\scripts\check_source_chapter_sequence.py" --novel-dir "Horror Game Developers" --chapters chXXX-chYYY` after fetch/repair/publish; decide separately whether to migrate HGD display/routing to source chapter numbers |
| Pipeline requires too much manual artifact repair | create a per-batch control packet, use repair-safe QA commands, make next safe action explicit before resume, use the QA omission literal-safe recovery path before escalating to manual prompt, and format only the latest refined artifact after QA retry |
| MoonRead rendering mismatch | run reader smoke after generated content changes |
| Worker false completion | verify disk state, tests, reports, and git diff |
| Memory doc damage | keep docs short, use `DOC_RECOVERY.md`, avoid worker rewrites of canonical files |

## Core Commands

Run from repo root:

```powershell
cd "D:\Fogust\Workspace\Novel\Deep Sea Embers"
$env:PYTHONIOENCODING='utf-8'
```

Validate pipeline:

```powershell
python -m compileall novel_pipeline
python test_translation.py
novel-pipeline --config ".system/config.yaml" preflight
python scripts\check_output_quality_guardrails.py
```

Open dashboard:

```powershell
novel-pipeline --config ".system/config.yaml" operator --open-browser
```

Read run status:

```powershell
novel-pipeline --config ".system/config.yaml" status --run-id <run-id>
```

Plan a bounded run:

```powershell
novel-pipeline --config ".system/config.yaml" report run-plan --run-id <run-id>
```

Run a scan-only gate:

```powershell
novel-pipeline --config ".system/config.yaml" run --range chXXX-chYYY --run-id <run-id> --stop-after glossary-scan
```

Resume bounded work:

```powershell
novel-pipeline --config ".system/config.yaml" resume --run-id <run-id> --until-chapter chXXX --manual-action-mode stop
```

Inspect/recover one block:

```powershell
novel-pipeline --config ".system/config.yaml" inspect-block --run-id <run-id> --block-id <block-id>
novel-pipeline --config ".system/config.yaml" rerun-block --run-id <run-id> --block-id <block-id> --from-stage <stage>
```

MoonRead:

```powershell
cd "D:\Fogust\Workspace\Novel\MoonRead"
npm.cmd run generate:chapters
npm.cmd run lint
npm.cmd run build
npm.cmd run smoke
```

## Next Safe Action

HGD translation has local verified output through `ch220`; MoonRead is published through `ch220`. Deep Sea Embers is published through `ch150`.

Next safe choices:

1. Commit the `dse-ch121-ch150-v1` / `hgd-ch201-ch220-v1` checkpoint and MoonRead publication update.
2. Treat future HGD continuation or quality work as a new bounded goal.
3. If deploying externally, redeploy the pushed MoonRead update from the hosting provider.
4. Stop again on manual QA prompt, provider failure, command length failure, validation failure, or unexpected scope expansion.
