# Glossary Approval Decisions: batch-ch004-ch008-v2

**Date:** 2026-04-16
**Run ID:** `batch-ch004-ch008-v2`
**Chapters:** ch004, ch005, ch006, ch007, ch008
**Approval Method:** Deterministic manual gate (Codex decisions, Qwen implementation)

## Summary

- **Total candidates from scan:** 26
- **Approved terms:** 12 (46.2%)
- **Rejected terms:** 24 (including 13 auto-reject + 11 ask-human rejected)
- **Glossary notes created/updated:** 12
- **Ledger records appended:** 5 (ch004-ch008 glossary_approved)
- **Provider calls:** 0 (deterministic implementation only)

## Approved Glossary Terms

The following 12 terms were approved and corresponding glossary notes created/updated in `01_Glossary/`:

| Original Term | Thai Term | Category | Chapter | Block | Approval Notes |
|---------------|-----------|----------|---------|-------|----------------|
| 白橡木号 | เรือโอ๊กขาว | vessel | ch004 | ch004-block-006 | Approved at batch-ch004-ch008-v2 deterministic glossary gate; named vessel. |
| 灵体 | ร่างวิญญาณ | entity | ch004 | ch004-block-001 | Approved at batch-ch004-ch008-v2 deterministic glossary gate; recurring supernatural form. |
| 劳伦斯 | ลอว์เรนซ์ | character | ch004 | ch004-block-004 | Manual addition after source review; recurring named character. |
| 山羊头 | หัวแพะ | entity | ch004 | ch004-block-002 | Manual addition after source review; recurring supernatural shipboard entity/name. |
| 异常099 | สิ่งผิดปกติ 099 | entity | ch004 | ch004-block-006 | Manual addition after source review; recurring anomaly designation. |
| 无垠海 | ทะเลไร้ขอบเขต | location | ch004 | ch004-block-004 | Manual canonical approval; artifact candidate 垠海 is a substring false positive. |
| 灵界 | มิติวิญญาณ | location | ch004 | ch004-block-002 | Manual addition after source review; recurring metaphysical layer/dimension. |
| 幽邃深海 | ทะเลลึกอันเร้นลับ | location | ch004 | ch004-block-003 | Manual addition after source review; recurring cosmological sea/depth term. |
| 人偶 | ตุ๊กตา | entity | ch006 | ch006-block-005 | Manual addition after source review; recurring anomaly/object. |
| 大副 | ต้นเรือ | title | ch004 | ch004-block-005 | Manual addition after source review; recurring nautical rank. |
| 水手长 | หัวหน้ากะลาสี | title | ch006 | ch006-block-004 | Manual addition after source review; recurring crew title. |
| 牧师 | บาทหลวง | title | ch004 | ch004-block-005 | Manual addition after source review; recurring religious title. |

## Rejected Terms

The following 24 terms were rejected (no glossary notes created):

### Auto-Reject (13 terms):
- 邪门, 惊人, 白橡, 白橡木, 橡木号, 橡木, 木号, 身影, 啸声, 一眼, 常反, 邓肯船, 肯船

### Ask-Human Rejected (11 terms):
- 垠海 (substring of approved canonical term 无垠海)
- 舱室 (generic nautical term, not glossary-worthy)
- 呼啸声 (sound effect, not glossary-worthy)
- 罗盘 (generic nautical instrument, not glossary-worthy)
- 符号 (generic term, not glossary-worthy)
- 水手 (generic crew term, not glossary-worthy)
- 盖子 (generic object term, not glossary-worthy)
- 箱子 (generic object term, not glossary-worthy)
- 海面 (generic nautical term, not glossary-worthy)
- 大海 (generic nautical term, not glossary-worthy)
- 球体 (generic term, not glossary-worthy)

## Substring Conflict Resolution

Following glossary policy, substring false positives were rejected in favor of longer canonical terms:

1. **白橡木号 cluster:**
   - Approved: 白橡木号 (full vessel name)
   - Rejected: 白橡, 白橡木, 橡木号, 橡木, 木号 (all substrings)

