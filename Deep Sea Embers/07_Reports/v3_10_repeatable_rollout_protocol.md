# V3.10 Repeatable Rollout Protocol

Date: 2026-04-24
Scope: Deep Sea Embers operator protocol for repeatable bounded batch handoff.

## Purpose

V3.10 exists to make one bounded batch handoff repeatable without rewriting the process each time. The deliverable is not a new translation batch. The deliverable is a practical operator protocol, a reusable checklist, and a reusable worker prompt.

## Lessons Carried Forward From V3.7-V3.9

- Bounded batches are manageable when the range is explicit and the stop conditions are explicit.
- Scan-only and glossary approval must stay separate from translation.
- Worker reports are claims until disk state proves them.
- `command_too_long` needs a stop-and-shrink response, not a silent policy change.
- QA hard-fail needs a recovery fork, not force-accept.
- Final output must be validated before the batch is declared complete.
- The current Deep Sea Embers source in this workspace exists only through `ch023`.

## Standard Batch Size Decision Rule

- Default batch size is `5` contiguous chapters.
- Prefer the smallest contiguous range that keeps one scan, one approval step, one translation window, and one final verification cycle inside a single operator session.
- Never cross an unverified source boundary.
- Never expand the batch because a worker says the rest is available.
- If the source range is not verified beyond `ch023`, do not plan any `ch024+` work.

## Standard Gates

### 1. Scan-Only Gate

Run glossary scan only for the exact range. Stop after scan output exists and before translation starts.

### 2. Glossary Approval Gate

Review the scan/classification output, decide ambiguous terms, and approve only the terms that are explicitly accepted. Do not force-accept unresolved terms.

### 3. Bounded Translation Gate

Run the worker with an exact range, exact allowed write set, and exact stop conditions. The worker may only process the assigned batch.

### 4. Final Output Gate

Check final chapter files, formatting validation, and cleanliness before declaring the run complete.

## Standard Stop Conditions

Stop immediately on:

- manual QA prompt
- `command_too_long`
- provider failure
- formatting validation failure
- missing expected output artifacts
- any out-of-range processing
- any mismatch between worker report and disk evidence
- any request to force-accept without explicit approval

## Standard Recovery Fork

### QA Hard-Fail

Inspect the narrowest artifact set first, identify the exact omission or drift, repair only the smallest proven defect, then rerun from the failed stage. Do not force-accept.

### `command_too_long`

Shrink the scope or switch to a narrower recovery slice. Do not silently change providers or widen the batch.

### Provider Failure

Retry only if the surrounding state is clean. If the failure repeats, stop and report for operator review.

### Formatting Validation Failure

Repair formatting only, then recheck the output cleanliness. Do not widen the fix beyond the proven defect.

## Exact Recommendation For The Current Deep Sea Embers State

Do not run a new batch now. The verified source in this workspace exists only through `ch023`, so any new `ch024+` plan would be out of scope until new source is available and a fresh fetch/scan decision is made.

## Acceptance Statement

V3.10 is accepted only if the checklist template, worker prompt template, and this protocol make future bounded batch handoff repeatable without rewriting the process each time.

Current status: protocol artifacts created, but no new translation batch is started.
