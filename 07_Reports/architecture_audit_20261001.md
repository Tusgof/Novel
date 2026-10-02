# Architecture Audit: Novel Translation Workspace

Date: 2026-10-01
Scope: read-only analysis before an architecture redesign
Repository: `D:\Fogust\Workspace\Novel`

## Executive Summary

The project is operational for bounded work and MoonRead currently builds successfully, but the architecture has accumulated three structural problems:

1. The shared engine is physically owned by `Deep Sea Embers`, while generic code, novel-specific rules, and reader-specific repairs are mixed together.
2. Quality gates are not one consistent acceptance contract. QA, deterministic guardrails, Sentinel, and MoonRead each inspect different representations and have different coverage.
3. New-novel setup is not self-contained. It creates a vault and copied prompts, but it does not copy the provider shim, initialize blocking Sentinel, create an Obsidian vault, or run the mandatory Libra pilot automatically.

The result is a system that can produce a verified bounded batch when an experienced operator coordinates the stages, but it is not yet a reliable long-running platform that can be safely handed a new novel and left to execute.

## Verified Current Map

| Area | Current implementation | Evidence |
|:--|:--|:--|
| Control plane | Root `PROJECT_BRAIN.md`, `IMPLEMENT_PLAN.md`, `ARCHITECTURE.md`, `HERDR_WORKER_PROTOCOL.md` | Root inventory and boot-sequence read |
| Translation engine | `Deep Sea Embers/novel_pipeline/` | 29 Python modules; `pipeline.py` has 4,193 lines |
| Novel state | Four novel folders with raw, work, output, ledger, glossary, and reports | `00_Config/novel_registry.json`; directory inventory |
| Reader | `MoonRead/`, registry-driven generated content | `MoonRead/scripts/generate-chapters.mjs` |
| Provider transport | Per-novel `scripts/openrouter_provider_shim.py` plus CLI providers | Same shim hash across four novel folders |
| Ledger | Append-only JSONL with cross-process append lock | `Deep Sea Embers/novel_pipeline/files.py`, `ledger.py` |
| Current reader build | 4 books, 649 available chapters, 0 missing, 0 rejected | `MoonRead/content/generated/library.json` |
| Current production interruption | Re:Zero ch009/ch010 stopped by provider exhaustion | `Re Zero Watching Him Die Again and Again/07_Reports/rezero_ch009_ch010_provider_limit_checkpoint_20260917.md` |
| Current worktree | Pre-existing dirty `.gitignore`, old Sentinel reports, and Playwright artifacts | `git status --short --untracked-files=all` |

The generated reader state and the working files do not describe the same publication boundary: the registry exposes DSE through `ch281`, HGD through `ch290`, IRS through `ch070`, and Re:Zero through `ch008`, while local output directories contain extra files beyond some of those ranges. The generator correctly follows the registry range, but the duplicated range metadata is a drift risk.

## Findings

