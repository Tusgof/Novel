# Cross-Chapter Consistency Audit Report
## Chapters ch001-ch003
**Date:** 2026-04-16  
**Auditor:** Qwen Code  
**Project:** Deep Sea Embers Translation Pipeline

---

## 1. Files Read
- `D:\Fogust\Workspace\Novel\AGENTS.md`
- `D:\Fogust\Workspace\Novel\Deep Sea Embers\PROJECT_BRAIN.md`
- `D:\Fogust\Workspace\Novel\Deep Sea Embers\Implement_PLAN.md`
- `D:\Fogust\Workspace\Novel\Deep Sea Embers\01_Glossary\*.md` (16 glossary files)
- `D:\Fogust\Workspace\Novel\Deep Sea Embers\05_Output\ch001\ch001.md`
- `D:\Fogust\Workspace\Novel\Deep Sea Embers\05_Output\ch002\ch002.md`
- `D:\Fogust\Workspace\Novel\Deep Sea Embers\05_Output\ch003\ch003.md`
- Formatted JSON artifacts in `04_Work\ch001`, `04_Work\ch002`, `04_Work\ch003`

## 2. Files Changed
- Created: `D:\Fogust\Workspace\Novel\check_chinese.py` (temporary)
- Created: `D:\Fogust\Workspace\Novel\check_quotes.py` (temporary)
- Created: `D:\Fogust\Workspace\Novel\check_glossary.py` (temporary)
- Created: `D:\Fogust\Workspace\Novel\Deep Sea Embers\07_Reports\cross_chapter_consistency_ch001_ch003.md` (this report)

## 3. Validation Commands and Results

### 3.1 Python Compilation
```bash
python -m compileall novel_pipeline
```
**Result:** Success - No syntax errors

### 3.2 Translation Tests
```bash
python test_translation.py
```
**Result:** Success - "All tests passed!"

### 3.3 Run Status Checks
```bash
novel-pipeline --config ".system/config.yaml" status --run-id run-ch001-clean-v4
```
**Result:** 
- Run `run-ch001-clean-v4`: Complete
- 5/5 blocks complete for ch001
- No failed blocks
- Output exists: `05_Output/ch001/ch001.md`

```bash
novel-pipeline --config ".system/config.yaml" status --run-id batch-ch002-ch003-v1
```
**Result:**
- Run `batch-ch002-ch003-v1`: Complete
- ch002: 6/6 blocks complete
- ch003: 5/5 blocks complete
- No failed blocks
- Outputs exist: `05_Output/ch002/ch002.md`, `05_Output/ch003/ch003.md`

## 4. Chapter/Block Artifact Summary

### ch001 Status
- **Expected blocks:** 5
- **Formatted JSON artifacts:** 5 (`ch001-block-001` to `ch001-block-005.formatted.json`)
- **Final output:** `05_Output/ch001/ch001.md` exists (100 lines)
- **Status:** Complete

### ch002 Status
- **Expected blocks:** 6
- **Formatted JSON artifacts:** 6 (`ch002-block-001` to `ch002-block-006.formatted.json`)
- **Final output:** `05_Output/ch002/ch002.md` exists (71 lines)
- **Status:** Complete

### ch003 Status
- **Expected blocks:** 5
- **Formatted JSON artifacts:** 5 (`ch003-block-001` to `ch003-block-005.formatted.json`)
- **Final output:** `05_Output/ch003/ch003.md` exists (84 lines)
- **Status:** Complete

## 5. Provider/Meta/Error Leakage Result
**Search patterns:** `quota|rate limit|429|capacity|Provider|Traceback|Exception|stderr|stdout|Gemini|Claude|Qwen`

**Result:** **NONE** - No provider/meta/error text found in any final output.

## 6. Chinese Body Text Result
**Method:** Regex search for Han characters (`[\u4e00-\u9fff]`) excluding first line (chapter title).

**Result:** **NONE** - No untranslated Chinese body text found.

**Note:** One line in ch003.md (line 83) triggered a false positive due to encoding/mojibake issues in the PowerShell regex, but Python regex confirmation shows no actual Chinese characters.

## 7. Quote/Italic/Paragraph Formatting Findings

