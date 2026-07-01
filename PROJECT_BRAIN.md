# Project Brain: Novel Translation System

Last updated: 2026-07-01

This is the durable memory for the workspace. Keep it compact. Put long evidence, experiments, and historical detail in root-level `07_Reports/` or `01_Research_Log/` as appropriate.

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
- `ARCHITECTURE.md`: system structure, boundaries, flows, and ownership
- `DOC_RECOVERY.md`: integrity hashes and recovery steps for the canonical docs

Novel-specific folders may keep compatibility stubs, reports, artifacts, and runtime files. Do not put durable cross-novel planning content inside a single-novel folder.

## Architecture

System structure, source-of-truth ownership, layer rules, pipeline flow, actor map, provider routing, guardrail stack, recovery model, and new-novel setup flow live in `ARCHITECTURE.md`.

Keep this section short. Update `PROJECT_BRAIN.md` for current state, active risks, current routing summary, active guardrails, and next safe action only.

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
- 2026-06-30 user review for DSE `ch140-ch160`: repaired `审判官` Thai drift in final output/MoonRead (`อินควิสิเตอร์`/`ผู้พิพากษา` -> `ตุลาการ`) and removed the unnecessary `(Prominence)` parenthetical. Added scoped output guardrail coverage for this repaired range. Remaining minor review queue: `DND` appears only inside a source author-note promo in `ch152`, not story body.
- V6.33 DSE continuation completed and published: `ch161-ch180` translated/refined/QA-passed/formatted/assembled, outputs exist, Sentinel final report `07_Reports/sentinel_quality_dse-v6-33-ch161-ch180-final_20260630_005304.md` reports blocker/major/minor/info `0/0/0/0`, and MoonRead now publishes DSE through `ch180`.
- Libra - Pilot Gate DSE completed on 2026-06-29 in isolated experiment vault `Deep Sea Embers/04_Work/_experiments/libra_pilot_dse_v1`. Raw sampling used fetched `03_Raw/ch001-ch160` with seed `632160`; in-sample `dse-libra-pilot-insample-v1` completed 54/54 blocks and OOS `dse-libra-pilot-oos-v1` completed 56/56 blocks. Current failed blocks: none. Output guardrails passed and Sentinel blocker/major/minor/info was `0/0/0/0`. Report: `Deep Sea Embers/07_Reports/libra_pilot_gate_dse_completion_20260629.md`.

Horror Game Developer:

