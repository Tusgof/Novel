# Recovery Report: ch009-block-003 & ch009-block-004
Date: 2026-04-18

## 1. Preflight Status Summary
- Run ID: `batch-ch009-ch018-v1`
- Status before recovery:
  - Completed blocks: ch009-block-001, ch009-block-002
  - Failed blocks: ch009-block-003, ch009-block-004
  - Pending blocks: ch009-block-005, ch009-block-006
  - Chapters ch010–ch013: 0 blocks processed (pending translating)
  - Chapters ch014–ch018: 0 blocks processed (guardrail respected)
- Provider usage (historical): Claude refining failures with Windows error 3221225786; Codex fallback triggered but no successful records.

## 2. Codex GPT‑5.4 Smoke Test
- Command: `"Reply OK only" | codex exec -m gpt-5.4 --skip-git-repo-check --cd "D:\Fogust\Workspace\Novel\Deep Sea Embers" --sandbox read-only -`
- Result: **OK** (exit code 0, output "OK")
- Duration: ~2 seconds
- Conclusion: Codex CLI is functional and can reach GPT‑5.4.

## 3. Recovery Method
- Created temporary Python script `recovery_single.py` that:
  1. Loads config from `.system/config.yaml`
  2. Overrides `stage_routing["refinement"]` **in memory only**:
     - `provider = "codex"`
     - `model = "gpt-5.4"`
     - `fallback_provider = "qwen"`
     - `fallback_model = "deepseek-reasoner"`
     - `fallbacks = ({"provider": "qwen", "model": "deepseek-reasoner"},)`
     - All other routing parameters (timeout, retry, scan budgets) copied from original.
  3. Calls `rerun_block_pipeline` with:
     - `run_id = "batch-ch009-ch018-v1"`
     - `block_id = "ch009-block-003"` (then `ch009-block-004`)
     - `from_stage = "refine"`
- **No changes** were made to `.system/providers.yaml` or any production source code.
- **No calls to Claude** were made during recovery.
- Temporary scripts were deleted after execution.

## 4. ch009-block-003 Outcome
- **Refinement provider**: `codex` (model `gpt-5.4`)
- **QA provider**: `qwen` (model `deepseek-reasoner`)
- **Formatting provider**: `local`
- **Ledger records added**:
  - `2026-04-18T09:46:25.338369+00:00` – refining completed (provider=codex)
  - `2026-04-18T09:47:00.380195+00:00` – qa completed (provider=qwen)
  - `2026-04-18T09:47:00.401517+00:00` – formatting completed (provider=local)
  - `2026-04-18T09:47:00.418058+00:00` – block completed (provider=local)
- **QA result**: PASSED (retry 0)
- **Formatted artifact**: `04_Work/ch009/ch009-block-003.formatted.json`
- **Cleanliness checks**:
  - No provider/meta/error text (quota, 429, Provider, Traceback, etc.)
  - No Chinese Han characters in formatted Thai prose
  - No wrong glossary variants (`ดันแคน เอบนอร์มัล`, `แอบนอร์มัล`, etc.)
  - No quote‑only lines (stripped content `"`)

## 5. ch009-block-004 Outcome
- **Refinement provider**: `codex` (model `gpt-5.4`)
- **QA provider**: `qwen` (model `deepseek-reasoner`)
- **Formatting provider**: `local`
- **Ledger records added**:
  - `2026‑04‑18T09:48:17.372968+00:00` – refining completed (provider=codex)
  - `2026‑04‑18T09:48:42.376923+00:00` – qa completed (provider=qwen)
  - `2026‑04‑18T09:48:42.397398+00:00` – formatting completed (provider=local)
  - `2026‑04‑18T09:48:42.414207+00:00` – block completed (provider=local)
- **QA result**: PASSED (retry 0)
- **Formatted artifact**: `04_Work/ch009/ch009-block-004.formatted.json`
- **Cleanliness checks**:
  - All checks passed (same as block‑003).

