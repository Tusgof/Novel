# Refinement Comparative QA: GPT‑5.4 and GPT‑5.4‑mini
**Date:** 2026‑04‑17  
**Reviewer:** Qwen Code  
**Benchmark artifacts:** `04_Work/_experiments/refinement_benchmark_gpt_20260417_132844`

## 1. Executive Summary

GPT‑5.4 successfully passed all hard‑failure checks and the ch004‑block‑002 omission trap, delivering faithful, tonally appropriate Thai prose. It is **acceptable as a Claude‑limit fallback** for refinement, provided the existing deterministic validation gates (no Chinese characters, glossary compliance, no wrong variants, no quote‑only lines) remain in place.

GPT‑5.4‑mini also passed all hard‑failure checks **except** the omission trap on ch004‑block‑002, where it omitted Duncan’s speechless reaction “……?”. This indicates a fidelity risk for subtle but important narrative details. GPT‑5.4‑mini is **not acceptable for production refinement** without additional QA safeguards that can detect such omissions.

The current production refined artifacts (Claude‑based, with manual repair on ch004‑block‑002) remain the quality baseline. Qwen DeepSeek Reasoner should **continue as the refinement fallback** for fidelity‑critical blocks, and its QA‑judge role should be retained to catch omission‑type errors.

**Recommended routing:**  
1. **Primary refinement:** Claude Sonnet (when quota available).  
2. **Claude‑limit fallback:** GPT‑5.4 (with deterministic validation + QA judge).  
3. **Secondary fallback:** Qwen DeepSeek Reasoner (already configured).  
4. **Do not route:** GPT‑5.4‑mini for refinement; reserve for non‑critical tasks.

## 2. Candidate Matrix

Scoring rubric (0–5):
- **Fidelity:** preserves all source meaning, no omissions/additions.
- **Thai prose quality:** natural, literary, polished Thai.
- **Tone:** dark nautical fantasy, restrained, eerie.
- **Glossary compliance:** approved terms used consistently.
- **Dialogue/narration handling:** dialogue remains dialogue; narration not over‑quoted.
- **Production risk:** likelihood of needing QA repair if used in live pipeline.

### ch004‑block‑002 (omission‑trap block)

| Candidate | Fidelity | Thai prose | Tone | Glossary | Dialogue | Production risk | Hard‑failure status |
|-----------|----------|------------|------|----------|----------|-----------------|-------------------|
| GPT‑5.4 | 5 | 4 | 5 | 5 | 5 | 2 | **PASS** |
| GPT‑5.4‑mini | 3 | 4 | 5 | 5 | 5 | 4 | **FAIL omission trap** (missing “……?”) |
| production_current_repaired | 5 | 5 | 5 | 5 | 5 | 1 | **PASS** |
| historical_claude | 1 | 4 | 5 | 5 | 5 | 5 | **FAIL omission trap** (missing “เงียบ”, “……?”) |

### ch005‑block‑003

| Candidate | Fidelity | Thai prose | Tone | Glossary | Dialogue | Production risk | Hard‑failure status |
|-----------|----------|------------|------|----------|----------|-----------------|-------------------|
| GPT‑5.4 | 5 | 4 | 5 | 5 | 5 | 2 | **PASS** |
| GPT‑5.4‑mini | 5 | 4 | 5 | 5 | 5 | 3 | **PASS** |
| production_current_repaired | 5 | 5 | 5 | 5 | 5 | 1 | **PASS** |
| historical_claude | 5 | 4 | 5 | 5 | 5 | 3 | **PASS** |

### ch006‑block‑001

| Candidate | Fidelity | Thai prose | Tone | Glossary | Dialogue | Production risk | Hard‑failure status |
|-----------|----------|------------|------|----------|----------|-----------------|-------------------|
| GPT‑5.4 | 5 | 4 | 5 | 5 | 5 | 2 | **PASS** |
| GPT‑5.4‑mini | 5 | 4 | 5 | 5 | 5 | 3 | **PASS** |
| production_current_repaired | 5 | 5 | 5 | 5 | 5 | 1 | **PASS** |
| historical_claude | 5 | 4 | 5 | 5 | 5 | 3 | **PASS** |

**Notes:**
- **Thai prose quality:** GPT‑5.4 and GPT‑5.4‑mini produce fluent, readable Thai but occasionally retain literal‑draft phrasing; Claude outputs are slightly more polished.
- **Production risk:** Lower numbers indicate lower risk (1 = already QA‑passed, 5 = high risk of needing repair).
- **Hard‑failure status:** All candidates passed the basic checks (no Chinese characters, no provider/meta text, all glossary terms present, no wrong variants, no quote‑only lines).

## 3. Hard Failure Summary

| Block | Candidate | Chinese chars | Provider/meta | Missing glossary | Wrong variants | Quote‑only lines | Omission trap |
|-------|-----------|---------------|---------------|------------------|----------------|------------------|---------------|
| ch004‑block‑002 | GPT‑5.4 | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| | GPT‑5.4‑mini | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ (missing “……?”) |
| | production_current_repaired | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| | historical_claude | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ (missing “เงียบ”, “……?”) |
| ch005‑block‑003 | All candidates | ❌ | ❌ | ❌ | ❌ | ❌ | – |
| ch006‑block‑001 | All candidates | ❌ | ❌ | ❌ | ❌ | ❌ | – |

**Legend:** ❌ = none detected; ✅ = passed; ❌ = failed.

## 4. Block‑by‑Block Findings

