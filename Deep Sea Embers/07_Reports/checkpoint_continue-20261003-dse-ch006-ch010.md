# Checkpoint Report - CONTINUE-20261003-DSE-CH006-010

- Novel: deep-sea-embers
- Bounded run: lean-retranslate-20261003-dse-ch006-ch010
- Requested range: ch006-ch010
- Final run status: **complete**
- Promoted chapters: ch006, ch007, ch008, ch009, ch010
- Quarantined chapters: none

## Recovery

ch007 was quarantined after Sentinel found three dense paragraphs (Sentinel paragraphs 6, 14, and 18; lengths 1258, 1009, and 1030). I reflowed only those paragraphs at existing whitespace boundaries. The reconstructed text is identical to the pre-reflow wording; literal, refined, and QA checkpoints were not edited. The formatted checkpoint, staged Markdown, and formatted review hash were updated, then the same run ID was resumed.

## Gates

- Chapter QA: all five chapters passed.
- Deterministic paragraph guardrail: passed on staged and promoted output; maximum paragraph lengths were ch006=679, ch007=835, ch008=501, ch009=466, ch010=508.
- Blocking Sentinel: all five chapters reported 0 blocker / 0 major / 0 minor / 0 info.
- Atomic promotion: each promoted file is byte-identical to its staged file.
- Spot-check: title, opening, middle, ending, paragraph density, dialogue/thought formatting, and source-language leakage were checked for all five chapters; no CJK leakage or provider/meta placeholder text was found.

## Resume evidence

- Provider calls: 52 (literal_translation=29, refinement=7, qa_judge=10, term_harvest=6).
- Provider failures: 7, all recovered through configured fallback routes.
- ch007 reused literal, refinement, QA, and formatting checkpoints; only term harvest was regenerated after the formatted-hash update.
- No global provider exhaustion, manual prompt, force-accept, routing change, scope expansion, commit, push, or publish.

## Artifacts

- Run report: Deep Sea Embers/04_Work/_lean_runs/lean-retranslate-20261003-dse-ch006-ch010/lean_run_report.json
- Staged output: Deep Sea Embers/04_Work/_lean_runs/lean-retranslate-20261003-dse-ch006-ch010/_staged_output/
- Promoted output: Deep Sea Embers/05_Output/ch006/ through ch010/
- Final Sentinel evidence: 07_Reports/sentinel_quality_lean-lean-retranslate-20261003-dse-ch006-ch010_20261003_110510.{json,md}

## Prevention

Keep the whitespace-boundary paragraph-density repair as the run-local recovery step, and rerun staged guardrails and blocking Sentinel before resuming a quarantined chapter.
