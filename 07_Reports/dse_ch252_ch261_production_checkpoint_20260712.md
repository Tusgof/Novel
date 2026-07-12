# DSE Production Checkpoint: ch252-ch261

Date: 2026-07-12

## Scope And Outcome

- Novel: Deep Sea Embers
- Run: `dse-ch252-ch261-v1`
- Scope: `ch252-ch261`
- Blocks: 58/58 complete
- Current failed blocks: none
- Historical failed records: none
- Scope expansion: none

## Glossary Gate

- Scan candidate count: 24
- Approved terms: 寒霜城邦, 现实维度, 蕾·诺拉, 寒霜海军, 一千米事件, 四号潜水器, 五号潜水器, 守墓人, 教堂舰
- Rejected candidates: generic terms, fragments, and title-only phrases as documented in `Deep Sea Embers/07_Reports/glossary_approval_decisions_dse-ch252-ch261-v1.md`.

## Recovery And Provider Evidence

- QA completed through DeepSeek V4 Flash: 29 blocks; V4 Pro fallback: 15 blocks; Gemini Flash fallback: 14 blocks.
- QA initiated 9 refinement retries. `ch260-block-001` removed approved term `教皇 -> พระสันตะปาปา` during refinement; the pipeline recovered the literal-safe term and QA passed without force-accept.
- AI formatting completed normally with DeepSeek V4 Flash or Gemini Flash on most blocks. Three blocks used deterministic local fallback after provider output was empty or failed content-preservation validation, including `ch254-block-004` and `ch259-block-004`.
- Local fallback is a recoverable incident only because the validator rejected unsafe AI output and preserved verified refined content. It is not evidence that the AI formatter is fully reliable.

## Verification

- `python -m compileall novel_pipeline`: passed
- `python test_translation.py` with `PYTHONIOENCODING=utf-8`: passed
- `python scripts/check_output_quality_guardrails.py --novel deep-sea-embers --chapters ch252-ch261`: passed
- Scoped Sentinel: `07_Reports/sentinel_quality_dse-ch252-ch261-final_20260712_161905.md`, blocker/major/minor/info `0/0/0/0`
- Spot-check: `ch252`, `ch254`, `ch256`, `ch259`, `ch261`; titles, opening/middle/ending, dialogue, glossary usage, Chinese leakage, and paragraph density passed.

## Publication Gate

- MoonRead reader scope updated through `ch261`.
- Publication verification and git push are the remaining steps for this checkpoint.