### ch004‑block‑002 (omission‑trap block)
**Ranking:**  
1. **production_current_repaired** – manually repaired Claude output, fully faithful, polished prose.  
2. **GPT‑5.4** – faithful, preserves all meaning including the speechless reaction; prose slightly less polished than Claude.  
3. **GPT‑5.4‑mini** – missing Duncan’s “……?” reaction; otherwise faithful. This omission is a tangible fidelity risk.  
4. **historical_claude** – omitted the entire middle section (goat‑head silence, “สู้ๆ! สู้ๆ! สู้ๆ!”, Duncan’s speechless reaction). Unacceptable for production.

**Key observation:** GPT‑5.4‑mini’s failure on the omission trap demonstrates that even a modern small model can drop subtle but narratively important details. This justifies retaining a QA‑judge step for any GPT‑based refinement.

### ch005‑block‑003
**Ranking:**  
1. **production_current_repaired** – polished, faithful, already QA‑passed.  
2. **GPT‑5.4** – faithful, clear prose, minor wording differences from Claude.  
3. **historical_claude** – faithful, slightly more literary phrasing.  
4. **GPT‑5.4‑mini** – faithful, comparable to GPT‑5.4 but with slightly more literal phrasing.

All candidates preserved the core meaning and glossary terms. No obvious omissions.

### ch006‑block‑001
**Ranking:**  
1. **production_current_repaired** – most polished, already QA‑passed.  
2. **GPT‑5.4** – faithful, clean prose.  
3. **historical_claude** – faithful, good tone.  
4. **GPT‑5.4‑mini** – faithful, acceptable prose.

Again, no fidelity issues detected. The main differences are stylistic.

## 5. Production Routing Recommendation

### GPT‑5.4 as Claude‑limit fallback
**Acceptable: Yes, conditional.**  
- GPT‑5.4 passed all hard‑failure checks and the omission trap.  
- Its prose is fluent and tonally appropriate for dark nautical fantasy.  
- **Condition:** Must retain the existing deterministic validation gates (Chinese‑character check, glossary compliance, wrong‑variant detection, quote‑only line detection) and the QA‑judge step (currently Qwen DeepSeek Reasoner) to catch any subtle omissions that might slip through.

### GPT‑5.4‑mini as refinement candidate
**Acceptable: No.**  
- Failed the omission trap on ch004‑block‑002 (missing “……?”).  
- While it passed all other hard checks, this single omission demonstrates a fidelity risk that cannot be ignored for production refinement.  
- **Alternative use:** Could be considered for low‑risk tasks (e.g., term‑suggestion, non‑critical formatting) where omission of subtle markers is not critical, but refinement is not recommended.

### Qwen DeepSeek Reasoner role
- **Remain as fallback for refinement** (already configured as second fallback after Claude).  
- **Continue as QA judge** – its ability to detect omission‑type errors has been validated (it caught Claude’s omissions in ch004‑block‑002).  
- Consider making Qwen the **primary refinement fallback** for fidelity‑critical blocks if GPT‑5.4 shows any further issues in larger‑scale testing.

### Claude‑limit handling
- When Claude quota is exhausted, the pipeline should **fall back to GPT‑5.4**, not silently switch to Claude for literal translation or QA.  
- The provider‑routing policy (`.system/providers.yaml`) should be updated to include GPT‑5.4 as a refinement provider with appropriate retry/cooldown settings.

## 6. Risks and Required Gates

### Remaining risks
1. **Subtle omission risk:** Even GPT‑5.4 could potentially omit small narrative details in other blocks; the omission trap only tests one known pattern.  
2. **Provider quota/capacity:** GPT‑5.4 may also encounter capacity errors; the pipeline must wait/resume rather than silently falling back to Claude for refinement.  
3. **Style drift:** GPT‑5.4’s prose may occasionally drift toward a more neutral tone; the QA judge should flag tone inconsistencies.

### Required validation gates (must remain)
1. **Deterministic validation** (already implemented):
   - No Chinese Han characters in output.
   - No provider/meta/error text.
   - All required glossary terms present.
   - No wrong glossary variants (e.g., “เอบนอร์มัล”).
   - No quote‑only lines.
2. **QA‑judge step** (Qwen DeepSeek Reasoner):
   - Must continue to evaluate fidelity, tone, and completeness.
   - Should be configured to flag missing reactions, omitted dialogue markers, etc.
3. **Manual QA spot‑check** (for first few blocks of any new batch):
   - Human review of GPT‑5.4 outputs before full‑batch commitment.

## 7. Final Decision Needed From Codex/User

1. **Approve GPT‑5.4 as Claude‑limit fallback for refinement?**  
   - If yes, update `.system/providers.yaml` refinement routing to include `gpt-5.4` as a fallback after `claude_sonnet` and before `qwen_deepseek-reasoner`.  
   - Ensure the pipeline’s retry/cooldown logic respects GPT‑5.4 capacity errors (wait/resume, no silent Claude fallback).

2. **Reject GPT‑5.4‑mini for refinement?**  
   - If yes, leave it out of the production routing table; reserve for experimental or non‑critical tasks.

3. **Retain Qwen DeepSeek Reasoner as QA judge and secondary fallback?**  
   - No configuration change needed; confirm existing setup remains.

4. **Any additional validation gates to add?**  
   - Consider adding a regex‑based check for known omission patterns (e.g., “……?” presence when certain keywords appear). This can be implemented as a deterministic post‑refinement check.

---

**Confirmation:** During this review, no production files (`06_Logs/run_ledger.jsonl`, `04_Work/ch*/` artifacts, `05_Output/`, `01_Glossary/`) were modified, and no live provider calls (Gemini, Claude, Qwen, Codex CLI) were made. All checks were read‑only and deterministic.