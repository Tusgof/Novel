# Recovery Report: ch009‑block‑006 QA Fallback Failure

**Recovery timestamp:** 2026‑04‑18 (executed after the previous Gemini command_too_long failure)  
**Run ID:** `batch‑ch009‑ch018‑v1`  
**Block ID:** `ch009‑block‑006`  
**Scope:** QA‑stage recovery only; translation and refinement left untouched.

---

## 1. Pre‑check status summary for ch009‑block‑006

| Artifact | Presence | Status |
|----------|----------|--------|
| `literal.json` | ✓ | Committed (Gemini) |
| `refined.json` | ✓ | Committed (Claude) – latest version after QA‑triggered re‑refinement |
| `qa.json` | ✓ | `passed: false` – previous QA failure (Qwen primary → Gemini fallback) |
| `formatted.json` | ✗ | Missing |
| Chapter output `ch009.md` | ✗ | Missing (only 5 of 6 blocks complete) |

**Block progression:**  
- `ch009‑block‑001` … `‑005` → **completed** (all artifacts present)  
- `ch009‑block‑006` → **failed** at QA stage; fallback chain (Qwen → Gemini) failed with `command_too_long`.

**Ledger record of the failure:**
```json
{
  "block_id": "ch009-block-006",
  "created_at": "2026-04-18T11:04:32.411154+00:00",
  "input_hash": "",
  "metadata": {
    "duration_seconds": 0.287004,
    "error_type": "ProviderOutputError",
    "message": "Provider 'gemini' returned unusable output (command_too_long). The command line is too long.",
    "model": "pro",
    "provider": "gemini",
    "returncode": 1,
    "stderr_preview": "The command line is too long.",
    "stdout_preview": ""
  },
  "output_hash": "",
  "provider": "qwen",
  "run_id": "batch-ch009-ch018-v1",
  "stage": "qa",
  "status": "failed"
}
```

---

## 2. Recovery command used

```powershell
$env:PYTHONIOENCODING='utf-8'
python -m novel_pipeline.cli --config ".system/config.yaml" rerun-block \
  --run-id batch-ch009-ch018-v1 \
  --block-id ch009-block-006 \
  --from-stage qa
```

**Timeout:** 600 000 ms (10 minutes) – sufficient for Qwen QA and local formatting.

---

## 3. Recovery method

**Normal QA rerun succeeded** – no in‑memory fallback modification was required.

The pipeline’s configured routing (`providers.yaml`) was used as‑is:
- Primary QA provider: `qwen` (model `deepseek‑reasoner`)
- Fallback provider: `gemini` (model `pro`)

The rerun triggered only the primary Qwen QA; the fallback was **not** invoked because Qwen completed successfully. No temporary script to disable the Gemini fallback was needed.

---

## 4. QA result and exact feedback

**QA passed** – `04_Work/ch009/ch009‑block‑006.qa.json` updated:

```json
{
  "block_id": "ch009-block-006",
  "chapter_id": "ch009",
  "feedback": "PASS: No omissions or additions; meaning accurately preserved; glossary terms correctly applied (เรือผู้ไร้บ้าน, หัวแพะ, ทะเลไร้ขอบเขต, ตุ๊กตา, มิติวิญญาณ, ดันแคน); tone appropriate for nautical dark fantasy; refined text improves phrasing slightly without altering core meaning.",
  "findings": [],
  "judge_provider": "qwen",
  "metadata": {},
  "passed": true,
  "retry_count": 0
}
```

**Judge provider:** `qwen` (primary). No fallback used.

---

## 5. Formatting result

**Formatting completed** – `04_Work/ch009/ch009‑block‑006.formatted.json` created.  
**Local provider** executed formatting stage, producing the final Thai text block.

---

## 6. Chapter output assembly

**`05_Output/ch009/ch009.md` created** – the pipeline detected that all six formatted blocks are now present and assembled the final chapter Markdown.

