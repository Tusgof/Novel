# Project Brain: Novel Translation System

Last updated: 2026-06-17

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

## Current Verified State

Deep Sea Embers:

- latest full retranslation run: `deep-sea-embers-retranslate-ch001-ch050-v2`
- `ch001-ch050` translated and repaired under `05_Output/`
- latest product review evidence: `Deep Sea Embers/07_Reports/product_review_deep-sea-embers-retranslate-ch001-ch050-v2_20260616.md`; degraded only because preflight sees the documented untracked queue
- no current failed blocks are known
- final-output checks have covered missing output, Han Chinese body text, provider/meta leakage, quote-only lines, known user-reported variants, paragraph density, and HGD required source beat
- notable approved terms include `实太阳神` -> `สุริยเทพที่แท้จริง` and `面具神` -> `เทพหน้ากาก`
- DSE title fallback incident closed for MoonRead `ch052-ch080`: source titles existed in Chinese, but no `04_Work/ch052-ch080/title.json` sidecars had been created, so final assembly silently fell back to generic `บทที่ N` headings. Prevention: final assembly now refuses named Chinese source titles without a translated title sidecar, and `scripts/check_output_quality_guardrails.py` rejects generic DSE headings when the source title has a real named Chinese title.

Horror Game Developer:

- MoonRead published scope is `ch001-ch100`
- active continuation goal: translate HGD through `ch200`, then publish the completed verified range to MoonRead
- `hgd-ch101-ch110-v1` completed: all 10 blocks translated/refined/QA-passed/formatted/assembled, outputs exist, output guardrails passed, and no current failed blocks remain. This range is not yet published to MoonRead.
- `hgd-ch111-ch120-v1` completed: all 10 blocks translated/refined/QA-passed/formatted/assembled, outputs exist, output guardrails passed, and no current failed blocks remain. This range is not yet published to MoonRead. QA omission hard-fails in this range confirmed the root cause: refinement can still drop poems, thoughts, or sound-effect/source-beat blocks after ordinary retries.
- HGD source titles are English; Thai reader titles are protected by HGD title normalization and title sidecars
- `04_Work/ch001/title.json` through `ch080/title.json` exist to prevent single-block reruns from falling back to English titles
- HGD project folder is now `D:\Fogust\Workspace\Novel\Horror Game Developers`; it has the user-created Obsidian vault and durable pronoun policy at `Horror Game Developers/02_Database_Views/HGD Pronoun Policy.md`
- V6.17 title/format incident is closed for published scope: `ch022-block-001` dropped the source beat "Like that, four days passed."; it was restored as `*และแล้ว สี่วันก็ผ่านไป*`
- V6.17.1 found and repaired narrow English leakage in HGD output: `Horror Developer System`, `Developer Seth Thorne`, `Jump Scare`, `Scenario`, `Section Chief`, selected sound effects in `ch022`, and `Seth's USB stick`
- HGD pronoun incident closed for published scope: Seth-dominant chapters had drifted between `ผม` and `ฉัน`, and Kyle/Seth peer address drifted between `นาย`, `คุณ`, and `เธอ`. Cause: HGD had no durable pronoun policy, and prompts/profile/QA did not pin Seth's Thai voice. Prevention: HGD Obsidian policy note, HGD research/style/prompt/QA pronoun rules, and `scripts/check_output_quality_guardrails.py` Seth-pronoun checks for known high-risk published chapters. Repair report: `Deep Sea Embers/07_Reports/hgd_pronoun_consistency_repair_20260616.md`
- prevention: `scripts/check_output_quality_guardrails.py` checks the HGD `ch022` required source beat, known HGD English leakage terms, and HGD Seth pronoun drift; `test_translation.py` covers the `ch022` and HGD pronoun regressions
- HGD title/truncation incident closed for MoonRead `ch001-ch080`: `ch036-ch080` lacked title sidecars and new title mappings, while `ch002`, `ch060`, and `ch072` had truncation risks from earlier recovery paths. Prevention: HGD title sidecars through `ch080`, `Horror Game Developers/scripts/normalize_hgd_titles.py`, source-vs-output truncation guardrail, and MoonRead title fallback checks. Repair report: `Horror Game Developers/07_Reports/hgd_title_truncation_repair_20260617.md`
- HGD `ch081-ch090` completed under run `hgd-ch081-ch090-v1`; ch089 required deterministic recovery because QA retry repeatedly re-refined away source beats. Prevention for this batch: title normalizer covers `ch036-ch090`, and the recovery metadata records why ch089 used literal-safe manual QA acceptance before AI formatting.
- HGD `ch091-ch100` completed under run `hgd-ch091-ch100-v1` and published to MoonRead. V6.23 smoothness fixes were exercised in production: batch glossary approval worked, HGD title gate stopped missing title mappings before publishing English titles, and QA repair-safe mode recovered ch091/ch093/ch095/ch097 without retry refinement overwriting repairs. Checkpoint: `Horror Game Developers/07_Reports/hgd_ch091_ch100_checkpoint.md`.

MoonRead:

- current reader library includes Deep Sea Embers `ch001-ch080` and Horror Game Developer `ch001-ch100`
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
- QA fallback: Qwen `deepseek-reasoner`, then OpenRouter `deepseek/deepseek-v4-pro`, then Codex emergency fallback
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
- preserve exact source meaning over style polish
- record recurring quality issues and prevention mechanisms here or in `IMPLEMENT_PLAN.md`

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
| HGD final output truncation after force-accept/retry | compare output length against source and reject dangling endings before MoonRead publication |
| Pipeline requires too much manual artifact repair | create a per-batch control packet, use repair-safe QA commands, make next safe action explicit before resume, and use the QA omission literal-safe recovery path before escalating to manual prompt |
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

HGD translation has local verified output through `ch120`; MoonRead remains published through `ch100`.

Next safe choices:

1. Commit the `hgd-ch111-ch120-v1` checkpoint and QA omission recovery code after deterministic validation.
2. Start the next bounded HGD increment with scan-only gate for `ch121-ch130`.
3. Keep MoonRead published scope at `ch001-ch100` until the HGD continuation reaches the approved publish point.
4. Stop again on manual QA prompt, provider failure, command length failure, validation failure, or unexpected scope expansion.
