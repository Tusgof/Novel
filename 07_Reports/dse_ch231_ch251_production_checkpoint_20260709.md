# DSE ch231-ch251 Production Checkpoint

Date: 2026-07-09

## Scope

- Novel: Deep Sea Embers
- Chapters: `ch231` through `ch251`
- Production output path: `Deep Sea Embers/05_Output/chXXX/chXXX.md`
- MoonRead target: `deep-sea-embers` through `ch251`

## Run IDs

- `dse-ch231-ch235-v1`
- `dse-ch236-ch240-v1`
- `dse-ch241-ch245-v1`
- `dse-ch246-ch250-v1`
- `dse-ch251-v1`

## Completion State

All target chapters completed and final Markdown exists:

- `ch231-ch235`: complete
- `ch236-ch240`: complete
- `ch241-ch245`: complete
- `ch246-ch250`: complete
- `ch251`: complete

Current failed blocks: none.

Historical failed records:

- `dse-ch231-ch235-v1`: 1 historical provider/refine failure, recovered.
- `dse-ch241-ch245-v1`: 1 historical QA hard-fail on `ch242-block-001`, recovered.

## Glossary Decisions Added

New approved terms from this production continuation include:

- `珀利` -> `พอลลี่`
- `拜尔敏` -> `ไบเออร์มิน`
- `真实之眼` -> `ดวงตาแห่งความจริง`
- `海雾舰队` -> `กองเรือหมอกทะเล`
- `倒悬大陆` -> `ทวีปกลับหัว`
- `独眼巨人` -> `ยักษ์ตาเดียว`
- `光影反相` -> `ภาวะแสงเงากลับด้าน`
- `血海` -> `ทะเลเลือด`
- `符文圆环` -> `วงแหวนรูน`
- `现实覆盖` -> `การครอบทับความเป็นจริง`
- `钢铁中将` -> `พลเรือโทเหล็กกล้า`
- `潜渊计划` -> `โครงการดำดิ่งสู่ห้วงลึก`
- `潜渊` -> `ดำดิ่งสู่ห้วงลึก`
- `载人潜水器` -> `ยานดำน้ำบรรทุกคน`
- `安全水深` -> `ความลึกน้ำปลอดภัย`
- `近海安全区` -> `เขตปลอดภัยใกล้ชายฝั่ง`
- `三号潜水器` -> `ยานดำน้ำหมายเลขสาม`

Existing term updated:

- `克里特古王国`: added alias `古克里特王国`.

## Incidents And Recovery

### `ch242-block-001` QA false hard-fail

Cause: QA confused two source names in the same block. The source line says `“邓肯”`, so Thai `“ดันแคน”` was correct. Another nearby sentence references a thing disguised as `“周铭”`, which was correctly rendered as `“โจวหมิง”`.

Action: reran the block from QA without force-accepting.

Result: QA passed with retry `0`, formatting completed, and `ch242.md` assembled.

Prevention note: if this pattern recurs, prefer block-level source comparison before treating name-related QA hard-fails as real drift.

### `dse-ch246-ch250-v1` command wrapper timeout

Cause: the bounded resume exceeded the shell wrapper timeout while the pipeline process was still active.

Action: monitored the original process and ledger instead of launching a duplicate resume.

Result: the existing process completed through `ch250` with no current failed blocks.

Prevention note: for long 5-chapter runs, monitor ledger/process after wrapper timeout before rerunning.

## Verification

- `novel-pipeline status` for all five run IDs: no current failed blocks, no manual action needed.
- `python scripts/check_output_quality_guardrails.py --novel deep-sea-embers --chapters ch231-ch251`: passed.
- `python scripts/sentinel_quality_report.py --scope dse-ch231-ch251-final --novel deep-sea-embers --chapters ch231-ch251 --fail-on major --skip-advisory-english`: blocker/major/minor/info `0/0/0/0`.
- `python -m compileall novel_pipeline`: passed.
- `python test_translation.py`: passed.

Spot-check chapters:

- `ch231`
- `ch236`
- `ch242` incident chapter
- `ch246`
- `ch251`

Spot-check result: titles, openings, middles, endings, paragraph density, and glossary usage were acceptable. `ch246` contains a source author-promo note with English book-title text; this is source-side promo text, not story-body leakage.

## MoonRead

`00_Config/novel_registry.json` was updated so Deep Sea Embers publishes through `ch251`.

MoonRead verification must run after this report:

- `npm.cmd run generate:chapters`
- `npm.cmd run publish:verify`

## Next Safe Action

Publish to MoonRead, run reader checks, inspect generated `ch231`, `ch242`, and `ch251`, then commit and push if all checks pass.
