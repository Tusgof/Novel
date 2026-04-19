# Glossary Scan Report: batch-ch019-ch023-v1

## 1. Scope
- Run ID: batch-ch019-ch023-v1
- Chapter range: ch019-ch023
- Command run: `novel-pipeline --config ".system/config.yaml" run --range ch019-ch023 --run-id batch-ch019-ch023-v1 --stop-after glossary-scan`
- Timestamp: 2026-04-19

## 2. Execution Result
- Success: Yes
- Fetch completed: Yes - 5 chapters fetched (ch019-ch023)
- Scan-only stop message appeared: Yes - "Stop requested after glossary scan. Review batch glossary artifact before approval."
- Command exited cleanly: Yes (exit code 0)

## 3. Ledger/Status Summary
- Total records: 10
- Fetched record count: 5
- Glossary scanned record count: 5
- Glossary approved record count: 0
- Translation/refinement/QA/formatting/completed record count: 0
- Current failed records: 0
- ch024+ records: 0
- Artifact path: 04_Work/_batch/batch-ch019-ch023-v1/glossary_scan.json
- Item count: 23

## 4. Batch Glossary Artifact
- Path: 04_Work/_batch/batch-ch019-ch023-v1/glossary_scan.json
- Exists: Yes
- Chapter IDs: ch019, ch020, ch021, ch022, ch023

## 5. Candidate Terms
| Source Term | Category | Chapter ID | First Seen Block | Notes |
|---|---|---|---|---|
| 人影 | term | ch019 | ch019-block-001 | Standard Chinese term |
| 些黑袍人 | title | ch019 | ch019-block-003 | Descriptor phrase |
| 黑袍人 | term | ch019 | ch019-block-003 | Common fantasy term |
| 袍人 | term | ch019 | ch019-block-003 | Short form fragment |
| 阳神 | term | ch019 | ch019-block-004 | Proper noun/lore deity |
| 高台 | term | ch020 | ch020-block-001 | Common location term |
| 实太阳神 | title | ch020 | ch020-block-004 | Formal title/name |
| 面具神 | term | ch020 | ch020-block-004 | Lore term |
| 具神 | term | ch020 | ch020-block-004 | Fragment/abbreviation |
| 黑曜石 | term | ch021 | ch021-block-003 | Material/object term |
| 曜石 | term | ch021 | ch021-block-003 | Fragment of 黑曜石 |
| 好像 | term | ch021 | ch01-block-003 | Common adverb |
| 船长室门 | term | ch022 | ch022-block-001 | Descriptive compound |
| 长室门 | term | ch022 | ch022-block-001 | Fragment of 船长室门 |
| 船长室 | term | ch022 | ch022-block-001 | Common location term |
| 长室 | term | ch022 | ch022-block-001 | Fragment of 船长室 |
| 室门 | term | ch022 | ch022-block-001 | Fragment of 船长室门 |
| 邓肯船 | term | ch022 | ch022-block-003 | Character-specific name |
| 肯船 | term | ch022 | ch022-block-003 | Fragment of 邓肯船 |
| 是失乡号 | phrase | ch022 | ch022-block-004 | Verb phrase |
| 区域 | term | ch022 | ch022-block-004 | Common noun |
| 罗盘 | term | ch023 | ch023-block-005 | Common object term |
| 鸽子 | term | ch023 | ch023-block-005 | Common animal term |

## 6. Initial Classification Hints
- **Likely review/lore/proper noun terms**:
  - 阳神, 实太阳神, 面具神, 黑曜石, 船长室门, 是失乡号
- **Likely generic/common terms**:
  - 人影, 黑袍人, 高台, 好像, 船长室, 区域, 罗盘, 鸽子
- **Likely substring/noise fragments**:
  - 些黑袍人, 袍人, 具神, 曜石, 长室门, 长室, 室门, 邓肯船, 肯船
- **Possible conflicts with existing glossary**:
  - 是失乡号 may be noisy because approved term likely is 失乡号 / เรือผู้ไร้บ้าน.
  - 邓肯船 and 肯船 are known false-positive style substrings and should not be treated as real terms.

## 7. Guardrail Verification
- [x] No glossary notes created/modified in 01_Glossary/
- [x] No final outputs created for ch019-ch023 (all output paths missing)
- [x] No translation/refinement/QA/formatting stages active
- [x] No ch024+ processing detected
- [x] No provider calls outside scan/fetch behavior
- [x] No manual ledger edits (records are from automated pipeline)

## 8. Blockers
None - scan completed successfully as expected.

## 9. Recommended Next Step
Codex/user should review glossary scan and perform glossary classification/approval gate before any translation.