- MoonRead published scope is `ch001-ch270`, with HGD local ids now matching source chapter numbers
- active continuation goal: none; HGD translation and MoonRead publication are complete through `ch270`. Keep future work as new bounded goals
- V6.33 HGD continuation completed and published: `ch251-ch270` translated/refined/QA-passed/formatted/assembled, outputs exist, Sentinel final report `07_Reports/sentinel_quality_hgd-v6-33-ch251-ch270-final_20260629_200006.md` reports blocker/major/minor/info `0/0/0/0`, and MoonRead now publishes HGD through `ch270`.
- `hgd-ch101-ch110-v1` completed: all 10 blocks translated/refined/QA-passed/formatted/assembled, outputs exist, output guardrails passed, and no current failed blocks remain. This range is published to MoonRead.
- `hgd-ch111-ch120-v1` completed: all 10 blocks translated/refined/QA-passed/formatted/assembled, outputs exist, output guardrails passed, and no current failed blocks remain. This range is published to MoonRead. QA omission hard-fails in this range confirmed the root cause: refinement can still drop poems, thoughts, or sound-effect/source-beat blocks after ordinary retries.
- `hgd-ch121-ch130-v1` completed: all 10 blocks translated/refined/QA-passed/formatted/assembled, outputs exist, output guardrails passed, and no current failed blocks remain. This range is published to MoonRead. `ch126` exposed a pipeline smoothness bug: QA retry wrote a newer refined artifact, but formatting could still use an older in-memory refined draft; prevention now reloads the latest refined artifact after QA before formatting.
- `hgd-ch131-ch140-v1` completed: all 10 blocks translated/refined/QA-passed/formatted/assembled, outputs exist, output guardrails passed, and no current failed blocks remain. This range is published to MoonRead. `ch136` needed a bounded pronoun repair from `เรา` to `ผม` in Seth internal monologue, then QA passed with `--no-auto-refine`.
- `hgd-ch141-ch150-v1` completed: all 10 blocks translated/refined/QA-passed/formatted/assembled, outputs exist, output guardrails passed, and no current failed blocks remain. This range is published to MoonRead. Repairs during the run exposed recurring smoothness issues: glossary conflict (`Team Leader Soran` needed `หัวหน้ากลุ่มโซแรน`), Seth pronoun drift (`เรา`/`ฉัน` -> `ผม` only in Seth POV), quest-term confusion (`Chain Quest Activated` vs `Continuation Quest Activated`), rank mistranslation (`ระดับ A` where source meant a ranked gate), and stale formatted artifact after local recovery on `ch146`.
- `hgd-ch151-ch160-v1` completed: all 10 blocks translated/refined/QA-passed/formatted/assembled, outputs exist, output guardrails passed, and no current failed blocks remain. This range is published to MoonRead. QA routing was corrected before completion: normal QA now uses `openrouter_reasoning` with `deepseek/deepseek-v4-flash`; `deepseek/deepseek-v4-pro` is no longer in the normal HGD QA fallback path, and new QA ledger records include model metadata.
- `hgd-ch161-ch170-v1` completed: all 10 blocks translated/refined/QA-passed/formatted/assembled, outputs exist, output guardrails passed, and no current failed blocks remain. This range is published to MoonRead. QA audit used only `deepseek/deepseek-v4-flash` via `openrouter_reasoning` or `qwen deepseek-reasoner` fallback; no V4 Pro QA route was used.
- `hgd-ch171-ch180-v1` completed: all 10 blocks translated/refined/QA-passed/formatted/assembled, outputs exist, output guardrails passed, and no current failed blocks remain. This range is published to MoonRead. `ch176` needed bounded recovery for Seth pronoun drift plus missing Dreamwalker/Mirelle tail content; QA passed after repair. QA audit used only `deepseek/deepseek-v4-flash` via `openrouter_reasoning` or `qwen deepseek-reasoner` fallback; no V4 Pro QA route was used.
- `hgd-ch181-ch190-v1` completed: all 10 blocks translated/refined/QA-passed/formatted/assembled, outputs exist, output guardrails passed, and no current failed blocks remain. This range is published to MoonRead. Historical failed records came from Codex quota when QA fallback reached emergency fallback on `ch182`/`ch186`; bounded QA reruns recovered both. QA audit used only `deepseek/deepseek-v4-flash` via `openrouter_reasoning` or `qwen deepseek-reasoner` for completed QA records; no V4 Pro QA route was used.
- `hgd-ch191-ch200-v1` completed: all 10 blocks translated/refined/QA-passed/formatted/assembled, outputs exist, output guardrails passed, and no current failed blocks remain. This range is published to MoonRead. `Shepherd Decree`/`Decree Shepherd` mojibake was repaired during the glossary gate, and title mappings were added through `ch200`. QA audit used only `deepseek/deepseek-v4-flash` via `openrouter_reasoning` or `qwen deepseek-reasoner` for completed QA records; no V4 Pro QA route was used.
- `hgd-ch201-ch220-v1` completed: all 20 blocks translated/refined/QA-passed/formatted/assembled, outputs exist, output guardrails passed, and no current failed blocks remain. `ch206` and `ch211` used manual QA force-accept after deterministic repair, which exposed a status bug: `qa force_accepted` was not treated as terminal QA success for pending-stage calculation. Prevention: `ResumeState.next_pending_stage()` now treats `qa force_accepted` and `qa skipped` as QA-done states.
- HGD `ch201-ch220` post-publication quality incident closed: user found Seth voice drift in `ch203` (`กู`) and English/glossary leakage in `ch206`. Cause: Sentinel was available as a post-run/report gate but was not yet a mandatory blocking pipeline/publish stage for this historical published range, and the deterministic forbidden-output list did not include these exact variants. Repair: `ch203`, `ch206`, and related Sentinel findings in `ch202`, `ch208`, `ch210`, `ch211`, `ch212`, `ch214`, `ch216`, `ch217`, `ch218`, and `ch219` were corrected in final output/MoonRead. Prevention: HGD output guardrail now rejects `กู`, common English parenthetical leftovers, approved glossary leakage such as `A Twisted Game`, and observed Thai encoding corruption patterns; Sentinel glossary coverage now uses longest-match overlap handling so terms like `Conductor Quest` do not falsely require both the long system term and its shorter subterm. Latest strict report: `07_Reports/sentinel_quality_hgd-ch201-ch220-final-clean_20260622_233211.md` with blocker/major/minor/info `0/0/0/0`.
- HGD source titles are English; Thai reader titles are protected by HGD title normalization and title sidecars
- HGD source-sequence incident closed: local ids were migrated to source chapter numbers, missing source chapters `29`, `30`, `54`, `55`, `91`, and `221` were inserted/translated, `ch172` now correctly points to source `Chapter 172` after the full renumbering, and MoonRead publishes HGD through `ch250`. Prevention: run `Deep Sea Embers/scripts/check_source_chapter_sequence.py` after HGD fetch/repair/publish work.
- `04_Work/ch001/title.json` through `ch080/title.json` exist to prevent single-block reruns from falling back to English titles
- HGD project folder is now `D:\Fogust\Workspace\Novel\Horror Game Developers`; it has the user-created Obsidian vault and durable pronoun policy at `Horror Game Developers/02_Database_Views/HGD Pronoun Policy.md`
- V6.17 title/format incident is closed for published scope: `ch022-block-001` dropped the source beat "Like that, four days passed."; it was restored as `*และแล้ว สี่วันก็ผ่านไป*`
- V6.17.1 found and repaired narrow English leakage in HGD output: `Horror Developer System`, `Developer Seth Thorne`, `Jump Scare`, `Scenario`, `Section Chief`, selected sound effects in `ch022`, and `Seth's USB stick`
- HGD `ch149` terminology leakage incident closed: user found `ทวิสเต็ดแมน`, `อโนมาลี`, and English parentheticals such as `(Twisted Man)` / `(Anomaly)` in published output even though earlier chapters had used natural Thai. Cause: `The Anomaly.md` approved a transliteration, `Squad Leader.md` had mojibake, and the HGD forbidden-output guardrail did not yet include these variants. Prevention: glossary notes now use `ความผิดปกติ` and `หัวหน้ากลุ่ม`, HGD output/MoonRead generated chapters were repaired for the repeated leakage set, `HGD_FORBIDDEN_ENGLISH_OUTPUT` rejects the known variants, and `test_translation.py` covers the regression. Repair report: `Horror Game Developers/07_Reports/hgd_english_leakage_repair_20260621.md`
- Full translated-output audit after the HGD `ch149` report closed additional hard failures across the current published scope: leaked category labels such as `(character)`, `(entity)`, `(rank)`, `(system)`, `(term)`, DSE English explanatory leftovers `(Anomaly)` / `(Vision)`, and broken UI Markdown in HGD `ch208`/`ch219`. Prevention: output guardrails now reject leaked metadata labels and broken UI bracket wrappers. Audit report: `07_Reports/full_translated_output_quality_audit_20260621.md`
- Glossary policy clarified after the HGD leakage audit: approved glossary entries are not soft bilingual display. Final output and MoonRead must use the approved `thai_term`; approved English originals/aliases must not remain as parentheticals or UI labels unless a future explicit glossary field allows bilingual display. Prevention: HGD approved-glossary leakage guardrail now scans final output and MoonRead generated chapters, and regression tests cover English alias leakage plus unusable `thai_term` placeholders.
- V6.25 Sentinel Quality Gate initial slice completed: `scripts/sentinel_quality_report.py` now produces JSON/Markdown blocker/major/minor reports, reuses existing guardrails, enforces approved glossary leakage across registered novels, and records advisory English-token findings for feedback review. First strict run exposed 35 HGD approved-glossary blockers; deterministic repair removed them from final output/formatted artifacts, MoonRead was regenerated/deployed, and optimized Sentinel now reports blocker/major/minor/info `0/0/80/0` for current published scope. Latest report: `07_Reports/sentinel_quality_current-published-optimized_20260621_165359.md`
- Sentinel is now a blocking production pipeline stage for DSE and HGD via `execution.sentinel.mode: blocking` and `fail_on: major`. After a chapter output is assembled, the pipeline runs scoped Sentinel for that chapter, writes a `sentinel` ledger record, and blocks the run on blocker/major findings. Runtime Sentinel skips advisory English-token review so only product-safety failures stop translation. Do not wire Sentinel as an unscoped MoonRead postgenerate hook until historical backlog outside the touched range is intentionally cleaned.
- Sentinel also blocks glossary/category note leakage such as `คำ: ชื่อตัวละคร`, `คำ: สิ่งมีชีวิต/ศัตรู`, `คำ: ฉายา/ตำแหน่ง`, and `คำ: คำเรียก...` after IRS ch020 exposed a leaked glossary tail in final output.
- HGD Decree/Conductor terminology drift closed for published output: user found `ประกาศิต` / `โองการ` / `บัญญัติ` and `คอนดักเตอร์` / `ผู้บงการ` / `วาทยกร` drift around `ch208-ch210`. Cause: older glossary notes disagreed (`Temporal Decree` and `Mender Decree` used `โองการ...` while most Decree terms used `ประกาศิต...`), and old output used both `วาทยากร` misspelling and `คอนดักเตอร์` for the entity. Repair: final/MoonRead product text now uses `ประกาศิต` for Decree-family terms, `วาทยกร` for The Conductor entity, keeps `เควสต์คอนดักเตอร์` only for `Conductor Quest`, and leaves `ผู้บงการ` only for `The Orchestrator`. Prevention: HGD guardrail now rejects `โองการ`, `บัญญัติ`, `วาทยากร`, and standalone `คอนดักเตอร์`; regression test covers the allowed `เควสต์คอนดักเตอร์` exception.
- HGD Squad/Team Leader title drift closed for published output: user found `หัวหน้ากลุ่ม` and `หัวหน้าหน่วย` used for the same `Squad Leader` / `Team Leader` role. Canonical is `หัวหน้ากลุ่ม` for the HGD gate-team role, including `Team Leader Soran` -> `หัวหน้ากลุ่มโซแรน`. Repair: final output, formatting artifacts, and MoonRead generated chapters were normalized from `หัวหน้าหน่วย` to `หัวหน้ากลุ่ม`. Prevention: `Squad Leader.md` documents `หัวหน้าหน่วย` as a rejected older variant, and HGD guardrail/regression now rejects `หัวหน้าหน่วย`.
- HGD `ch223` role confusion closed: source has `Section Chief` and `Guild Master`, but output drifted to `หัวหน้ากลุ่ม` and `ท่านเจ้าสำนัก`, making the `หัวหน้าแผนก` disappear. Repair: `ch223` final/artifact/MoonRead text now uses `หัวหน้าแผนก` for `Section Chief`, `หัวหน้ากิลด์` for `Guild Master`, and `หัวหน้ากลุ่มโซแรน` for `Team Leader Soran`. Prevention: HGD guardrail/regression now rejects `เจ้าสำนัก` and `โซรัน`; Sentinel glossary coverage should be run on touched chapters after role/name repairs.
- HGD `ch224` placeholder corruption closed: source uses `Guild Master`, but final/MoonRead output contained repeated `?????????????` placeholders where the title should appear. Repair: `ch224` final/artifact/MoonRead text now uses `หัวหน้ากิลด์`. Prevention: HGD guardrail/regression now rejects repeated question-mark placeholders (`?????`) in output.
- HGD post-ch224 scoped cleanup closed for touched publish surface: deterministic checks found old published leftovers in `ch091`, `ch222`, `ch235`, and `ch236` after the ch224 repair. Repair: removed `(Twisted Man)` / `(Anomaly)` leakage in `ch091`, normalized `โซรัน` -> `โซแรน`, `ซาร่า` -> `ซาราห์`, `มาสเตอร์กิลด์` -> `หัวหน้ากิลด์`, and `(Fragments)` -> Thai-only `เศษเสี้ยว`. Prevention: MoonRead generator now rejects known fatal HGD product terms, `run-sentinel-gate.mjs` refuses accidental full-workspace scans unless explicitly allowed, and scoped `publish:verify` passed for `ch091,ch222,ch224,ch235,ch236` with blocker/major/minor/info `0/0/0/0`.
- HGD `ch164` Kaelen/Kyle name drift closed: source has distinct characters `Kaelen` and `Kyle`, and the approved glossary says `Kaelen Jacobs` -> `เคเลน เจคอบส์`, but output used `ไคลน์`, which was visually too close to `ไคล์` and confused speakers. Repair: changed `ไคลน์` to `เคเลน` in ch164 final/formatted/refined product path and regenerated MoonRead. Prevention: HGD output guardrail now rejects `ไคลน์`, and `test_translation.py` covers the regression.
- Libra - Glossary Bot coverage added to Sentinel after the HGD `ch164` name drift: Sentinel now compares approved glossary originals/aliases found in `03_Raw/chXXX/source.json` against final output and MoonRead, so missing approved Thai terms are caught even when no known wrong variant is listed yet. Character full-name entries may pass with the approved Thai first name in prose, but wrong near-miss variants such as `ไคลน์` remain blockers. The first scoped run also caught `Sarah` -> `ซาร่า` and `Kaelen` -> `เคลเลน`/`คาเลน` drift across `ch164-ch166`; repair changed them to approved `ซาราห์` and `เคเลน`. Prevention: run Sentinel coverage for touched ranges after major translation/repair/publish work, and keep provider glossary context scoped by Libra rather than passing the entire growing glossary blindly.
- HGD pronoun incident closed for published scope: Seth-dominant chapters had drifted between `ผม` and `ฉัน`, and Kyle/Seth peer address drifted between `นาย`, `คุณ`, and `เธอ`. Cause: HGD had no durable pronoun policy, and prompts/profile/QA did not pin Seth's Thai voice. Prevention: HGD Obsidian policy note, HGD research/style/prompt/QA pronoun rules, and `scripts/check_output_quality_guardrails.py` Seth-pronoun checks for known high-risk published chapters. Repair report: `Deep Sea Embers/07_Reports/hgd_pronoun_consistency_repair_20260616.md`
- prevention: `scripts/check_output_quality_guardrails.py` checks the HGD `ch022` required source beat, known HGD English leakage terms, and HGD Seth pronoun drift; `test_translation.py` covers the `ch022` and HGD pronoun regressions
- HGD title/truncation incident closed for MoonRead `ch001-ch080`: `ch036-ch080` lacked title sidecars and new title mappings, while `ch002`, `ch060`, and `ch072` had truncation risks from earlier recovery paths. Prevention: HGD title sidecars through `ch080`, `Horror Game Developers/scripts/normalize_hgd_titles.py`, source-vs-output truncation guardrail, and MoonRead title fallback checks. Repair report: `Horror Game Developers/07_Reports/hgd_title_truncation_repair_20260617.md`
- HGD formatting audit closed for MoonRead `ch001-ch200`: `ch177` exposed a broader layout problem where refinement/formatting collapsed dialogue, thoughts, UI text, and action beats into dense paragraphs. Prevention: QA now strips common Markdown wrappers before detecting fail lines, `scripts/check_output_quality_guardrails.py` checks HGD paragraph density beyond `ch001-ch035` while respecting `--chapters`, catches malformed Markdown residue in both HGD output and MoonRead generated chapters, and truncation checks normalize runaway repeated characters before length comparison. Repairs: validated layout projection was applied to safe chapters, `ch047` was retranslated/repaired after runaway scream text masked truncation, and `ch072` was rerun through literal-safe QA recovery after a truncated refined artifact. Follow-up repair also removed marker residue such as `]**`, `***`, `:*`, and lone `*` lines from affected HGD chapters after `ch177` review.
- HGD `ch081-ch090` completed under run `hgd-ch081-ch090-v1`; ch089 required deterministic recovery because QA retry repeatedly re-refined away source beats. Prevention for this batch: title normalizer covers `ch036-ch090`, and the recovery metadata records why ch089 used literal-safe manual QA acceptance before AI formatting.
- HGD `ch091-ch100` completed under run `hgd-ch091-ch100-v1` and published to MoonRead. V6.23 smoothness fixes were exercised in production: batch glossary approval worked, HGD title gate stopped missing title mappings before publishing English titles, and QA repair-safe mode recovered ch091/ch093/ch095/ch097 without retry refinement overwriting repairs. Checkpoint: `Horror Game Developers/07_Reports/hgd_ch091_ch100_checkpoint.md`.
- `hgd-ch237-ch250-v2` completed and published to MoonRead. `hgd-ch237-ch250-v1` was abandoned because HGD fetch resolved local `ch237` by manifest ordinal and fetched source Chapter 253; prevention now prefers `metadata.site_chapter` in fetch resolution and `check_source_chapter_sequence.py` fails when local id and source chapter number differ. During v2, bounded repairs fixed Seth pronoun drift, hallucinated ranks, Team Leader/Squad Leader title drift, and approved-glossary English leakage. Output guardrails and Sentinel final report pass with blocker/major/minor/info `0/0/0/0`.
- Libra - Pilot Gate HGD completed on 2026-06-29 in isolated experiment vault `Horror Game Developers/04_Work/_experiments/libra_pilot_hgd_v1`. Raw sampling used fetched `03_Raw/ch001-ch250` with seed `632250`; in-sample `hgd-libra-pilot-insample-v1` completed 10/10 chapters; out-of-sample used two 5-chapter glossary batches and completed 10/10 chapters. Current failed blocks: none. Output guardrails passed and aggregate Sentinel blocker/major/minor/info was `0/0/0/0`. Report: `Horror Game Developers/07_Reports/libra_pilot_gate_hgd_completion_20260629.md`.