### 7.1 Quote-Only Lines
**Finding:** `ch001.md` contains 24 quote-only lines (lines containing only `"`).

**Examples:**
- Line 12: `"`
- Line 14: `"`
- Line 18: `"`
- ... (24 total occurrences)

**Analysis:** These appear to be dialogue formatting where quotes are on separate lines from content (e.g., `"` on line 12, `ข้างนอก` on line 13, `"` on line 14). This is a formatting style choice, not necessarily a bug.

**Recommendation:** Review formatter behavior for dialogue quotes. If this is intentional formatting for standalone dialogue markers, it's acceptable. If unintentional, the formatter should be adjusted to keep quotes on the same line as dialogue content.

### 7.2 Long Paragraphs
**Finding:** One unusually long paragraph in `ch001.md` line 9 (601 Thai characters).

**Excerpt:** `หลังจากตื่นนอนขึ้นมา เขาพบว่าตัวเองถูกขังอยู่ในห้องของตัวเอง นอกหน้าต่างคือหมอกหนาที่ไม่ยอมจางหาย ไอ...`

**Analysis:** The formatter's paragraph splitting may need adjustment for paragraphs over ~600 characters.

### 7.3 Italicized Sound Effects
**Manual inspection shows:**
- Sound effects like `ครืด...` and `ปัง!` appear to be properly italicized
- No obvious issues with non-dialogue quoted text being treated as dialogue
- Dialogue retains quote marks appropriately

## 8. Glossary Consistency Findings

### 8.1 Blockers (Critical Issues)

**1. Glossary Term Variant Inconsistency**
- **File:** `05_Output/ch002/ch002.md`
- **Line 39:** `"ดันแคน เอบนอร์มัล"` (incorrect variant)
- **Line 67:** `ดันแคน แอบโนมาร์` (correct, matches glossary)
- **Glossary:** Approved term is `แอบโนมาร์` (not `เอบนอร์มัล`)

**Impact:** Character name inconsistency within same chapter. The variant `เอบนอร์มัล` appears only once but contradicts the approved glossary term.

### 8.2 Non-Blocking Issues

**1. Character Name Distribution**
- `ดันแคน` (Duncan): ch002 (12 times), ch003 (20 times), ch001 (0 times)
- `โจวหมิง` (Zhou Ming): ch001 (17), ch002 (18), ch003 (1)
- **Analysis:** This may be correct if Duncan is not named in chapter 1 (character introduction timing).

**2. Ship Name Consistency**
- `เรือผู้ไร้บ้าน` (The Lost Home): ch002 (1), ch003 (11), ch001 (0)
- **Analysis:** Consistent usage across chapters where the ship appears.

### 8.3 Deprecated/Quarantined Terms Check
- `เรือสูญถิ่น` (deprecated for `乡号`): **NOT FOUND** in any output ✓
- `邓肯船`, `肯船` (quarantined): **NOT FOUND** in any output ✓

### 8.4 Suggested Glossary or Formatter Follow-ups

1. **Rerun block ch002-block-002** (or appropriate block containing line 39) to fix `เอบนอร์มัล` → `แอบโนมาร์`
2. **Verify ch001 source** to confirm Duncan should not appear by name in chapter 1
3. **Review formatter** for quote-only lines in dialogue formatting
4. **Consider adding** `เอบนอร์มัล` as an alias in the `艾布诺马尔` glossary entry if variant is acceptable

## 9. Final Recommendation

### **Status: NOT READY for production dry-run**

### **Blockers:**
1. **Glossary inconsistency** in ch002: Character name `เอบนอร์มัล` vs approved `แอบโนมาร์`
   - **File:** `05_Output/ch002/ch002.md` line 39
   - **Action required:** Rerun affected block from refinement or formatting stage

### **Non-blocking issues requiring review:**
1. **Quote-only lines** in ch001 (24 occurrences) - formatting style review needed
2. **Long paragraph** in ch001 line 9 (601 characters) - formatter tuning opportunity
3. **Character name distribution** - verify Duncan absence in ch001 is correct

