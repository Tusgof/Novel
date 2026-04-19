# Glossary Classification Report: batch-ch019-ch023-v1

## 1. Scope
- Run ID: batch-ch019-ch023-v1
- Candidate source artifact path: 04_Work/_batch/batch-ch019-ch023-v1/glossary_scan.json
- Total candidate count: 23
- Confirmation: No glossary/ledger/output/code files were modified during classification

## 2. Candidate Inventory
| Source Term | Category | Chapter ID | First Seen Block | Classification | Reason |
|---|---|---|---|---|---|
| 人影 | term | ch019 | ch019-block-001 | auto_reject | Generic/common noun meaning "human figure" |
| 些黑袍人 | title | ch019 | ch019-block-003 | auto_reject | Descriptive phrase/noisy fragment around 黑袍人 |
| 黑袍人 | term | ch019 | ch019-block-003 | auto_reject | Generic descriptor; contextual translation preferred |
| 袍人 | term | ch019 | ch019-block-003 | auto_reject | Substring/noise of 黑袍人 |
| 阳神 | term | ch019 | ch019-block-004 | ask_human | Possible lore/religious term; needs human review |
| 高台 | term | ch020 | ch020-block-001 | auto_reject | Generic location/common noun |
| 实太阳神 | title | ch020 | ch020-block-004 | ask_human | Likely formal cult/religious title; needs human decision |
| 面具神 | term | ch020 | ch020-block-004 | ask_human | Possible deity/lore reference; needs human decision |
| 具神 | term | ch020 | ch020-block-004 | auto_reject | Substring/noise from 面具神 |
| 黑曜石 | term | ch021 | ch021-block-003 | ask_human | Material term in 黑曜石小刀; may be generic or lore object |
| 曜石 | term | ch021 | ch021-block-003 | auto_reject | Substring/noise from 黑曜石 |
| 好像 | term | ch021 | ch021-block-003 | auto_reject | Common adverb ("seem/as if"); should be translated contextually |
| 船长室门 | term | ch022 | ch022-block-001 | auto_reject | Generic location phrase |
| 长室门 | term | ch022 | ch022-block-001 | auto_reject | Substring/noise |
| 船长室 | term | ch022 | ch022-block-001 | auto_reject | Generic location term |
| 长室 | term | ch022 | ch022-block-001 | auto_reject | Substring/noise |
| 室门 | term | ch022 | ch022-block-001 | auto_reject | Substring/noise |
| 邓肯船 | term | ch022 | ch022-block-003 | auto_reject | Confirmed quarantine false-positive; do not ask human |
| 肯船 | term | ch022 | ch022-block-003 | auto_reject | Confirmed quarantine false-positive; do not ask human |
| 是失乡号 | vessel | ch022 | ch022-block-004 | auto_reject | Noisy phrase containing approved 失乡号 + 是 |
| 区域 | term | ch022 | ch022-block-004 | auto_reject | Generic/common noun |
| 罗盘 | term | ch023 | ch023-block-005 | auto_reject | Generic object; reject for now unless context proves special |
| 鸽子 | term | ch023 | ch023-block-005 | ask_human | Generic animal but may be special; ask human |

## 3. Auto-Approve Candidates
None

## 4. Auto-Reject Candidates
- 人影: generic/common
- 些黑袍人: phrase/noisy fragment around 黑袍人
- 黑袍人: generic descriptor; contextual translation preferred
- 袍人: substring/noise
- 高台: generic location/common noun
- 具神: substring/noise from 面具神
- 曜石: substring/noise from 黑曜石
- 好像: common adverb
- 船长室门: generic location phrase
- 长室门: substring/noise
- 船长室: generic location term
- 长室: substring/noise
- 室门: substring/noise
- 邓肯船: confirmed quarantine false-positive; do not ask human
- 肯船: confirmed quarantine false-positive; do not ask human
- 是失乡号: noisy phrase containing approved 失乡号, includes 是
- 区域: generic/common
- 罗盘: generic object

## 5. Ask-Human Candidates
- 阳神: possible lore/religious term
  - Possible renderings: พระอาทิตย์, สุริยเทพ (suggestions only)
- 实太阳神: likely formal cult/religious title
  - Possible renderings: พระอาทิตย์จริงเจ้า, สุริยเทพที่แท้จริง (suggestions only)
- 面具神: possible deity/lore reference
  - Possible renderings: เทพหน้ากาก, พระเจ้าหน้ากาก (suggestions only)
- 黑曜石: material term in 黑曜石小刀; may be generic or lore object
  - Possible renderings: อ็อบซิเดียนสีดำ, หินภูเขาไฟสีดำ (suggestions only)
- 鸽子: generic animal but may be special in context
  - Possible renderings: นกพิราบ, นกโพรง (suggestions only)

## 6. Existing Glossary Conflicts
- 失乡号 exists and is approved as เรือผู้ไร้บ้าน.
- 是失乡号 is not a glossary term because it is a phrase including 是 + approved 失乡号.
- 邓肯船 and 肯船 are present in quarantine and are confirmed false positives.
- No exact approved match for 阳神, 实太阳神, 面具神, 黑曜石, 鸽子 unless otherwise found.

## 7. Substring / Noise Clusters
- 黑袍人 cluster: 些黑袍人, 黑袍人, 袍人
- 阳神 cluster: 阳神, 实太阳神, 面具神, 具神
- 黑曜石 cluster: 黑曜石, 曜石
- 船长室 cluster: 船长室门, 长室门, 船长室, 长室, 室门
- 失乡号 cluster: 是失乡号
- Duncan false-positive cluster: 邓肯船, 肯船

## 8. Validation
- Report opened in UTF-8: Chinese characters display correctly, no mojibake
- Candidate terms display as clean Chinese: all 23 terms visible as expected
- No mojibake fragments (e.g., ไบบๅฝฑ, ้ณยฅ, เธ, เน€) present
- 邓肯船 classified as auto_reject (not ask_human)
- Ask-human list contains exactly 5 terms: 阳神, 实太阳神, 面具神, 黑曜石, 鸽子
- No Thai mojibake remains in report
- No forbidden files modified (only 07_Reports/glossary_classification_batch-ch019-ch023-v1.md changed)

## 9. Blockers
None

## 10. Recommended Next Action
Codex/user 应审查 ask-human 术语并批准最终术语表决策后再进行任何翻译。