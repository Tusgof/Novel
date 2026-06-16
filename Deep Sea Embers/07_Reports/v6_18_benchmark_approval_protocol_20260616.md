# V6.18 Benchmark Approval Protocol - 2026-06-16

Purpose: define the smallest safe benchmark that can prove V6.18 speed improvement without weakening translation quality.

This report is read-only. It does not enable concurrency, enable cache skipping, call providers, edit ledger, or change artifacts.

## Current Evidence

- Current config keeps `execution.concurrency_enabled: false`.
- Current config keeps `execution.artifact_cache.mode: report_only`.
- Current config keeps `execution.pre_qa_guardrail.mode: report_only`.
- Read-only concurrency report: `07_Reports/concurrency_benchmark_deep-sea-embers-retranslate-ch001-ch050-v2.md`.
- Read-only run-plan report: `07_Reports/run_plan_deep-sea-embers-retranslate-ch001-ch050-v2.md`.
- Read-only cache report: `07_Reports/cache_benchmark_deep-sea-embers-retranslate-ch001-ch050-v2.md`.

The only stage/provider currently ready for a small benchmark is:

| stage | provider | target limit | evidence | status |
| --- | --- | ---: | --- | --- |
| formatting | openrouter | 2 | 268 timing records, 0 failed, projected 32.6% reduction | ready_for_small_benchmark |

All other stage/provider rows remain not ready because they have failed history or insufficient clean timing evidence.

## Required User Approval

Do not run the benchmark until the user explicitly approves this exact scope:

- stage: formatting only
- provider: openrouter only
- target concurrency: 2
- chapter scope: next approved 1-chapter bounded range after `ch050`
- production routing: unchanged except the explicitly approved benchmark flag/config for this test
- glossary approval: already completed for the benchmark chapter before translation continues
- QA: still required
- AI formatting: still required
- final-output guardrails: required

Approval wording should be explicit, for example:

```text
Approve V6.18 formatting/openrouter concurrency=2 benchmark on one bounded chapter after ch050.
```

## Stop Conditions

Stop immediately if any of these occur:

- provider failure
- command_too_long
- QA hard-fail
- manual prompt
- formatting validation failure
- output guardrail failure
- scope expands beyond the approved chapter
- any chNNN outside the approved range is processed
- ledger state becomes ambiguous

## Measurement

The benchmark report must compare:

- baseline sequential formatting timing from prior ledger data
- benchmark wall-clock timing
- provider failures
- QA failures or retries
- formatting validation issues
- final-output guardrail result
- exact files changed
- exact ledger records appended

Success requires:

- wall-clock improvement is visible for the approved chapter
- no new QA hard-fail
- no formatting validation failure
- final output passes guardrails
- runtime concurrency remains disabled after the benchmark unless a separate approval changes it

## Non-Goals

- Do not enable global parallel execution.
- Do not enable cache skipping.
- Do not benchmark translating, refining, or QA concurrency yet.
- Do not change provider routing.
- Do not start a new production batch as part of this protocol.

## Next Safe Action

Ask the user whether to approve the exact benchmark scope above. If not approved, keep V6.18 in planning state and continue only with read-only reports or unrelated deterministic work.
