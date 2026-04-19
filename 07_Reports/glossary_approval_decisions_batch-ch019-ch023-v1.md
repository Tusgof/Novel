# Glossary Approval Decisions: batch-ch019-ch023-v1

## 1. Scope
- Run ID: batch-ch019-ch023-v1
- Candidate count: 23
- Approval mode: user_v3_9_glossary_gate
- Source classification report: 07_Reports/glossary_classification_batch-ch019-ch023-v1.md

## 2. Approved Terms
| original_term | thai_term | category | first_seen_chapter | first_seen_block | glossary_note_path | reason |
|---|---|---|---|---|---|---|
| 实太阳神 | สุริยเทพที่แท้จริง | title | ch020 | ch020-block-004 | 01_Glossary/实太阳神.md | Formal cult/religious title; approved by user during V3.9 glossary approval gate |
| 面具神 | เทพหน้ากาก | entity | ch020 | ch020-block-004 | 01_Glossary/面具神.md | Deity/lore reference; approved by user during V3.9 glossary approval gate |

## 3. Rejected Terms
- 人影: generic/common
- 些黑袍人: phrase/noisy fragment around 黑袍人
- 黑袍人: generic descriptor; contextual translation preferred
- 袍人: substring/noise
- 阳神: possible lore term but rejected for now
- 高台: generic location/common noun
- 具神: substring/noise from 面具神
- 黑曜石: material term; generic or lore object but rejected for now
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
- 罗盘: generic object unless later context proves special; reject for now
- 鸽子: generic animal but may be special; ask human (kept for review but not approved)

## 4. Ledger Records Appended
- block_id: ch019 | stage: glossary_approved | status: completed
- block_id: ch020 | stage: glossary_approved | status: completed
- block_id: ch021 | stage: glossary_approved | status: completed
- block_id: ch022 | stage: glossary_approved | status: completed
- block_id: ch023 | stage: glossary_approved | status: completed

## 5. Guardrail Verification
- no translation/refinement/QA/formatting executed for this batch run
- no final outputs created for ch019-ch023 (05_Output/ remains absent)
- no ch024+ processing
- no provider calls outside local ledger append
- no rejected glossary notes created in 01_Glossary/
- no quarantine notes modified in 01_Glossary/quarantine/
- append-only ledger recorded for exactly 5 blocks with run_id=batch-ch019-ch023-v1

## 6. Next Step
Run status should now show glossary_approved completed and blocks pending translating. Codex/user must explicitly approve before translation begins.