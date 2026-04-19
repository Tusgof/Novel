# Glossary Approval Decisions: batch-ch009-ch018-v1

## Summary
- **Run ID**: batch-ch009-ch018-v1
- **Approved count**: 1
- **Rejected count**: 29
- **Chapters marked glossary_approved**: ch009, ch010, ch011, ch012, ch013, ch014, ch015, ch016, ch017, ch018

## Approved Terms
| Source Term | Thai Term | Category | First Seen Chapter | First Seen Block | Rationale |
|-------------|-----------|----------|-------------------|------------------|-----------|
| 瓦斯灯 | โคมไฟแก๊ส | item | ch018 | ch018-block-003 | Period technology / recurring setting object in ch018 sewer scenes. Consistent Thai rendering is useful. |

## Rejected Terms
| Source Term | Reason |
|-------------|--------|
| 球体 | Generic descriptive term ("sphere"), not a proper noun |
| 文明 | Generic noun ("civilization") |
| 箱子 | Generic object ("box") |
| 火炮 | Generic nautical term ("cannon") |
| 海面 | Generic term ("sea surface") |
| 一脸 | Generic descriptive phrase ("face expression") |
| 剪影 | Generic descriptive term ("silhouette") |
| 罗盘 | Generic item ("compass") |
| 光线 | Generic term ("light ray") |
| 影子 | Generic term ("shadow") |
| 许多 | Generic quantifier ("many") |
| 阴影 | Generic term ("shadow") |
| 石头 | Generic object ("stone") |
| 躯体 | Generic term ("body") |
| 段距 | Likely measurement term ("segment distance") |
| 文字 | Generic term ("text") |
| 些城 | Substring false positive of "那些城邦" |
| 诅咒人 | Substring fragment of "诅咒人偶" |
| 咒人 | Substring fragment of "诅咒人偶" |
| 开眼 | Substring fragment of "睁开眼睛" |
| 斯灯 | Substring fragment of "瓦斯灯" |
| 毛笔 | Likely misidentified; context suggests "羽毛笔" (feather pen) |
| 睁开眼 | Generic phrase ("open eyes") |
| 幽灵 | Context-dependent; appears in compounds like 幽灵船长 / 幽灵烈焰. Do not force a standalone glossary rendering. |
| 汪洋 | Poetic/common ocean descriptor; translate contextually. |
| 深海 | Substring of approved 幽邃深海; do not create a separate entry. |
| 航海 | Generic nautical activity; translate contextually or by compound. |
| 尸体 | Generic horror/body term; translate contextually. |
| 符号 | Generic symbol/mark term; if a specific mystical term like 符文 appears later, classify that separately. |

## Ledger Records Appended
Appended 10 glossary_approved ledger records with block_id values:
- ch009
- ch010
- ch011
- ch012
- ch013
- ch014
- ch015
- ch016
- ch017
- ch018

Each record includes metadata:
- approval_mode: deterministic_manual_gate
- decision_report: 07_Reports/glossary_approval_decisions_batch-ch009-ch018-v1.md
- approved_terms_count: 1
- rejected_terms_count: 29
- approved_terms: ["瓦斯灯"]
- rejected_terms: [list of 29 rejected terms]

## Safety Checks
✅ **Confirmed**:
- No provider calls (Gemini, Claude, Qwen, Codex, or any AI provider)
- No translation/refinement/QA/formatting executed
- No source files (03_Raw/) modified
- No output files (05_Output/) modified
- No glossary notes created for rejected terms
- Append-only ledger policy respected (only appended new records, no edits/deletions)
- No code/config (.system/, novel_pipeline/) modified
- No production artifacts (04_Work/ except read-only scan artifact) modified

**Files changed**:
1. `01_Glossary/瓦斯灯.md` – created with approved term
2. `06_Logs/run_ledger.jsonl` – appended 10 glossary_approved records
3. `07_Reports/glossary_approval_decisions_batch-ch009-ch018-v1.md` – this report

**Validation**: See validation command results in final console report.