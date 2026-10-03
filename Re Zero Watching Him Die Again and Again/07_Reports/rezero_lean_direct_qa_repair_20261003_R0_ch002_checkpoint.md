# Re:Zero Lean Direct QA Repair Checkpoint

Date: 2026-10-03  
Order: `LEAN-DIRECT-QA-REPAIR-20261003-R0-CH002`  
Run: `LEAN-RETRANSLATE-20261003-R0`  
Scope: `ch001-ch002`  
Pipeline: Lean production  
Machine report: `04_Work/_lean_runs/LEAN-RETRANSLATE-20261003-R0/lean_run_report.json`  
QA checkpoint: `04_Work/_lean_runs/LEAN-RETRANSLATE-20261003-R0/ch002/qa_checkpoint.json`

## Direct repair

The repaired artifact was:

`04_Work/_lean_runs/LEAN-RETRANSLATE-20261003-R0/ch002/refined_checkpoint.json`

Exactly one occurrence of each source-character leakage span was replaced in the refined checkpoint, without rerunning the whole refinement:

- `是她` -> `เธอ`
- `当她` -> `เธอ`
- `帮她` -> `เธอ`

Post-repair verification found zero occurrences of all three source spans. The bounded run was resumed from the affected QA gate. No force-accept was used.

## Resume result

- Run status: `blocked`.
- `ch001` reused its valid checkpoints and remained QA-passed through staged formatting.
- `ch002` reused literal translation and refinement, then failed assembled QA.
- Promoted outputs: none.
- Existing reader output was not promoted or published.

The new hard QA failure is separate from the repaired three-span leakage:

- The Subaru–Old Man Rom conversation is missing a contiguous dialogue/content section, including the discussion of dying, the silver-haired girl, and the insignia.
- The refined Thai contains stray untranslated placeholder tokens `base` and `presource`.

QA used the configured fallback after the primary reasoning route returned an unusable empty response. Run metrics are 31 provider calls, 3 provider failures, and 2,462.111 provider seconds.

## Gate status

- Title/source readiness: available for the requested bounded range.
- QA pass: **failed** at `ch002` assembled QA; this is the stop condition.
- Deterministic output guardrails: not reached after the hard QA stop.
- Blocking Sentinel: not reached.
- Inspector spot-check: not reached.
- Checkpoint report: written here.

No routing change, force-accept, scope expansion, publication, commit, or push was performed. The next action requires a separate recovery decision for the new omission and placeholder leakage; this order must remain stopped at the QA hard fail.
