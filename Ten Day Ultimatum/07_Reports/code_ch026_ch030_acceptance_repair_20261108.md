# Acceptance Repair Report — TDU ch026–ch030

Supersedes `code_ch026_ch030_worker_20261108.md` as acceptance evidence. The prior worker report is left unedited.

- Order: `CODE-TDU-INSPECTOR-REPAIR-20261108` (nonce `code-tdu-acceptance-02`)
- Run: `CODE-TDU-PROD-20261108-ch026-030`, scope ch026–ch030
- Plan: root-relative `04_Work/code_orders/CODE-TDU-INSPECTOR-REPAIR-20261108.json`, sha256 `512eec0fc5e8a07e2eb52d75137752531a7063e32d6abfc16eafe461295c8975`
- Branch/base: `code-tdu-fusionpunk-local` / `208fe61ddd97510306388d1b3ed712c5bf056e7a`
- Authority: local personal reading only. No publication, no MoonRead generation, no Git writes, no provider reroute, no force-accept, no Extra Usage.

## Pre-edit backup

`Ten Day Ultimatum/04_Work/_lean_runs/CODE-TDU-PROD-20261108-ch026-030/_inspector_acceptance_v1/` created before any edit: 36 byte copies plus `MANIFEST.json` (per-file sha256, source path, size) covering, for all five chapters, `refined_checkpoint.json`, `qa_checkpoint.json`, `formatted_checkpoint.json`, `glossary_review.json`, `chapter_result.json`, staged output, and final output, plus the pre-repair `lean_run_report.json`. Pre-repair refined sha256 prefixes: ch026 `8e9a3e865da44517`, ch027 `8bafbd4f452bb554`, ch028 `ba05c339410f6864`, ch029 `ee440d39793349ff`, ch030 `b99b616f3799cdb8`.

## Applied plan (one targeted cycle, paragraph edits then term edits)

Every paragraph edit was applied to the single paragraph containing its anchor; term edits were then applied to the whole chapter text. Existing metadata (including `worker_manual_repairs`, `tdu_repairs`, `source_script_annotation_repairs`) was preserved; a new `draft.metadata.inspector_acceptance_repair` records order id, nonce, plan path/hash, per-rule before/after and exact counts, and source notes.

| Chapter | Paragraph edits | Term edits | Refined chars | `input_hash` (unchanged) |
|:--|--:|--:|--:|:--|
| ch026 | 3 | 4 | 7346 | `a09a849e93ee3f23f2b3c80d7810ef660f2063fec0352dd8e5d61e99bb8099ad` |
| ch027 | 5 | 1 | 6798 | `358b488d3599f8f94f33532cc67e10c007054defe8044f28d976ca30653ffcce` |
| ch028 | 9 | 1 | 6163 | `d409c34d5769c24f0d60499a54e460606522acc11614334b69830ab10d9a3da3` |
| ch029 | 6 | 4 | 6131 | `2bfbcedd0585601ae2dc6c26a23610c41e114fbe0d26e57dd8b6cc92333f22a0` |
| ch030 | 4 | 2 | 6126 | `904f0a9c545bfb49b4f859cb3ffd5c22c2ab479c1a94822cde63bfebf78bad18` |

Term-edit counts as applied: ch026 `มังกรคน`→`มนุษย์มังกร` 2, `ดาบ ‘เจ็ดดำ’`→`‘ดาบเจ็ดดำ’` 1, `‘เจ็ดดำ’`→`‘ดาบเจ็ดดำ’` 1, `ดินแดนผีสางแห่งนี้`→`ที่บ้า ๆ นี่` 2; ch027 `ฉีเฮยเจี้ยน`→`ดาบเจ็ดดำ` 5; ch028 `มังกรคน`→`มนุษย์มังกร` 1; ch029 `เหรินหยาง`→`มนุษย์แกะ` 1, `เรียกภัยพิบัติ`→`กวักภัย` 3, `การสะท้อน`→`เสียงสะท้อน` 1, `เซิงเซียว`→`นักษัตร` 1; ch030 `ไอ้หนุ่มขี้โกง`→`ไอ้หนุ่มจอมโกหก` 1, `ที่ผีสิงแห่งนี้`→`ที่บ้า ๆ นี่` 1.

Ordering mattered in ch029: `การสะท้อน` had 4 matches before paragraph edits and 1 after, so paragraph-first application avoided `เสียงเสียงสะท้อน`. `input_hash` was never rewritten; QA/format/harvest invalidated through normal hash dependency.

## Resume run

`python -B -X utf8 -m novel_pipeline.cli --config "Ten Day Ultimatum/.system/config.yaml" lean-run --chapters ch026-ch030 --run-id CODE-TDU-PROD-20261108-ch026-030 --resume`

- Result: `status: complete`, 5/5 promoted, 0 quarantined.
- `reused_stages` per chapter: `literal_translation`, `refinement` (no new literal or refinement calls).
- Per-chapter QA: PASS (all five), fresh adjudications this cycle.
- Per-chapter staged Sentinel: 0/0/0/0 before promotion.
- No force-accept; no manual QA/format/harvest edits.

## Post-cycle measured routes and corrected fallback claim