Infinite Regressor Stories:

- new novel vault created at `D:\Fogust\Workspace\Novel\Infinite Regressor Stories`
- profile/config created for `infinite-regressor-stories`; source language for pipeline input is English from WeTried TLS, target is Thai
- new `wetriedtls` adapter extracts chapter bodies from escaped Next.js `self.__next_f` payloads
- source fetch completed for `ch001-ch394`: `394/394` raw `source.json` files exist and validation found `0` issues
- `ch395+` is not currently fetch-ready from WeTried TLS: checked pages return metadata/shell without body payload or server error
- registry entry exists with `reader.enabled: true`; MoonRead publishes IRS clean `ch001-ch050`.
- V6.32 IRS setup experiment completed for IRS on 2026-06-29. In-sample run `irs-v6-32-insample-treatment-v3` completed `34/34` blocks; out-of-sample run `irs-v6-32-oos-v1` completed `32/32` blocks. Current failed blocks: none. Scoped deterministic output audit passed for all 20 sampled chapters. Completion report: `Infinite Regressor Stories/07_Reports/v6_32_irs_experiment_completion_20260629.md`
- V6.33 IRS clean production retranslation completed and published for `ch001-ch050` using 5-chapter glossary batches. All 10 clean batch run IDs report current failed blocks: none and manual actions needed: none. Final outputs exist for all 50 chapters. Blocking Sentinel report `07_Reports/sentinel_quality_irs-clean-ch001-ch050-final-after-leakage-rule_20260630_101639.md` reports `0/0/0/0`; advisory report `07_Reports/sentinel_quality_irs-clean-ch001-ch050-final-advisory-review-after-leakage-rule_20260630_101829.md` reports `0/0/80/0` suspicious-English minor review items. Completion report: `Infinite Regressor Stories/07_Reports/irs_clean_retranslate_ch001_ch050_completion_20260630.md`. MoonRead publish Sentinel report `07_Reports/sentinel_quality_moonread-irs-ch001-ch050-publish_20260630_172648.md` reports `0/0/0/0`.
- IRS Thai numeral drift closed for published `ch001-ch050`: `ch004` and `ch006` contained Thai digits from AI refinement/formatting. Final output, current work artifacts, and MoonRead generated chapters were normalized to Arabic digits. Cause: providers can stylistically rewrite Arabic numerals into Thai numerals, and old archive/experiment artifacts still preserve pre-normalized drafts. Prevention: IRS registry quality policy now rejects `[๐-๙]`; output guardrails/test coverage verify the rule for both `05_Output` and MoonRead generated content; scoped IRS guardrails now honor `--novel infinite-regressor-stories` so unrelated HGD backlog cannot mask IRS-only verification.
- 2026-07-01 Thai numeral follow-up reconfirmed current IRS product state: IRS `05_Output/ch001-ch050` and MoonRead generated IRS chapters contain no Thai numerals, scoped Sentinel reports `0/0/0/0`, and Thai numerals remain only in old `_archive` artifacts from the pre-repair run. The same audit found DSE duplicate title tails in `ch167`, `ch169`, `ch174`, `ch175`, `ch176`, `ch177`, and `ch178`; `ch175` also had Thai numerals. The tails were removed from refined/formatted/final output, MoonRead was regenerated, the output guardrail now rejects Thai numerals across registered novels instead of IRS only, and duplicate-title detection now catches title-like body tails anywhere after H1. Reports: `07_Reports/irs_thai_numeral_audit_20260701.md`, `07_Reports/thai_numeral_leakage_repair_20260701.md`.
- current IRS production recommendation: safe for the next bounded sequential IRS production pilot, but not approved for long unmonitored parallel production. Reasoning-enabled OpenRouter QA returned empty assistant messages on long QA prompts; isolated IRS experiment routing used non-reasoning `deepseek/deepseek-v4-flash` QA with Gemini Flash fallback.
- setup/fetch evidence: `Infinite Regressor Stories/07_Reports/setup_fetch_20260624.md`

