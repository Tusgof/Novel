# Quality gates

**What.** Two deterministic gates on real output: the output guardrails (`scripts/check_output_quality_guardrails.py`: forbidden terms and patterns, unapproved placeholders, paragraph density, malformed Markdown, leaked translation-metadata labels, Thai-numeral leakage) and Sentinel (`scripts/sentinel_quality_report.py`: blocker / major / minor / info findings for a novel and chapter scope).

**How the owner asks.** "รัน guardrails + Sentinel", or implicitly at the end of any translation, repair, or publication.

**Drive it.**
```
python scripts/sentinel_quality_report.py --novel deep-sea-embers --chapters ch211-ch215 --fail-on major --scope ch211-ch215
python scripts/check_output_quality_guardrails.py --help
```

**Verify.** Sentinel exits successfully at `--fail-on major` for the touched scope, and its report is saved; quote the blocker/major/minor/info counts in your report.

**Gotchas.**
- Always pass an explicit novel and chapter scope. Full-workspace scans are refused by the MoonRead gate unless deliberately allowed.
- A Sentinel blocker or major finding means stop and report, not re-run until green.