This cycle: **10 provider calls** — `qa_judge` `opencode-go/deepseek-v4.1-flash#high` ×5, `term_harvest` `opencode-go/claude-haiku-5-5#low` ×5. No other stage called a provider. Tokens (input+output+reasoning, cache excluded): 71,960 (deepseek-high) + 11,217 (haiku-low). Cost remains unmeasured: `go_allowance_not_reported` / `provider_did_not_report_cost`.

**Correction:** the earlier "zero fallbacks" claim was inaccurate. Traces show **three Haiku-high independent QA adjudications** during the original worker cycles — ch029 `2026-11-07T20:55:07Z`, ch028 `21:11:31Z`, ch029 `21:15:42Z` — all `opencode-go/claude-haiku-5-5#high`. Transport failures remain a separate fact: **zero** provider failures/transport errors across the whole run. This acceptance cycle used no adjudication fallback.

## Gates

- `scripts/check_output_quality_guardrails.py --config "Ten Day Ultimatum/.system/config.yaml" --chapters ch026-ch030` → `output_quality_guardrails: passed` (exit 0).
- `scripts/sentinel_quality_report.py --novel ten-day-ultimatum --chapters ch026-ch030 --scope code-tdu-acceptance-repair-20261108 --fail-on major --skip-advisory-english` → `blocker/major/minor/info: 0/0/0/0` (exit 0); report `07_Reports/sentinel_quality_code-tdu-acceptance-repair-20261108_20261107_214240.{md,json}`.

## Inspection

All five titles unchanged and matching source: ผู้ตาย / ความโง่เขลา / แยกทางกัน / ปริศนา / มนุษย์หนู. Openings, middles and endings read against source with no truncation, no CJK, no Latin runs, no site footer, no omission placeholders.

Targeted verification in the final files: `มนุษย์มังกร` ch026 ×2 / ch028 ×1; `ดาบเจ็ดดำ` ch026 ×2 / ch027 ×5 with `ฉีเฮยเจี้ยน` and `เจ็ดดำ` standalone gone; `มนุษย์แกะ` ch029 ×1, `เหรินหยาง` gone; `กวักภัย` ×3, `เสียงสะท้อน` ×3, `การสะท้อน`/`เรียกภัยพิบัติ` gone; `นักษัตร` ×1, `เซิงเซียว` gone; ch030 `ไอ้หนุ่มจอมโกหก` ×1, `ค้นหาเต๋าในโกดัง` ×1, `ที่บ้า ๆ นี่` ×1. Attribution: ch027 now has `เธออยากจะบอกว่าฉันฆ่าหานอีโม่หรือ?` and `เธอส่ายหน้าแล้วเดินจากไป`; ch028/029 Qi paragraphs use `ฉัน` while Zhao/Li keep `ผม` (per-chapter `ผม/ฉัน`: 3/6, 1/15, 8/18, 5/11, 0/36); ch030 uses `เธอขาดฉันไม่ได้ เธอเข้าใจหรือยัง?`.

Residual observation (no further edit): ch027 still reads `ตัวอักษรเล็ก ๆ สามตัวจารึกไว้ว่า “ดาบเจ็ดดำ”`; the plan mandated the Thai sword name here, so the "three characters" framing now names the sword rather than three glyphs. The source's three-character clue remains present as a scene beat.

## Changed paths and final hashes

- `Ten Day Ultimatum/04_Work/_lean_runs/CODE-TDU-PROD-20261108-ch026-030/ch026..ch030/refined_checkpoint.json` (plan edits + metadata)
- `.../ch026..ch030/qa_checkpoint.json`, `formatted_checkpoint.json`, `glossary_review.json`, `chapter_result.json`, `_staged_output/ch0NN/ch0NN.md` (normal dependency invalidation)
- `.../lean_run_report.json`, `.../lean_run_inspector_acceptance_stdout.log`
- `.../_inspector_acceptance_v1/` (36 backups + `MANIFEST.json`)
- `Ten Day Ultimatum/05_Output/ch026..ch030/ch0NN.md`
- `07_Reports/sentinel_quality_lean-CODE-TDU-PROD-20261108-ch026-030-*` (new cycle reports)
- `07_Reports/sentinel_quality_code-tdu-acceptance-repair-20261108_20261107_214240.{md,json}`
- `Ten Day Ultimatum/07_Reports/code_ch026_ch030_acceptance_repair_20261108.md` (this report)

Final output sha256: ch026 `5a2811d5257726a8233082245995a5ace192c9925076eb5f96c3d51f01cac502`; ch027 `bb5b9e1e0a49374059f94e9d6559fcd78a7f762fad958129d7dcacdb8b535ef6`; ch028 `d63d07c732ea2fe275319f8b7e0fbcf12d2def2528e24e08f871fb50dfef329c`; ch029 `dcaa7e87647c74be1b2e71b7cb0636bc7230e1547fbdbf14bf139e40018a5d7c`; ch030 `73ba5089aa922ed35d2e4a5f29db6446d5fe18fe08adb773cff2b0b1cf189b8f`.

No raw, literal, title, config, glossary, prompt, provider, code, or reader files were edited. Primary checkout, MoonRead WIP and all other-owner work untouched.

## Next action

Inspector independent recheck of the five promoted chapters, then local reader use only.