Cross-novel experiment state:

- V6.34 Cross-Novel Libra - Blind Pilot Gate is active. Purpose: re-test the pipeline across DSE, HGD, and IRS using raw-source sampling that is not hand-picked from previously translated/problem chapters.
- Verified local raw source pools as of 2026-07-01: DSE `ch001-ch180` (`180`, no gaps), HGD `ch001-ch270` (`270`, no gaps), IRS `ch001-ch394` (`394`, no gaps).
- First V6.34 sample seed: `634001`; design is 10 strata per novel, 1 in-sample and 1 out-of-sample chapter per stratum, total 60 chapters across 3 novels.
- V6.34A sampling-only round is recorded at `01_Research_Log/2026-06-30_novel_pipeline_libra_blind_pilot_source_pool.md`; no provider calls or production translation were started during this round.
- V6.34B read-only baseline is recorded at `01_Research_Log/2026-06-30_novel_pipeline_libra_blind_pilot_baseline_v6_34b.md`; risk data lives in `07_Reports/v6_34b_cross_novel_baseline_risk_table_20260630_203000.json` and `.md`. Result: all 60 raw-source chapters exist; IRS is the highest-risk stress target due to long/very-long chapters, bracket/system density, repeated-character risk, embedded CJK/Hangul risk, and high glossary density.
- V6.34C IRS in-sample scan-only gate completed in isolated experiment vault `Infinite Regressor Stories/04_Work/_experiments/v6_34c_irs_insample_v1`: run `v6-34c-irs-insample-v1` scanned `ch009,ch076,ch086,ch157,ch183,ch201,ch252,ch300,ch338,ch381`, produced 175 glossary candidate items, wrote only `fetched`/`glossary_scanned` ledger records, created no final outputs, and has no current failed blocks. Research log: `01_Research_Log/2026-06-30_novel_pipeline_libra_blind_pilot_v6_34c_irs_scan.md`.
- V6.34C IRS glossary classification completed without approval writes: 62 approve-new candidates, 19 alias-to-existing candidates, 41 reject/noise candidates, and 53 ask-human/source-aware candidates. Translation remains paused until source-aware review and experiment-local `glossary_approved` records exist. Report: `07_Reports/v6_34c_irs_glossary_classification_20260701.md`; research log: `01_Research_Log/2026-06-30_novel_pipeline_libra_blind_pilot_v6_34c_irs_glossary_classification.md`.
- V6.34C IRS experiment-local glossary approval completed: 73 notes created in the isolated experiment vault, 7 alias updates made there, 10 `glossary_approved` records appended for `v6-34c-irs-insample-v1`, no production glossary/output/MoonRead files changed, and translation/refinement/QA/formatting records remain `0`. Report: `07_Reports/v6_34c_irs_glossary_approval_decisions_20260701.md`; research log: `01_Research_Log/2026-06-30_novel_pipeline_libra_blind_pilot_v6_34c_irs_glossary_approval.md`.
- V6.34 Milestone 1 charter lock completed: `IMPLEMENT_PLAN.md` was rewritten around a measured cross-novel research loop, the old plan was archived at `Backup_IMPLEMENT_PLAN/01072026_IMPLEMENT_PLAN.md`, and the charter research log is `01_Research_Log/2026-06-30_novel_pipeline_v6_34_charter.md`. Current V6.34 next step is Milestone 2 source-pool and sampling gate, not production translation.
- V6.34 Milestone 2 source-pool/sampling gate completed: DSE `ch001-ch180`, HGD `ch001-ch270`, and IRS `ch001-ch394` raw pools have no gaps, missing `source.json`, or unreadable `source.json` within verified boundaries. Seed `634001` produced a 60-chapter cross-novel manifest: 20 chapters per novel, split into 10 in-sample and 10 out-of-sample chapters. Report: `07_Reports/v6_34_m2_source_pool_and_sample_manifest_20260701.md`; research log: `01_Research_Log/2026-06-30_novel_pipeline_v6_34_source_pool_sampling.md`.
- V6.34 Milestone 3 scan/glossary gate completed for the 30 in-sample chapters in isolated experiment vaults: DSE `v6-34-m3-dse-baseline-v1`, HGD `v6-34-m3-hgd-baseline-v1`, and IRS `v6-34-m3-irs-baseline-v1` each have 10 `fetched`, 10 `glossary_scanned`, and 10 `glossary_approved` records, with translation/refinement/QA/formatting records still `0`. Baseline policy holds all newly scanned candidates to avoid tuning before measurement. Decision report: `07_Reports/v6_34_m3_baseline_glossary_gate_decisions_20260701.md`; research log: `01_Research_Log/2026-06-30_novel_pipeline_v6_34_m3_scan_glossary_gate.md`.
- V6.34 Milestone 3 baseline translation stopped at a valid gate: HGD `v6-34-m3-hgd-baseline-v1` completed `ch024` and `ch037` blocks, then Sentinel found true experiment-output major glossary coverage failures on `ch037` (`Velora Art Museum` / `Art Museum` missing approved Thai term). A separate instrumentation bug was fixed so experiment Sentinel uses local registry/workspace overrides instead of production output/MoonRead. Research log: `01_Research_Log/2026-06-30_novel_pipeline_v6_34_m3_hgd_baseline_stop.md`. Next step is Milestone 4 defect analysis; do not repair `ch037` as a one-off before classification.
- V6.34 Milestone 4 initial analysis completed for HGD `ch037`: the miss is caused by title sidecar text `พิพิธภัณฑ์ศิลปะเวลอรา` conflicting with approved glossary `พิพิธภัณฑ์ศิลปะเวโลรา`; body QA passed because the defect is in final H1/title surface. Report: `07_Reports/v6_34_m4_initial_defect_analysis_hgd_ch037_20260701.md`; research log: `01_Research_Log/2026-06-30_novel_pipeline_v6_34_m4_initial_analysis.md`.
- V6.34 Milestone 4 treatment selected and initial slice implemented: final assembly now blocks title/H1 glossary drift when a source title contains an approved glossary original term or alias, and HGD `Velora Art Museum` now maps to approved `พิพิธภัณฑ์ศิลปะเวโลรา`. Report: `07_Reports/v6_34_m4_treatment_selection_title_glossary_20260701.md`; research log: `01_Research_Log/2026-07-01_novel_pipeline_v6_34_m4_treatment_selection.md`. Next step is Milestone 5 treatment rerun in isolated experiment state.
- V6.34 Milestone 5 treatment rerun started and safely stopped: HGD treatment vault `v6_34_m5_hgd_treatment_v1` reached `ch024`, then Sentinel blocked approved glossary English parenthetical leakage (`The Nightwalker`, `Nightwalker`, `Field Agent`). `The missing piece -> ชิ้นส่วนที่หายไป` was added to HGD title normalization after the treatment run exposed that map gap. Report: `07_Reports/v6_34_m5_hgd_treatment_early_stop_20260701.md`; research log: `01_Research_Log/2026-07-01_novel_pipeline_v6_34_m5_hgd_treatment_early_stop.md`.
- V6.34 Milestone 5 checkpoint passed through HGD `ch037`: deterministic approved-glossary parenthetical cleanup removed safe `thai_term (source/alias)` leakage, `ch024` now passes scoped Sentinel `0/0/0/0`, and `ch037` now uses `# ตอนที่ 37 - พิพิธภัณฑ์ศิลปะเวโลรา [2]` with scoped Sentinel `0/0/0/0`. Report: `07_Reports/v6_34_m5_hgd_treatment_checkpoint_ch024_ch037_20260701.md`; research log: `01_Research_Log/2026-07-01_novel_pipeline_v6_34_m5_hgd_treatment_checkpoint.md`.
- V6.34 Milestone 5 checkpoint passed through HGD `ch132`: treatment progressed through `ch066`, `ch103`, then hit `ch132` Sentinel `3/2/0/0`. Cause was mixed Layer 0/Layer 2: UTF-8 BOM-prefixed glossary notes were skipped by `parse_glossary_note()`, and HGD loose variants for Sarah/department names were not recorded as rejected variants. Parser now tolerates BOM, HGD notes record the variants, `Kaelen.md` body matches approved `เคเลน`, and `ch132` now passes Sentinel `0/0/0/0`. Report: `07_Reports/v6_34_m5_hgd_treatment_ch132_bom_glossary_repair_20260701.md`; research log: `01_Research_Log/2026-07-01_novel_pipeline_v6_34_m5_hgd_ch132_bom_glossary_repair.md`.
- V6.34 Milestone 5 HGD treatment slice completed: isolated run `v6-34-m5-hgd-treatment-v1` completed all 10 HGD in-sample chapters with current failed blocks none and latest scoped Sentinel `0/0/0/0` for every chapter. `ch250` exposed source redaction hallucination (`-ranked Gate` -> `ระดับ S`); prevention now repairs redacted ranked-gate markers to `เกตไม่ระบุแรงก์` only when source lacks an explicit S-rank. Report: `07_Reports/v6_34_m5_hgd_treatment_completion_20260701.md`; research log: `01_Research_Log/2026-07-01_novel_pipeline_v6_34_m5_hgd_treatment_completion.md`.
- V6.34 Milestone 5 HGD baseline-vs-treatment comparison completed: baseline stopped after `ch037` with Sentinel `0/2/0/0`; treatment completed all 10 HGD in-sample chapters with latest scoped Sentinel `0/0/0/0` for every chapter. Treatment improved measured product-surface defects enough to continue DSE/IRS treatment measurement, but historical failures, QA hard-fails, and five QA omission recovery events mean long-run smoothness is not proven yet. Report: `07_Reports/v6_34_m5_hgd_baseline_vs_treatment_comparison_20260701.md`; research log: `01_Research_Log/2026-07-01_novel_pipeline_v6_34_m5_hgd_baseline_vs_treatment_comparison.md`.
- V6.34 Milestone 5 DSE treatment attempt stopped before valid measurement: copied experiment vault `v6_34_m5_dse_treatment_v1` contained stale/off-by-one raw source for all 10 sampled chapters when compared with current DSE production `03_Raw`. `ch017` translated from stale raw and final assembly stopped on title glossary mismatch before output publication. New read-only guard `scripts/verify_experiment_source_parity.py` must pass before treatment/OOS provider calls. Report: `07_Reports/v6_34_m5_dse_treatment_source_mismatch_stop_20260701.md`; research log: `01_Research_Log/2026-07-01_novel_pipeline_v6_34_m5_dse_source_mismatch_stop.md`.

