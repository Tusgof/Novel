# OHKS Lean Recovery

- Order: LEAN-RECOVERY-20261003-OHKS
- Run: ohks-lean-retranslate-20261003-ch001-ch005
- Affected chapter: ch003
- Cause: the prior refinement checkpoint was truncated at [Soul of; the literal checkpoint covered the full 13,210-character source and reached the final sentence.
- Recovery: removed only the stale ch003/refined_checkpoint.json and ch003/qa_checkpoint.json, reused the valid literal checkpoint, and resumed the same bounded run. No manual output patch or force-accept was used.
- Prevention: treat refinement truncation as a refinement-stage invalidation; rerun from that stage and require QA plus Sentinel before promotion.
- Verification: ch001–ch005 status complete; all five QA checks passed; deterministic stage checks found no missing headings, truncation markers, QA metadata leakage, or runaway repeats; Sentinel reported 0 blocker, 0 major, 0 minor, and 0 info findings; five outputs were promoted.
