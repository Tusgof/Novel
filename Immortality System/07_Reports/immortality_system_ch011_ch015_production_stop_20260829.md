# Immortality System ch011-ch015 Production Stop

Date: 2026-08-29

## Scope

- Run: `immortality-system-ch011-ch015-v1`
- Production range: `ch011-ch015`
- Requested execution: bounded five-chapter batch with stop on provider failure, hard fail, or manual prompt

## Completed State

- Glossary scan covered all 20 source blocks after raising `max_calls_per_scan` from 8 to 32.
- Operator batch decisions: 59 total, 47 approved, 12 rejected, queue remaining 0.
- Title sidecars: 5/5 present and translated with the configured Gemini translation and DeepSeek refinement routes.
- Translation: 20/20 blocks completed; current failed blocks none; manual actions none.
- QA: every completed block passed at retry 0.
- Output guardrails: passed for `ch011-ch015`.
- Final scoped Sentinel: blocker/major/minor/info `0/0/0/0`.

## Stop Cause

The ledger records one provider failure at `ch014-block-002` during refinement:

- provider/model: OpenRouter `deepseek/deepseek-v4-flash`
- failure: `nonzero_exit`
- provider detail: empty assistant message after 41.34 seconds
- recovery already performed by the configured fallback: OpenRouter Gemini completed refinement, QA passed, formatting passed, and the final block validates.

The console continued because the existing fallback chain treats a recovered route failure as non-terminal. The user's work order is stricter and requires a stop on any provider failure, including recovered historical failures. No `ch016-ch020` run was started after this incident was discovered.

## Spot-Check Finding

Manual review of the first, middle, last, and incident chapters found a repeated grammatical defect in `ch011-ch012`:

- source term: `築基`
- current base glossary rendering: `ขั้นสร้างฐาน`
- bad verb-context output: `จะขั้นสร้างฐาน`, `เรื่องการขั้นสร้างฐาน`, `ยังไม่ขั้นสร้างฐาน`

Cause: the base term does not distinguish the verb/action `築基` from explicit realm labels such as `築基期` and `築基境`.

## Prevention And Next Safe Action

1. Keep explicit realm-family terms (`築基期`, `築基境`, and stage variants) as realm labels.
2. Change only the bare `築基` policy to the verb-safe `สร้างฐาน` and add a regression/forbidden-output check for the observed malformed phrases.
3. Rerun the affected `ch011` and `ch012` blocks from the earliest meaning-safe stage, then rerun QA, formatting, assembly, output guardrails, and Sentinel.
4. Continue with a fresh `ch016-ch020` scan-only gate only after the user resumes work after this provider-failure stop.

No force-accept or manual final-output patch was used.

## Resume Attempt 2026-08-29

- Added opt-in `execution.stop_on_provider_failure: true` for Immortality System. The default remains false for other novels.
- Changed the bare `築基` glossary entry to verb-safe `สร้างฐาน`; explicit realm entries remain unchanged.
- Added a registry output guardrail for malformed `จะ/ยังไม่/การ + ขั้นสร้างฐาน` phrases.
- Reran only `ch011-block-004` from refinement. The new refined artifact contains `ควรจะสร้างฐาน` and `ยังไม่สร้างฐาน`, with none of the observed malformed phrases.
- Strict stop then triggered at QA because OpenRouter reasoning returned an empty assistant message after 27.36 seconds. No QA fallback, formatting, final assembly, `ch012` repair, or `ch016` work was started.
- Current state: `ch011-block-004` is pending QA. The existing `ch011` final output is intentionally stale and still fails the new guardrail until the verified block is assembled.

Next safe action after another explicit resume: rerun `ch011-block-004` from QA, verify and assemble `ch011`, then rerun `ch012-block-004` from refine. Do not open `ch016-ch020` until both chapters pass guardrails and scoped Sentinel.

## Second QA Resume Attempt 2026-08-29

- Reran only `ch011-block-004` from QA; translation and refinement were reused from committed artifacts.
- OpenRouter reasoning returned another empty assistant message after 220.71 seconds and exited nonzero.
- Strict provider-stop enforcement recorded exactly one additional failed QA record, left the block pending QA, and did not call a fallback.
- No provider process remained after the command exited. No formatting, final assembly, `ch012` repair, or `ch016` work was started.

Current stop cause remains an external QA provider empty-response failure. The next safe action is still a bounded rerun of `ch011-block-004` from QA after work is explicitly resumed.

## Third QA Resume Attempt 2026-08-29

- Reran only `ch011-block-004` from QA from a clean worktree and ready preflight.
- The first QA response was a valid semantic `FAIL`, so the pipeline performed one configured auto-refinement using that feedback.
- The QA retry then returned an empty assistant message after 14.99 seconds and exited nonzero.
- Strict provider-stop enforcement recorded one additional failed QA record, left the block pending QA, and did not call a fallback.
- The latest refined artifact retains the verb-safe bare `築基` rendering. No formatting, final assembly, `ch012` repair, or `ch016` work was started, and no provider process remained after exit.

The run cannot safely advance until the post-refinement QA call returns a usable verdict. Do not force-accept the pre-refinement QA failure or publish the stale final output.

## QA Recovery And Formatting Stop 2026-08-29

- Resumed only `ch011-block-004` from QA from a clean worktree and ready preflight.
- OpenRouter reasoning returned a usable `PASS` at retry 0 for the latest refined artifact.
- The AI formatter then returned output that failed deterministic content-preservation validation with `formatted text content changed`.
- Strict provider-stop enforcement recorded one formatting failure and did not use the local formatter fallback.
- The valid QA artifact was preserved. The formatted artifact and final `ch011` output retain their older timestamps and were not overwritten.
- Current pending stage is `formatting`; no `ch012` repair or `ch016` work was started, and no provider process remained after exit.

Cause: the formatting provider altered content instead of making formatting-only changes. Prevention already active: deterministic content-preservation validation plus strict provider-stop prevents unsafe formatter output from reaching final assembly. Next safe action after explicit resume: rerun only `ch011-block-004` from `formatting`, then assemble and verify `ch011`.

## New-Model ch012 Stop 2026-08-29

- `ch011-block-004` formatting subsequently passed; assembled `ch011` passed the output guardrail and scoped Sentinel `0/0/0/0`.
- Production routing was migrated to Gemini 3.7 Flash and DeepSeek V4 Flash 0731, with DeepSeek V4 Pro removed.
- DeepSeek V4 Flash 0731 completed `ch012-block-004` refinement.
- The reasoning QA call was closed by the remote host after 42.53 seconds (`WinError 10054`); strict mode stopped without fallback and left the block pending QA.
- Inspection found `ไม่สามารถขั้นสร้างฐาน` in the new refined artifact. Cause: the original rejected-variant rule did not cover this modal construction.
- Prevention was expanded in the bare `築基` glossary note, registry forbidden-output pattern, and regression test.

No QA verdict, formatting, assembly, or `ch016` work followed the provider failure. Next safe action after explicit resume is to rerun `ch012-block-004` from refinement so the expanded glossary rule is applied before QA.

## New-Model ch012 Refinement Stop 2026-08-29

- Retried only `ch012-block-004` from refinement after the expanded modal prevention was committed and pushed.
- DeepSeek V4 Flash 0731 returned an empty assistant message after 24.59 seconds.
- Strict provider-stop recorded exactly one new refinement failure, did not call fallback, and left the previous refined artifact unchanged.
- Current pending stage is refinement. No QA, formatting, assembly, or `ch016` work followed the failure, and no provider process remained after exit.

Next safe action after another explicit resume remains a bounded rerun of `ch012-block-004` from refinement.
