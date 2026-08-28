# Batch Rollout Checklist

Use this checklist for every bounded Immortality System batch.

## Run Metadata

- Run ID: `<RUN_ID>`
- Novel: `Immortality System`
- Chapter range: `<CHAPTER_RANGE>`
- Source range verified through: `<SOURCE_RANGE>`
- Batch phase: `<SCAN_ONLY | GLOSSARY_APPROVAL | BOUNDED_TRANSLATION | FINAL_OUTPUT>`
- Operator: `<OPERATOR>`
- Worker model: `<WORKER_MODEL>`
- Date: `<DATE>`
- Related report files: `<REPORT_FILES>`

## Batch Size Decision Rule

- Default batch size is `5` chapters.
- Use the largest contiguous verified source range that fits one review cycle and provider limits.
- Never cross an unverified source boundary.
- Recovery batches stay at the smallest chapter/block slice needed.

## Scan-Only Gate

- [ ] Requested range is contiguous and inside verified source.
- [ ] Run is limited to glossary scan.
- [ ] No translation, refinement, QA, or formatting is allowed yet.
- [ ] Scan output is written only for the requested range.
- [ ] No out-of-range chapter appears in scan output.

## Glossary Approval Gate

- [ ] Scan/classification report reviewed.
- [ ] Approved, rejected, and unresolved terms are separated.
- [ ] Ambiguous terms have explicit operator approval.
- [ ] Only approved glossary notes are updated.
- [ ] Approval records match the intended range.

## Bounded Translation Gate

- [ ] Glossary approval is complete for the target range.
- [ ] Run ID and exact chapter range are recorded.
- [ ] Intermediate artifacts stay inside the bounded batch.
- [ ] Worker claims are checked against disk state.

## Final Output Gate

- [ ] Final output exists for every chapter in the range.
- [ ] Formatting validation passed.
- [ ] No provider/meta text or Chinese body text remains.
- [ ] Names, titles, and approved glossary terms are consistent.
- [ ] No quote-only lines, truncation, or missing source beats remain.
- [ ] Ledger/status matches the output files.

## Stop Conditions

Stop immediately on manual QA prompt, `command_too_long`, provider failure, formatting
validation failure, missing/mismatched artifacts, out-of-range processing, or a worker
report that conflicts with disk evidence. Never force-accept without explicit approval.

## Final Signoff

- [ ] Range completed exactly as planned.
- [ ] All files and gates verified on disk.
- [ ] No scope drift occurred.
- [ ] Research/incident report records any recovery and prevention.