### **Positive findings:**
- No provider/meta/error leakage ✓
- No untranslated Chinese body text ✓
- No deprecated/quarantined terms in outputs ✓
- All chapters complete with correct block counts ✓
- All validation commands pass ✓

## 10. Anything Codex Should Review Carefully

1. **The `เอบนอร์มัล` variant in ch002 line 39** - This is the only critical blocker. Should be fixed by rerunning the affected block.

2. **Quote-only lines formatting** - Determine if this is intentional formatting style or a formatter bug. If intentional, update formatting policy documentation.

3. **Duncan name absence in ch001** - Check source material to confirm this is correct (character may not be named until chapter 2).

4. **Formatted JSON artifacts** - All present and correct counts (5, 6, 5 blocks respectively).

5. **Provider usage in ledger** - Status shows some provider failures in historical data but all blocks ultimately completed successfully.

---

**Next Steps:**
1. Fix glossary inconsistency in ch002
2. Review and decide on quote formatting style
3. Verify character introduction timing
4. Re-audit after fixes before production batch

**Audit completed:** 2026-04-16

---

## 11. Repair Verification (2026-04-16)

### 11.1 Repair Actions Taken

**Glossary inconsistency fix for ch002:**
1. **Block ch002-block-003:** Rerun from formatting stage
   - Command: `novel-pipeline --config ".system/config.yaml" rerun-block --run-id batch-ch002-ch003-v1 --block-id ch002-block-003 --from-stage format`
   - Result: Success - Formatted artifact regenerated

2. **Block ch002-block-004:** Rerun from refinement stage (after deleting stale refined artifact)
   - Command: `del "04_Work\ch002\ch002-block-004.refined.json"`
   - Command: `novel-pipeline --config ".system/config.yaml" rerun-block --run-id batch-ch002-ch003-v1 --block-id ch002-block-004 --from-stage refine`
   - Result: Success - Refined and formatted artifacts regenerated, QA passed

### 11.2 Post-Repair Validation

**Python compilation:**
```bash
python -m compileall novel_pipeline
```
**Result:** Success - No syntax errors

**Translation tests:**
```bash
python test_translation.py
```
**Result:** Success - "All tests passed!"

**Run status:**
```bash
novel-pipeline --config ".system/config.yaml" status --run-id batch-ch002-ch003-v1
```
**Result:**
- All blocks complete (11/11)
- No failed blocks
- Final outputs exist for ch002 and ch003

### 11.3 Glossary Consistency Verification

**Wrong variant scan results:**
- `ดันแคน เอบนอร์มัล`: **NOT FOUND** ✓
- `ดันแคน แอบนอร์มัล`: **NOT FOUND** ✓  
- `เอบนอร์มัล`: **NOT FOUND** ✓
- `แอบนอร์มัล`: **NOT FOUND** ✓

**Correct term verification:**
- `ดันแคน แอบโนมาร์`: **FOUND** in:
  - `05_Output/ch002/ch002.md` (lines 39, 55, 57, 67)
  - `04_Work/ch002/ch002-block-003.refined.json`
  - `04_Work/ch002/ch002-block-003.formatted.json`
  - `04_Work/ch002/ch002-block-004.refined.json`
  - `04_Work/ch002/ch002-block-004.formatted.json`

### 11.4 Output Cleanliness Post-Repair

**Provider/meta/error text:** NONE found in any chapter ✓

**Chinese body text:** NONE found in any chapter (excluding chapter titles) ✓

**Quote-only lines:**
- ch001: 26 quote-only lines (unchanged - formatting style question)
- ch002: 0 quote-only lines ✓
- ch003: 0 quote-only lines ✓

### 11.5 Updated Status

**Previous blocker RESOLVED:**
- Glossary inconsistency in ch002 has been fixed
- All instances of `邓肯·艾布诺马尔` now correctly translated as `ดันแคน แอบโนมาร์`

**Remaining non-blocking issues:**
- Quote-only lines in ch001 (26 occurrences) - formatting style review needed
- Long paragraph in ch001 line 9 (601 characters) - formatter tuning opportunity
- Character name distribution - Duncan not named in ch001 (may be correct)

### 11.6 Production Readiness Assessment

**Status: READY for production dry-run**

