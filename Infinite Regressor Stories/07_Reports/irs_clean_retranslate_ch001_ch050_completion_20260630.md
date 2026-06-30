# IRS Clean Retranslation ch001-ch050 Completion

Date: 2026-06-30

## Scope

- Novel: Infinite Regressor Stories
- Production clean retranslation scope: ch001-ch050
- Batch size: glossary batches of 5 chapters
- Run IDs:
  - irs-clean-ch001-ch005-v1
  - irs-clean-ch006-ch010-v1
  - irs-clean-ch011-ch015-v1
  - irs-clean-ch016-ch020-v1
  - irs-clean-ch021-ch025-v1
  - irs-clean-ch026-ch030-v1
  - irs-clean-ch031-ch035-v1
  - irs-clean-ch036-ch040-v1
  - irs-clean-ch041-ch045-v1
  - irs-clean-ch046-ch050-v1

## Result

- ch001-ch050 final Markdown files exist under `05_Output/`.
- All 10 batch statuses report current failed blocks: none.
- All 10 batch statuses report manual actions needed: none.
- IRS remains not published to MoonRead because registry reader publishing is disabled for this novel.

## Repairs During Final Gate

- Normalized approved glossary terms in early chapters after later batch approvals:
  - `ZERO_SUGAR` -> `ซีโร่ชูการ์`
  - `iJoinedToday` -> `เพิ่งสมัครวันนี้`
  - `Silver Bells` -> `ระฆังเงิน`
  - `Samcheon World` -> `โลกสามพัน`
  - `National Road Management Corps` -> `หน่วยจัดการถนนแห่งชาติ`
  - `New Buddha Cult` -> `ลัทธิพุทธะองค์ใหม่`
  - `Prophecy` -> `คำพยากรณ์`
- Removed leaked glossary/category note tail from ch020.

## Cause And Prevention

Cause:

- Some terms were approved in later 5-chapter glossary batches, so early output used older variants or left English handles.
- ch020 had an empty source footnote section, but a glossary/category note tail leaked into product text.

Prevention:

- Aggregate Sentinel was rerun across ch001-ch050 after all 5-chapter batches completed.
- Sentinel now includes a blocking `glossary_note_leakage` rule for category-note tails such as `คำ: ชื่อตัวละคร`, `คำ: สิ่งมีชีวิต/ศัตรู`, `คำ: ฉายา/ตำแหน่ง`, and `คำ: คำเรียก...`.
- `test_translation.py` now includes a regression test for glossary note leakage without blocking real story ability lists.

## Verification

- Surface scan: `BAD_COUNT=0`
  - no missing output
  - no Han Chinese body text
  - no provider/meta/error text
  - no runaway repeated characters
  - no quote-only lines
- Blocking Sentinel:
  - `07_Reports/sentinel_quality_irs-clean-ch001-ch050-final-after-leakage-rule_20260630_101639.md`
  - blocker/major/minor/info: `0/0/0/0`
- Advisory Sentinel:
  - `07_Reports/sentinel_quality_irs-clean-ch001-ch050-final-advisory-review-after-leakage-rule_20260630_101829.md`
  - blocker/major/minor/info: `0/0/80/0`
  - all 80 findings are `suspicious_english` minor review items, not publish blockers.
- Major-run spot-check inspected:
  - ch001
  - ch020
  - ch033
  - ch035
  - ch050
- Code validation:
  - `python -m compileall novel_pipeline`: passed
  - `python test_translation.py`: passed

## Remaining

- IRS MoonRead publication is not enabled yet.
- If the user wants IRS in MoonRead, enable reader registry scope separately, regenerate chapters, then run MoonRead `publish:verify`, `lint`, `build`, and `smoke`.