## 6. Provider Records Summary
- **Provider=codex records appeared in ledger**: **YES** (2 completed refining records)
- **Qwen refinement fallback used after Codex**: **NO** (Codex succeeded, fallback not triggered)
- **Claude used**: **NO** (routing overridden)
- **Gemini used**: unchanged (literal translation already completed)
- **Qwen used for QA**: **YES** (2 new QA records)

## 7. Current Status After Recovery
- Run `batch‑ch009‑ch018‑v1` status:
  - Completed blocks: ch009‑block‑001, ‑002, ‑003, ‑004
  - Failed blocks: **none**
  - Pending blocks: ch009‑block‑005, ‑006 (translating)
  - Chapters ch010–ch013: 0 blocks processed (still pending translating)
  - Chapters ch014–ch018: 0 blocks processed (guardrail intact)
- Provider usage now includes:
  - `codex`: refining completed: 2
  - `qwen`: qa completed: 4
  - `claude`: refining completed: 4, failed: 3 (historical)
  - `gemini`: translating completed: 5
  - `local`: formatting completed: 4, etc.

## 8. Guardrail Result for ch010–ch018 and ch014–ch018
- **ch010–ch013**: No translation/refinement/QA/formatting records added. All blocks remain pending translating.
- **ch014–ch018**: No translation/refinement/QA/formatting records added. All blocks remain pending translating.
- **No final output** for ch009 (`05_Output/ch009/ch009.md` does not exist) because blocks 005–006 are still pending.

## 9. Files Changed
- **Created**:
  - `04_Work/ch009/ch009-block-003.refined.json` (updated)
  - `04_Work/ch009/ch009-block-003.qa.json` (updated)
  - `04_Work/ch009/ch009-block-003.formatted.json` (updated)
  - `04_Work/ch009/ch009-block-004.refined.json` (updated)
  - `04_Work/ch009/ch009-block-004.qa.json` (updated)
  - `04_Work/ch009/ch009-block-004.formatted.json` (updated)
- **Appended**:
  - `06_Logs/run_ledger.jsonl` (8 new records: 2 codex refining, 2 qwen QA, 2 local formatting, 2 local completed)
- **Temporary scripts** (deleted after use):
  - `temp_recovery.py`
  - `recovery_single.py`
  - `validate_recovery.py`
- **Report file**:
  - `07_Reports/ch009_failed_block_recovery_gpt54.md` (this file)

## 10. Commands Run
```powershell
# Preflight status
python -m novel_pipeline.cli --config ".system/config.yaml" status --run-id batch-ch009-ch018-v1

# Codex smoke test
$env:PYTHONIOENCODING='utf-8'
"Reply OK only" | codex exec -m gpt-5.4 --skip-git-repo-check --cd "D:\Fogust\Workspace\Novel\Deep Sea Embers" --sandbox read-only -

# Recovery block 003
python recovery_single.py ch009-block-003

# Recovery block 004
python recovery_single.py ch009-block-004

# Validation
python -m compileall novel_pipeline
python test_translation.py
python validate_recovery.py
```

## 11. Blocker Requiring Codex/User Review
- **Claude instability** remains a production risk. The Windows error `3221225786` (access violation) appears during refinement retries after QA failures. The pipeline correctly triggers the configured fallback chain (Claude → Codex → Qwen), but the previous run suggests the Codex fallback may have been killed by an outer timeout before committing a ledger record.
- **This recovery proves** that GPT‑5.4 can successfully replace Claude for refinement (both blocks passed QA on first attempt). Consider adjusting the default refinement routing to use GPT‑5.4 as primary when Claude exhibits repeated crashes, or increase the timeout for fallback providers.
- **Next steps**: Continue V3.8 Phase 3 (ch009‑ch013) by processing remaining blocks ch009‑block‑005 and ‑006, then proceed to ch010‑ch013. Monitor provider stability; if Claude crashes again, consider a temporary routing override for the remainder of the batch.

---
**Recovery completed successfully. Both failed blocks now have clean, QA‑passed formatted artifacts.**