---

## 7. Cleanliness checks for ch009‑block‑006 and ch009.md

| Check | Result | Notes |
|-------|--------|-------|
| Provider/meta/error text | **Pass** | No `quota`, `rate limit`, `429`, `capacity`, `Provider`, `Traceback`, `Exception`, `stderr`, `stdout`, `Gemini`, `Claude`, `Qwen`, `Codex` in `formatted.json` or `ch009.md`. |
| Chinese Han characters in Thai body text | **Pass** | Only the chapter‑title line (`# 第九章 …`) contains Chinese characters; all body text is Thai. |
| Wrong glossary variants | **Pass** | No occurrences of `ดันแคน เอบนอร์มัล`, `ดันแคน แอบนอร์มัล`, `เอบนอร์มัล`, `แอบนอร์มัล`. Approved term `แอบโนมาร์` not present in this chapter. |
| Quote‑only lines (stripped = `\"`) | **Pass** | No lines consist solely of a double‑quote character. |
| Mojibake / wrong‑script output | **Pass** | All Thai characters are valid Thai script; no Chinese, Japanese, or Korean characters in the body. |

---

## 8. Provider routing audit for this recovery

- **Primary QA provider:** `qwen` (model `deepseek‑reasoner`) – **used successfully**.
- **Fallback QA provider:** `gemini` (model `pro`) – **not invoked**.
- **Refinement provider:** unchanged (`claude` → `codex` fallback chain) – **not re‑run**.
- **Translation provider:** unchanged (`gemini`) – **not re‑run**.

**Config modifications:** None. `.system/providers.yaml` remains unchanged.

---

## 9. Guardrail result for ch010‑ch018

| Guardrail | Status |
|-----------|--------|
| No new `04_Work/ch010/` … `ch018/` directories | **Pass** – only `ch009` exists under `04_Work/`. |
| No new artifacts for ch010‑ch018 | **Pass** – no `literal.json`, `refined.json`, `qa.json`, `formatted.json` created. |
| No new `05_Output/ch010/` … `ch018/` directories | **Pass** – only `ch001`–`ch009` present. |
| No ledger records for ch010‑ch018 after recovery | **Pass** – the three new ledger entries are all for `ch009‑block‑006`. |

**Conclusion:** ch010‑ch018 remain untouched; the recovery was strictly bounded to ch009‑block‑006.

---

## 10. Files changed

| Path | Change |
|------|--------|
| `04_Work/ch009/ch009‑block‑006.qa.json` | Updated (`passed: true`, new feedback) |
| `04_Work/ch009/ch009‑block‑006.formatted.json` | Created |
| `05_Output/ch009/ch009.md` | Created (full chapter assembly) |
| `06_Logs/run_ledger.jsonl` | Appended three records:<br>• `qa` (qwen, completed)<br>• `formatting` (local, completed)<br>• `completed` (local, completed) |
| `07_Reports/ch009_block_006_qa_recovery.md` | This report. |

**No modifications to:** `.system/providers.yaml`, source code, glossary notes, glossary scan artifacts, or any other block’s artifacts.

---

## 11. Commands run

1. Status pre‑check:
   ```powershell
   novel‑pipeline --config '.system/config.yaml' status --run‑id batch‑ch009‑ch018‑v1
   ```
2. Recovery command (as shown in section 2).

No additional commands were executed.

---

## 12. Remaining blocker requiring Codex/user review

**None.** The recovery succeeded without requiring manual artifact editing, config changes, or fallback‑chain overrides. The pipeline’s normal rerun‑block mechanism worked as intended, and ch009 is now complete.

**Next step (if continuing V3.8 Phase 3):** Proceed to translation of ch010‑ch013 using the same normal routing (Claude primary → Codex fallback → Qwen fallback). The Gemini command‑length limitation for QA fallback remains a known risk; should a future QA fallback again hit `command_too_long`, a similar bounded recovery can be applied.