**All critical blockers resolved:**
1. ✓ Glossary consistency fixed
2. ✓ No provider/meta/error leakage
3. ✓ No Chinese body text
4. ✓ No deprecated/quarantined terms
5. ✓ All validation commands pass
6. ✓ All blocks complete

**Repair verified:** 2026-04-16

---

## 12. ch001 Formatting Repair Verification (2026-04-16)

### 12.1 Repair Actions Taken

**Formatting debt fix for ch001:**
1. **All ch001 blocks (001-005):** Rerun from formatting stage
   - Command: `novel-pipeline --config ".system/config.yaml" rerun-block --run-id run-ch001-clean-v4 --block-id ch001-block-001 --from-stage format`
   - Command: `novel-pipeline --config ".system/config.yaml" rerun-block --run-id run-ch001-clean-v4 --block-id ch001-block-002 --from-stage format`
   - Command: `novel-pipeline --config ".system/config.yaml" rerun-block --run-id run-ch001-clean-v4 --block-id ch001-block-003 --from-stage format`
   - Command: `novel-pipeline --config ".system/config.yaml" rerun-block --run-id run-ch001-clean-v4 --block-id ch001-block-004 --from-stage format`
   - Command: `novel-pipeline --config ".system/config.yaml" rerun-block --run-id run-ch001-clean-v4 --block-id ch001-block-005 --from-stage format`
   - **Result:** All commands succeeded. Final chapter output rewritten automatically.

### 12.2 Post-Repair Validation

**Python compilation:**
```bash
python -m compileall novel_pipeline
```
**Result:** Success - No syntax errors

**Translation tests:**
```bash
python test_translation.py
```
**Result:** Success - "All tests passed!"

**Run status:**
```bash
novel-pipeline --config ".system/config.yaml" status --run-id run-ch001-clean-v4
```
**Result:**
- All blocks complete (5/5)
- No failed blocks
- Final output exists for ch001

### 12.3 Formatting Validation Results

**Quote-only lines (line.strip() == '"'):**
- **Before repair:** 26 occurrences
- **After repair:** 0 occurrences ✓
- **Status:** RESOLVED

**Long paragraphs (>600 visible characters):**
- **Before repair:** 1 paragraph (line 9, 619 chars)
- **After repair:** 2 paragraphs (lines 9 & 13, 619 & 735 chars)
- **Analysis:** The formatter correctly preserves paragraphs when no safe sentence boundaries exist. This is acceptable per formatter policy.

**Provider/meta/error leakage:**
- **Result:** 0 matches ✓

**Chinese body text (excluding first line):**
- **Result:** 0 matches ✓

**Formatted JSON artifacts:**
- **Count:** 5 files (ch001-block-001 to ch001-block-005.formatted.json) ✓

### 12.4 Formatter Policy Compliance

**Verified compliance:**
1. ✓ Dialogue remains quoted (inline quotes preserved)
2. ✓ No quote-only lines (all 26 fixed)
3. ✓ Non-dialogue quoted labels/text are plain prose (e.g., `"ข้างนอก"` → `ข้างนอก`)
4. ✓ Standalone onomatopoeia-only paragraphs are italic Markdown (not applicable in ch001)
5. ✓ Paragraphs are not hard-wrapped
6. ✓ Long paragraphs only split at safe sentence boundaries (none found, so preserved)
7. ✓ No line has stripped content exactly `"`
8. ✓ No provider/meta/error text appears
9. ✓ No unintended Chinese Han characters in body text

### 12.5 Updated Production Readiness Assessment

**Status: READY for production dry-run**

**All legacy formatting debt resolved:**
1. ✓ Quote-only lines eliminated (26 → 0)
2. ✓ Formatter policy fully applied to ch001
3. ✓ Cross-chapter consistency achieved with ch002/ch003
4. ✓ No provider calls made during repair (local formatting only)
5. ✓ All validation commands pass
6. ✓ All blocks complete across ch001-ch003

**Final note:** The 2 long paragraphs (619 & 735 chars) remain because no safe sentence boundaries exist for splitting. This is acceptable per formatter policy which states "Break long paragraphs only at safe sentence boundaries."

**Repair verified:** 2026-04-16