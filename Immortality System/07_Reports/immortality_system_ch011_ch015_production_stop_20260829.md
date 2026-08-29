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
