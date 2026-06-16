# Batch Rollout Checklist

Use this checklist for every bounded Deep Sea Embers batch run. Fill in the placeholders before execution.

## Run Metadata

- Run ID: `<RUN_ID>`
- Novel: `Deep Sea Embers`
- Chapter range: `<CHAPTER_RANGE>`
- Source range verified through: `<SOURCE_RANGE>`
- Batch phase: `<SCAN_ONLY | GLOSSARY_APPROVAL | BOUNDED_TRANSLATION | FINAL_OUTPUT>`
- Operator: `<OPERATOR>`
- Worker model: `<WORKER_MODEL>`
- Date: `<DATE>`
- Related report files: `<REPORT_FILES>`

## Batch Size Decision Rule

- Default batch size is `5` chapters.
- Use the largest contiguous verified source range that still fits one operator review cycle and stays within provider/command limits.
- Never cross an unverified source boundary.
- If the verified source ends before the requested range, stop at the last verified chapter and do not speculate past it.
- If the batch is only for recovery, keep it to the smallest chapter/block slice needed to repair the failure.

## Scan-Only Gate

- [ ] Confirm the requested range is contiguous and inside verified source.
- [ ] Confirm the run is limited to glossary scan only.
- [ ] Confirm no translation, refinement, QA, or formatting is allowed yet.
- [ ] Confirm scan output files are written only for the requested range.
- [ ] Confirm no out-of-range chapter appears in the scan output.
- [ ] Confirm the worker report matches disk state.

## Glossary Approval Gate

- [ ] Review the scan/classification report.
- [ ] Separate approved terms, rejected terms, and unresolved terms.
- [ ] Get explicit operator approval for ambiguous terms before translation.
- [ ] Update only approved glossary notes.
- [ ] Confirm glossary approval records match the intended chapter blocks.
- [ ] Confirm no force-accept decision was made without approval.

## Bounded Translation Gate

- [ ] Confirm glossary approval is complete for the target range.
- [ ] Confirm the worker prompt names the exact allowed write set.
- [ ] Confirm the worker cannot process outside `<CHAPTER_RANGE>`.
- [ ] Confirm translation starts only after the scan and approval gates are closed.
- [ ] Confirm intermediate artifacts stay inside the bounded batch.
- [ ] Confirm any worker claim is treated as unverified until checked on disk.

## Final Output Gate

- [ ] Confirm final output files exist for every chapter in `<CHAPTER_RANGE>`.
- [ ] Confirm formatting validation passed.
- [ ] Confirm no provider text, meta text, or Chinese body text remains.
- [ ] Confirm no wrong glossary variants remain.
- [ ] Confirm no quote-only lines or lost dialogue marks remain.
- [ ] Confirm ledger/status evidence matches the final output files.

## Stop Conditions

Stop the batch immediately on any of the following:

- manual QA prompt
- `command_too_long`
- provider failure
- formatting validation failure
- missing or mismatched output artifacts
- any out-of-range processing
- any worker report that does not match disk evidence
- any request to force-accept without explicit approval

## Recovery Decision

- If the failure is `qa hard-fail`, inspect the narrowest artifact set first, repair only the smallest proven defect, and rerun from the failed stage.
- If the failure is `command_too_long`, shrink the batch or rerun a narrower recovery slice.
- If the failure is provider-related, retry only when the surrounding state is clean; otherwise stop and report.
- If the failure is formatting validation, repair formatting only and recheck cleanliness.
- If the failure involves out-of-range processing, stop and do not continue until the run scope is corrected.

## Final Signoff

- [ ] Range completed exactly as planned.
- [ ] All required files verified on disk.
- [ ] No forbidden scope drift occurred.
- [ ] All stop conditions were checked.
- [ ] Worker claims were verified before acceptance.
- [ ] Operator signoff complete.

## Explicit Reminders

- No out-of-range processing.
- No force-accept without approval.
- No trusting worker reports without verification.
- No silent scope expansion beyond `<CHAPTER_RANGE>`.
- No marking a batch complete until the disk state proves it.