| # | Area | Finding | Category | Evidence |
|:--:|:--|:--|:--|:--|
| 1 | Control documents | Current-state claims are inconsistent. `PROJECT_BRAIN.md` contains a MoonRead summary of 3 books / 611 chapters and older DSE/HGD/IRS boundaries, while the generated manifest currently contains 4 books / 649 chapters. The active plan is V6.35, but its next action still describes the old provider-blocked Re:Zero work. | INCONSISTENT | `PROJECT_BRAIN.md` MoonRead and Current Verified State sections versus `MoonRead/content/generated/library.json` and the Re:Zero checkpoint |
| 2 | Engine ownership | The only shared pipeline package is inside `Deep Sea Embers`. This makes the first novel the physical owner of multi-novel execution, scripts, imports, tests, and Sentinel. | DEBT | `Deep Sea Embers/novel_pipeline/`, `Deep Sea Embers/test_translation.py`, `Deep Sea Embers/scripts/` |
| 3 | Cross-layer coupling | Generic pipeline code contains novel-specific branches for HGD, IRS, and Re:Zero, including pronoun repair, title maps, ranked-gate repair, and source-aware repairs. Adding a new novel therefore changes the shared engine or depends on hidden conditionals. | FRAGILE | `Deep Sea Embers/novel_pipeline/pipeline.py` functions `_apply_hgd_peer_address_repairs`, `_normalize_hgd_chapter_title`, `_apply_rezero_source_aware_repairs` |
| 4 | Sentinel ownership | Sentinel is physically located in the DSE scripts folder and its existing guardrail collection hard-codes DSE and HGD paths. IRS and Re:Zero receive some registry-driven checks, but not the same novel-specific guardrail set. | INCONSISTENT | `Deep Sea Embers/scripts/sentinel_quality_report.py`, especially `collect_existing_guardrails()` |
| 5 | Glossary coverage | Sentinel's approved glossary loader only indexes source terms containing Latin letters. DSE has 264 approved pipeline glossary entries but the same audit function returns 0 Sentinel entries for DSE. A green DSE Sentinel result therefore does not prove DSE glossary coverage. | MISSING | Read-only probe: pipeline parser reported 264 approved DSE entries; `sentinel_quality_report.approved_glossary_terms()` reported 0 |
| 6 | QA contract | The QA prompt requests an exact `PASS:`/`FAIL:` verdict, but `parse_ai_feedback()` treats any output without a recognized issue prefix as having no findings. A malformed response such as `not a QA verdict` produces `passed=True` when deterministic rules are clean. | FRAGILE | `Deep Sea Embers/novel_pipeline/stages/qa.py`; local mocked probe returned `Malformed verdict passed: True` |
| 7 | Acceptance boundary | Final assembly writes `05_Output` first and runs blocking Sentinel afterward. A Sentinel failure leaves a final-looking Markdown file on disk, while MoonRead generation validates files rather than checking ledger acceptance. There is no separate accepted/rejected publication state in the output path. | FRAGILE | `_write_chapter_output_with_sentinel_gate()` in `pipeline.py`; `MoonRead/scripts/generate-chapters.mjs` reads output files directly |
| 8 | Formatting semantics | Cleanup functions can remove meaningful source beats. `_clean_refined_output()` drops every line beginning with `*`, and the local formatter removes quotes from short text without a reliable dialogue classifier. A probe showed `*สี่วันผ่านไป*` disappearing and a short quoted sentence losing its quotes. | FRAGILE | `stages/refine.py`, `stages/format.py`; read-only behavior probe |
| 9 | Reader boundary | MoonRead is documented as a consumer of verified Markdown, but the generator repairs Thai mojibake and applies an HGD title map while importing files. The reader can therefore produce content that differs from `05_Output`, and the same policy exists in two places. | INCONSISTENT | `MoonRead/scripts/generate-chapters.mjs`: `repairThaiMojibake()` and `normalizeBookMarkdown()` |
| 10 | Title policy | HGD title normalization exists both in Python pipeline assembly and MoonRead generation. Title sidecars, registry title policy, a Python map, and a JavaScript map can disagree. | DEBT | `pipeline.py`, `scripts/translate_chapter_titles.py`, `MoonRead/scripts/generate-chapters.mjs`, `00_Config/novel_registry.json` |
| 11 | New-novel setup | `initialize_novel_project()` copies prompts and templates but does not copy `scripts/openrouter_provider_shim.py`; the generated provider config still points to `scripts\\openrouter_provider_shim.py`. It also does not create `.obsidian`, enable blocking Sentinel, or start Libra - Pilot Gate. | MISSING | `novel_pipeline/project_setup.py`; isolated setup probe: `Copied provider shim exists: False`, `Obsidian vault config exists: False`, `Sentinel mode: report_only` |
| 12 | Fetch durability | Manifest construction fetches the complete TOC/chapter metadata in memory and writes `manifest.json` only after the entire adapter call returns. A long fetch interruption loses the in-progress manifest and has no resumable fetch ledger. | FRAGILE | `stages/fetch.py` `load_or_build_manifest()`; `adapters/fanfiction_jina.py` `build_manifest()` |
| 13 | Ledger performance | `RunLedger.has_committed()` and related queries reload and parse the complete JSONL file on every call. On the current 4.3 MB DSE ledger, one state load took about 0.145 seconds and ten committed checks took about 1.46 seconds in a local read-only probe. This cost grows with historical retries and long runs. | PERFORMANCE | `novel_pipeline/ledger.py`; timing probe against `Deep Sea Embers/06_Logs/run_ledger.jsonl` |
| 14 | Cost/budget observability | Provider responses record model and duration but do not persist token usage, estimated cost, route budget consumption, or a run-level spend ceiling. The V6.34 measurement contract names cost/sustainability concerns, but runtime evidence cannot calculate provider cost from the ledger. | MISSING | `ProviderResponse`, `RunRecord` metadata, `openrouter_provider_shim.py`; search found no usage/cost fields in pipeline/provider code |
| 15 | Test execution | `test_translation.py` contains 247 test functions but its `__main__` block invokes 197 by name. There is no CI workflow. The standard script passed, but an auto-discovered local call of all 247 functions reported 7 failures, including fixture-dependent and stale-assumption cases. | DEBT | `Deep Sea Embers/test_translation.py`, root inventory (`.github/workflows` absent), auto-discovery probe |
| 16 | Publication range | The registry manually stores `last_chapter` for each novel. Local output counts exceed some registry ranges: DSE has output through `ch291` while registry publishes through `ch281`; HGD has output through `ch293` while registry publishes through `ch290`. This is safe only while every command uses the registry consistently. | FRAGILE | `00_Config/novel_registry.json`; read-only output inventory |
| 17 | Configuration duplication | Each novel has its own `.system/config.yaml` and `.system/providers.yaml`, with copied routing and shim files. The intended Layer 0/Layer 1/Layer 2 model is documented, but runtime loading is still primarily per-novel copying rather than explicit inheritance with validation. | DEBT | Four novel `.system/providers.yaml` files; `config.py`; identical shim hashes |
| 18 | Experiment reproducibility | V6.34 reports show that stale/off-by-one copied experiment source was possible and required a later parity guard. This proves experiment vault identity and source identity were not intrinsic to the artifact contract. | FRAGILE | `07_Reports/v6_34_m5_dse_treatment_source_mismatch_stop_20260701.md`, `verify_experiment_source_parity.py` |
| 19 | Stage output integrity | Literal parsing can fall back to a single pair when provider line count does not match source sentence count, and truncation protection is primarily a character-ratio check for longer blocks. Short omissions rely heavily on QA behavior. | FRAGILE | `stages/translate.py` `parse_literal_pairs()` and `run_literal_translation_stage()` |
| 20 | Worker boundary | HERDR protocol validation is strong and checks scope, hashes, and worker identity, but the runtime has no general persistent work-order registry or machine-enforced file ownership beyond the protocol envelope and append lock. | DEBT | `HERDR_WORKER_PROTOCOL.md`, `scripts/validate_herdr_envelope.py`, `files.py`; no worker-order state store found |