MoonRead:

- current reader library includes published Deep Sea Embers `ch001-ch180`, Horror Game Developer `ch001-ch270`, and Infinite Regressor Stories `ch001-ch050`
- both current novels now pass the 60-chapter reader blurb gate; MoonRead registry includes source-backed Thai synopsis text for both books
- canonical MoonRead app path is `D:\Fogust\Workspace\Novel\MoonRead`; it is no longer owned by the Deep Sea Embers folder
- MoonRead imports novels from `00_Config\novel_registry.json`; adding a future novel should start by adding a registry entry, not by hardcoding paths in `MoonRead\scripts\generate-chapters.mjs`
- MoonRead reads verified Markdown only
- MoonRead must not call providers, edit glossary/source/artifacts, or modify ledger
- latest relevant checks: `generate:chapters` produced 3 books / 500 available chapters / 0 missing / 0 rejected; scoped Sentinel publish reports passed for DSE `ch161-ch180`, HGD `ch251-ch270`, and IRS `ch001-ch050`; MoonRead `lint`, `build`, and `smoke` passed.
- MoonRead `publish:verify` is the scoped publish gate for generated chapters and reader validation
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
- latest pushed commit is current git HEAD: `f816bd0`
- latest readiness reports: `Deep Sea Embers/07_Reports/preflight_report_20260616_after_v6_18_gate.md`, `Deep Sea Embers/07_Reports/recovery_drill_20260616_after_v6_18_gate.md`, and `Deep Sea Embers/07_Reports/preflight_recovery_readiness_note_20260616.md`
- no current untracked queue is present; verify with `git status --short --untracked-files=all` before treating any future queue text as current state.

