# Quality gates

**What.** Two deterministic gates on real output: the output guardrails (`scripts/check_output_quality_guardrails.py`: forbidden terms and patterns, unapproved placeholders, paragraph density, malformed Markdown, leaked translation-metadata labels, Thai-numeral leakage) and Sentinel (`scripts/sentinel_quality_report.py`: blocker / major / minor / info findings for a novel and chapter scope).

**How the owner asks.** "รัน guardrails + Sentinel", or implicitly at the end of any translation, repair, or publication.

**Drive it.**
```
python scripts/sentinel_quality_report.py --novel deep-sea-embers --chapters ch211-ch215 --fail-on major --scope ch211-ch215
python scripts/check_output_quality_guardrails.py --help
```

**Verify.** Sentinel exits successfully at `--fail-on major` for the touched scope,
and its report is saved under `07_Reports/generated/<UTC month>/`. Quote counts
AND source-coverage status. The report's semantic-fidelity limit remains explicit;
green glossary/format checks are not a semantic-quality certificate.
The JSON separates `checked_invariants_passed` from `safe_to_publish`: the latter
is false on blocked input and unknown (`null`) on green checks, never a release approval.

**Gotchas.**
- Always pass an explicit novel and chapter scope. Full-workspace scans are refused by the MoonRead gate unless deliberately allowed.
- A Sentinel blocker or major finding means stop and report, not re-run until green.
- Missing/unreadable source blocks source-backed acceptance rather than silently
  reporting zero semantic findings. Chinese approved terms participate in coverage;
  rejected variants remain blockers even if the canonical Thai also appears.
- Inspect reader-discovered escapes with [governance-health.md](governance-health.md).