2. **无垠海 cluster:**
   - Approved: 无垠海 (canonical cosmological sea term)
   - Rejected: 垠海 (substring)

3. **邓肯船 cluster:**
   - Rejected: 邓肯船, 肯船 (known quarantined false-positives)

## Implementation Details

### Files Created/Updated:
1. **Glossary notes (12 files)** in `01_Glossary/`:
   - 白橡木号.md, 灵体.md, 劳伦斯.md, 山羊头.md, 异常099.md
   - 无垠海.md, 灵界.md, 幽邃深海.md, 人偶.md, 大副.md
   - 水手长.md, 牧师.md

2. **Ledger records (10 entries total)** appended to `06_Logs/run_ledger.jsonl`:
   - **Original (malformed):** `glossary_approved` with block_id: ch004-glossary-approved, ch005-glossary-approved, etc.
   - **Correction (correct):** `glossary_approved` with block_id: ch004, ch005, ch006, ch007, ch008
   - Provider: "local"
   - Correction metadata includes `ledger_correction: true` and `corrects_block_id_pattern`

3. **This report** at `07_Reports/glossary_approval_decisions_batch-ch004-ch008-v2.md`

### Validation Performed:
- ✅ All 12 approved glossary notes exist with correct `thai_term` and `status: approved`
- ✅ No glossary notes created for 24 rejected terms
- ✅ 10 `glossary_approved` ledger records exist for batch-ch004-ch008-v2 (5 malformed + 5 corrected)
- ✅ Correction records have proper block_id values (ch004, ch005, etc.)
- ✅ No provider calls made (deterministic implementation only)
- ✅ No modifications to source/output artifacts or quarantine notes

## Ledger Records

### Original Records (Malformed block_id)
Appended glossary_approved records with malformed block_id values (ch004-glossary-approved, etc.):
```json
{
  "approval_mode": "deterministic_manual_gate",
  "decision_report": "07_Reports/glossary_approval_decisions_batch-ch004-ch008-v2.md",
  "approved_terms_count": 12,
  "rejected_terms_count": 24
}
```

### Ledger Correction (2026-04-16)
**Issue:** The pipeline checks `ledger.has_committed(run_id=run_id, block_id=chapter_id, stage="glossary_approved")` requiring exact chapter IDs as block_id.

**Correction:** Appended missing correct glossary_approved records with proper block_id values:
- `ch004`, `ch005`, `ch006`, `ch007`, `ch008`

**Correction metadata:**
```json
{
  "approval_mode": "deterministic_manual_gate",
  "ledger_correction": true,
  "corrects_block_id_pattern": "<chapter>-glossary-approved",
  "decision_report": "07_Reports/glossary_approval_decisions_batch-ch004-ch008-v2.md"
}
```

**Note:** Original malformed records remain in ledger (append-only policy). Correction records enable pipeline to proceed.

## Next Steps

The batch `batch-ch004-ch008-v2` is now ready for translation. The glossary approval gate is complete with:

1. ✅ Human review of classification report completed
2. ✅ Approved glossary terms created/updated (12 terms)
3. ✅ Rejected terms validated (no glossary notes created)
4. ✅ Ledger records appended for all chapters (ch004-ch008)
5. ✅ No provider calls or translation/refinement/QA/formatting executed

**Operational status:** The batch can now proceed with `resume` or `run --range ch004-ch008` to begin literal translation stage.

## Compliance Check

- [x] No Gemini, Claude, or Qwen providers called
- [x] No resume, run --range, rerun-block, translation, refinement, QA, or formatting executed
- [x] No modifications to `04_Work/_batch/batch-ch004-ch008-v2/glossary_scan.json`
- [x] No glossary notes created for rejected terms
- [x] No modifications to quarantine notes
- [x] No edits to source/output artifacts
- [x] No manual rewriting of existing ledger lines (append-only)

---
*Report generated by deterministic glossary approval implementation.*