## Provider Routing

Current intended routing:

- setup/fetch authority: Codex / GPT-5.4 via Ferryman
- glossary scan: OpenRouter `google/gemini-3-flash-preview`
- glossary option suggestion: OpenRouter `deepseek/deepseek-v4-flash`
- literal translation: OpenRouter `google/gemini-3-flash-preview`
- refinement: OpenRouter `deepseek/deepseek-v4-flash`
- QA primary: OpenRouter `deepseek/deepseek-v4-flash` with reasoning enabled
- QA fallback: OpenRouter reasoning `deepseek/deepseek-v4-pro` only. Qwen and Codex are not automatic QA fallbacks because recent IRS evidence showed qwen headless empty stdout on Windows and Codex quota failures.
- formatting primary: OpenRouter `deepseek/deepseek-v4-flash`
- formatting fallback/cleanup: local deterministic formatter
- OpenRouter API key env var: `NOVEL_OPENROUTER_API`; do not use the legacy OpenRouter env var name for current work.

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
| New novel pipeline not tuned before scaling | before sampling, fetch the intended source scope into `03_Raw/`; if the site is partially unavailable, record the verified fetchable scope first. Then run **Libra - Pilot Gate**: randomly sample 20 chapters from that fetched scope with a recorded seed, use 10 in-sample chapters to tune, use 10 out-of-sample chapters to measure generalization, then classify fixes by multi-novel/language/novel/run layer before long production batches |
| Cross-novel experiments overfit to familiar translated ranges | sample from verified `03_Raw/` source pools with a fixed seed and stratified coverage; keep translated chapters only if the raw-source sample selects them naturally; record every experiment round in `01_Research_Log/` |
| Provider formatting can leave duplicate title paragraphs or dense thought/prose paragraphs | final assembly now removes an immediate title-like first body paragraph below the H1 and applies conservative long-paragraph reflow after AI formatting; keep output guardrails active for duplicate title and paragraph density |
| Long pilot or production runs are too slow under serial translate/refine/QA | keep current work bounded; treat translation/refinement/QA parallelism as a dedicated milestone with ledger safety and provider isolation instead of enabling broad concurrency casually |
| HGD Seth pronoun drift | keep HGD Obsidian pronoun policy, prompt/profile rules, and published-scope guardrail checks aligned |
| New novel setup without vault | create/open the novel Obsidian vault first, then add profile/glossary/source/output folders inside it |
| Dense or broken formatting | AI formatting plus deterministic validation; use `C:\Users\ASUS\Downloads\good format.md` as style reference |
| HGD English title fallback | keep HGD title normalization and title sidecars through the published range |
| HGD English/glossary leakage in final output | keep approved glossary notes natural Thai, reject known leakage variants with output guardrails, and add regression tests whenever a user reports a repeated term leak |
| HGD final output truncation after force-accept/retry | compare output length against source and reject dangling endings before MoonRead publication |
| HGD local chapter id diverging from source chapter number | run `python "Deep Sea Embers\scripts\check_source_chapter_sequence.py" --novel-dir "Horror Game Developers" --chapters chXXX-chYYY` after fetch/repair/publish; decide separately whether to migrate HGD display/routing to source chapter numbers |
| Pipeline requires too much manual artifact repair | create a per-batch control packet, use repair-safe QA commands, make next safe action explicit before resume, use the QA omission literal-safe recovery path before escalating to manual prompt, and format only the latest refined artifact after QA retry |
| MoonRead generator contains HGD-specific title/term policy in code | keep changes surgical for now; move policy into registry/shared quality config in a dedicated refactor |
| Full unscoped Sentinel scan is slow | use scoped Sentinel gates for publication and only run full scans intentionally with explicit range/all confirmation |
| Full unscoped output guardrail hits historical HGD backlog | run output guardrails against the touched chapter range before publication; clean broad historical backlog as a dedicated quality pass |
| Codex provider config is tied to the Deep Sea Embers cwd/read-only sandbox | use explicit novel paths for setup/fetch work until provider config is generalized for multi-novel routing |
| Infinite Regressor Stories `ch395+` unavailable from WeTried TLS | keep fetched source scope at `ch001-ch394` until the source page exposes body payload; do not create placeholder source chapters |
| IRS long-run reliability is not stable enough for unmonitored parallel production | use bounded sequential IRS production pilots; keep reasoning-enabled OpenRouter QA disabled for long QA prompts until a later probe proves it no longer returns empty assistant messages; promote long repeated-character detection before scaling |
| Thai numeral drift and duplicate title tails | product output should use Arabic digits across registered novels; global output guardrail rejects Thai numerals in final output and MoonRead generated chapters, including legacy reader paths. Duplicate-title guardrail rejects `บทที่/ตอนที่ N ...` body tails after H1. Old archive/experiment artifacts may still contain historical Thai numerals and are not product surface |
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
python scripts\check_output_quality_guardrails.py --chapters chXXX-chYYY
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
npm.cmd run publish:verify
npm.cmd run lint
npm.cmd run build
npm.cmd run smoke
```

## Next Safe Action

Current reader state: Deep Sea Embers is published through `ch180`; Horror Game Developer is published through `ch270`; Infinite Regressor Stories is published through clean `ch050`. Libra - Pilot Gate is complete for IRS, DSE, and HGD as per V6.32/V6.33, but V6.34 is now active to run a stricter cross-novel blind pilot from verified raw source pools.

V6.33 translation-output and reader-publication phase is complete:

- HGD: `ch251-ch270` output complete, publish Sentinel `0/0/0/0`, MoonRead through `ch270`.
- DSE: `ch161-ch180` output complete, publish Sentinel `0/0/0/0`, MoonRead through `ch180`.
- IRS: clean `ch001-ch050` output complete, publish Sentinel `0/0/0/0`, MoonRead through `ch050`; advisory English review queue remains minor-only.
- All three used glossary batches of 5 chapters.

Next safe choices:

1. Rebuild DSE V6.34 Milestone 5 treatment vault from current production `03_Raw` and title sidecars, not from stale copied experiment raw.
2. Run `scripts/verify_experiment_source_parity.py` for DSE sampled chapters and require zero mismatches before any provider call.
3. Restart DSE treatment measurement from `ch017` only after source parity passes.
3. Keep all experiment output isolated from production `05_Output`, production glossary intent, production ledger intent, and MoonRead until a separate production gate approves changes.
4. Record each completed experiment round in `01_Research_Log/` and push it immediately.
5. Stop on provider failure, manual QA prompt, command length failure, validation failure, source extraction failure, source mismatch, Sentinel blocker/major, or unexpected scope expansion.
