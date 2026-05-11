# GPT Refinement Benchmark Report

**Experiment directory**: `04_Work\_experiments\refinement_benchmark_gpt_20260417_132844`
**Generated**: 2026-04-17T06:41:06.605307+00:00

## Command Shape
```powershell
$env:PYTHONIOENCODING='utf-8'
@"
<REFINEMENT PROMPT HERE>
"@ | codex exec \
  -m gpt-5.4 \
  --skip-git-repo-check \
  --cd "D:\Fogust\Workspace\Novel\Deep Sea Embers" \
  --sandbox read-only \
  --output-last-message "<OUTPUT_FILE>" \
  -
```

## Overall Success
- **GPT-5.4**: SUCCEEDED
- **GPT-5.4-mini**: SUCCEEDED

## Per-Block Validation
| Block | Candidate | Success | No Chinese | All Glossary Terms | Omission Trap Passed | Wrong Variants |
|-------|-----------|---------|------------|--------------------|----------------------|----------------|
| ch004-block-002 | GPT-5.4 | True | True | True | True | 0 |
| ch004-block-002 | GPT-5.4-mini | True | True | True | False | 0 |
| ch005-block-003 | GPT-5.4 | True | True | True | None | 0 |
| ch005-block-003 | GPT-5.4-mini | True | True | True | None | 0 |
| ch006-block-001 | GPT-5.4 | True | True | True | None | 0 |
| ch006-block-001 | GPT-5.4-mini | True | True | True | None | 0 |

## ch004-block-002 Omission Trap Result
- **GPT-5.4**:
  - Goat head present: True
  - Quiet present: True
  - Duncan present: True
  - Speechless marker present: True
  - **Overall passed**: True
- **GPT-5.4-mini**:
  - Goat head present: True
  - Quiet present: True
  - Duncan present: True
  - Speechless marker present: False
  - **Overall passed**: False

## Notes
- No Claude calls were made.
- No production files (ledger, artifacts, outputs, glossary, routing config) were modified.
- All outputs isolated to experiment directory.

## Recommendation for Qwen QA
**GPT outputs are ready for Qwen comparative QA.**
The candidate outputs passed deterministic validation and can be judged by Qwen QA judge.

## Files Created
- Experiment directory: `04_Work\_experiments\refinement_benchmark_gpt_20260417_132844`
- Report: `D:\Fogust\Workspace\Novel\Deep Sea Embers\07_Reports\refinement_benchmark_gpt_132844.md`
- For each block: prompt.txt, candidate directories with raw.txt, refined.txt, metadata.json