## What Is Working And Should Be Preserved

- Explicit bounded chapter/block ranges and stop conditions.
- Append-only ledger history and cross-process JSONL append locking.
- Hashes and artifact files for stage-level recovery.
- Source parity validation for isolated experiments.
- Blocking Sentinel configuration where enabled, deterministic output guardrails, and major-run spot checks.
- Provider shim token redaction and stdin prompt transport.
- Registry-driven MoonRead book discovery rather than hard-coded novel pages.
- HERDR `ACK -> SMOKE -> START -> RETURN` scope and independent Inspector acceptance.
- Separation of experiment vaults from production output and MoonRead content.

## Main Root Causes

1. **Ownership is physical rather than logical.** The first novel folder owns shared code and shared quality tools.
2. **Policy is duplicated across layers.** Registry, YAML, Python, JavaScript, glossary notes, title sidecars, and prompts can each encode part of the same rule.
3. **Acceptance is file-based rather than state-based.** A Markdown file's existence is close to publication eligibility even when the ledger says a gate failed.
4. **The runtime is optimized for recovery by a knowledgeable operator.** It is not yet optimized for resumable fetch, durable scheduling, budget accounting, or unattended execution.
5. **Tests are regression-oriented but not a complete executable contract.** Many historical checks are embedded in a large script and some are not part of its default execution path.

## Redesign Constraints

Any replacement architecture should preserve the current product behavior while making these boundaries explicit:

- a workspace-level engine independent of any novel folder;
- a typed novel adapter/profile layer for source, language, style, glossary, and title policy;
- one canonical stage contract for artifacts, status, hashes, acceptance, and publication eligibility;
- a fetch ledger that can resume chapter-by-chapter;
- a provider gateway that records route, model, retries, tokens, cost estimate, and stop reason without secrets;
- one quality service with generic checks plus registered novel/language plugins;
- a publication manifest derived from accepted artifacts, not merely from files present on disk;
- a real test runner and CI/hermetic verification path;
- explicit migration handling for existing DSE/HGD/IRS/Re:Zero artifacts and historical reports.

## Verification And Limitations

Verified during this audit:

- `python test_translation.py` passed with `PYTHONIOENCODING=utf-8`.
- `python -m compileall novel_pipeline` passed.
- MoonRead `npm.cmd run lint` passed.
- MoonRead `npm.cmd run build` passed and generated 662 static pages.
- MoonRead `npm.cmd run smoke` passed with no unexpected console errors.
- No provider call, fetch, translation, publication, or architecture mutation was performed.

Limitations:

- Provider quality itself was not rebenchmarked; this is a code/data-flow audit.
- Existing dirty worktree files were preserved and not cleaned.
- The seven failures from auto-invoking all test functions include tests that expect pytest-style fixtures or historical fixtures; they are evidence of a nonstandard harness, not by themselves seven product defects.
- A clean-clone test was not run because the request was diagnostic and the current repository contains large ignored runtime state; portability remains an open verification item.

## Recommended Redesign Order

1. Freeze and snapshot the current behavior and publication manifests.
2. Extract a workspace-level engine and make novel folders data/config/plugin roots.
3. Define stage/artifact/acceptance contracts and make publication consume only accepted manifests.
4. Move quality checks behind one registry-driven interface, including full CJK glossary coverage.
5. Add resumable fetch, provider budget telemetry, and a real test/CI entrypoint.
6. Re-run Libra - Pilot Gate for one novel as a migration validation, then repeat cross-novel OOS checks.

This order is a redesign roadmap, not an implementation claim. No redesign changes were made by this audit.
