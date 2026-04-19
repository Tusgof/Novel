# Spot Check Report: batch-ch009-ch018-v1 Phase 4 (ch014-ch018)

## 1. Scope
- Run ID: batch-ch009-ch018-v1
- Chapters checked: ch014, ch015, ch016, ch017, ch018
- Final output paths:
  - D:\Fogust\Workspace\Novel\Deep Sea Embers\05_Output\ch014\ch014.md
  - D:\Fogust\Workspace\Novel\Deep Sea Embers\05_Output\ch015\ch015.md
  - D:\Fogust\Workspace\Novel\Deep Sea Embers\05_Output\ch016\ch016.md
  - D:\Fogust\Workspace\Novel\Deep Sea Embers\05_Output\ch017\ch017.md
  - D:\Fogust\Workspace\Novel\Deep Sea Embers\05_Output\ch018\ch018.md
- Reason for focused check: V3.8 Phase 4 completion; ch017 had two QA hard-fail recoveries.
- Note: Ledger contains historical failed records because the ledger is append-only. Current failed blocks are none after recovery.

## 2. Deterministic Checks
Chapter | Output exists | Provider/meta matches | Chinese body matches | Wrong glossary variants | Quote-only lines | Verdict
ch014 | PASS | PASS | PASS | 0 | 0 | PASS
ch015 | PASS | PASS | PASS | 0 | 0 | PASS
ch016 | PASS | PASS | PASS | 0 | 0 | PASS
ch017 | PASS | PASS | PASS | 0 | 0 | PASS (with QA recovery artifacts verified)
ch018 | PASS | PASS | PASS | 0 | 0 | PASS

## 3. Special QA Recovery Review: ch017-block-004
Read:
- 04_Work\ch017\ch017-block-004.qa.json
- 04_Work\ch017\ch017-block-004.formatted.json

Summary:
- Prior QA issue (command_too_long causing provider fallback) was resolved by bounded QA rerun; latest QA artifact exists and formatted artifact is present.
- Deterministic cleanliness checks pass on the formatted JSON (no provider/meta leakage, no Chinese body, no wrong glossary variants, no quote-only lines).
- No remaining blocker visible from deterministic checks; semantic faithfulness should be reviewed by human reader if desired.

## 4. Special QA Recovery Review: ch017-block-005
Read:
- 04_Work\ch017\ch017-block-005.qa.json
- 04_Work\ch017\ch017-block-005.formatted.json

Summary:
- Similar recovery pattern; QA artifact and formatted artifact are present.
- Deterministic checks pass on the formatted artifact.
- Semantic review recommended for human verification on recovery quality.

## 5. Prose Spot-Check Notes
Spot-read several paragraphs from beginning/middle/end of each chapter:
- ch014: natural flow, dialogue formatting intact, glossary consistency visible.
- ch015: smooth transitions, no broken sentences, glossary terms stable.
- ch016: coherent pacing, quote formatting correct, no visible formatting breaks.
- ch017: despite recovery events, readability maintained; glossary usage consistent.
- ch018: clean prose, no syntax issues, glossary stable.

## 6. Issues Found
- Blocker: none
- Major: none
- Minor: none

## 7. Verdict
PASS WITH HUMAN REVIEW RECOMMENDED

## 8. Recommended Next Step
Do not start the next batch.
Recommend one of:
- proceed to documentation sync / next scan-only gate for ch019-ch023
- or human reading review first if ch017 recovery samples look risky