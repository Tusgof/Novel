---
name: novel-translation-repair
description: Use after Lean QA reports a chapter-local failure to diagnose and repair the earliest broken stage within the worker's bounded order, then rerun the required quality gates without force-accepting or changing system policy.
---

# Novel Translation Repair

This is a Worker skill for the post-QA part of a bounded Lean translation run. The Worker owns routine chapter-local recovery from diagnosis through verification. The Inspector owns architecture, provider routing, policy, scope, and final acceptance.

## Contract

- Work only inside the exact run, novel, chapter, and paths authorized by the HERDR order.
- Treat QA feedback as evidence to investigate, not as text to copy into the translation.
- Preserve the original source and ledger history. Never force-accept, weaken a gate, publish, or change a provider route.
- Do not edit `PROJECT_BRAIN.md`, `IMPLEMENT_PLAN.md`, `AGENTS.md`, architecture, or shared policy files.
- If another worker owns a path, a provider is failing globally, or the scope is ambiguous, preserve evidence and return `blocked`.

## Workflow

### 1. Freeze the incident

Check the owned provider and pipeline processes, run status, current failed blocks, and latest artifact timestamps. Do not start a second run over the same paths. Record the exact chapter/block, QA finding, stage, and run ID before editing anything.

Completion: the failure is isolated and no concurrent writer will be overwritten.

### 2. Read the evidence chain

Inspect, in order, the source, glossary projection, literal checkpoint, refined checkpoint, QA checkpoint, formatted checkpoint, final candidate, and ledger records. Compare hashes and timestamps, not filenames alone. Read the relevant source passage and the QA feedback together.

Completion: the earliest broken stage is identified with source-backed evidence.

### 3. Classify and choose the smallest repair

| Evidence | Repair | Resume point |
|:--|:--|:--|
| Provider timeout, quota/429, empty output, auth, or launch failure | Preserve traces and return `blocked`; use only the already configured fallback chain | No route change or blind retry |
| Missing, stale, or wrong raw source/title | Stop and return `blocked` unless the order explicitly authorizes source repair | Fetch/source gate |
| Glossary projection or approved term is wrong | Correct only the authorized novel/experiment glossary or projection input | Glossary or literal |
| Literal omission, truncation, mojibake, or source-script leakage | Repair the literal stage or its narrow existing hook | Literal |
| Refinement changes meaning, speaker, name, pronoun, joke, or drops content | Give QA's source-backed finding to refinement and rerun refinement | Refinement |
| Known, deterministic, source-backed spelling/variant defect | Apply the existing idempotent repair table/hook | Earliest stage that owns the defect |
| Formatting or Markdown-only defect | Use the local formatter/normalizer; do not rewrite prose | Formatting |
| QA false positive or disagreement | Use configured adjudication only; require source and Thai evidence | QA |

Never patch a final Markdown file to hide an omission, truncation, semantic drift, or glossary loss. A final-output-only repair is allowed only for a narrow deterministic formatting or approved variant fix and must leave a traceable reason.

### 4. Execute one bounded repair

Rerun only the affected block or chapter from the selected earliest stage. Keep the original artifacts and write new checkpoints through the normal pipeline. Do not rerun a whole batch or regenerate a chapter from scratch when the evidence does not require it.

Each retry must change the diagnosis, input, or stage. Do not repeat an identical failed attempt. Use at most two targeted repair cycles per chapter unless the HERDR order explicitly grants a larger repair budget.

Completion: a new candidate exists, its input hashes match the new upstream artifacts, and the ledger records the repair path.

### 5. Verify before returning

For the repaired chapter, run:

1. QA again against the original source.
2. The configured output guardrails for the touched scope.
3. Blocking Sentinel for the touched scope.
4. The relevant source-parity and artifact-integrity checks.

Confirm no current failed block, no unresolved manual action, no scope expansion, no provider/meta leakage, no CJK leakage, no truncation, and no rejected glossary variant. If the same defect appears in another chapter in the authorized range, report it and apply the same narrow repair only when evidence proves the pattern is shared.

Completion: the latest status and all required gates pass, or the chapter is quarantined with a concrete blocker.

### 6. Return a worker report

Return the exact run/chapter scope, root cause, earliest broken stage, files changed, commands and exit codes, repair cycles used, QA/guardrail/Sentinel results, remaining blockers, and next action. Report `complete` only when the repaired artifact is accepted by the normal gates. Report `blocked` for provider failure, manual input, missing source, scope conflict, or an unresolved QA/Sentinel failure.

## Efficiency rules

- Prefer checkpoint reuse and the earliest safe rerun; do not spend provider calls on already valid stages.
- Prefer deterministic, idempotent, source-backed repairs over another unconstrained rewrite.
- Keep QA as a judge: it reports the discrepancy; the repair stage changes the translation.
- Treat a successful fallback as a provider incident that must remain visible in metadata; it does not erase the failure.
- If a recurring pattern needs a shared guardrail, record a prevention proposal for the Inspector instead of editing system architecture from the Worker.
