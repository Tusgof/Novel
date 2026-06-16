# OpenRouter Provider Replacement Experiment - 2026-06-09

## Purpose

Design a controlled experiment to find provider routes that can replace or reduce dependency on unstable current routes:

- Claude CLI refinement fills session quota quickly.
- Gemini is slow or quota-limited in some routes.
- Qwen formatting has occasionally rewritten, truncated, or drifted from QA-passed refined text.

This is a benchmark design only. Do not change production routing until a benchmark report proves a replacement is safe.

## Current Production State

Active run: `deep-sea-embers-retranslate-ch024-ch028-v1`

- ch024: 5/5 complete, output exists
- ch025: 5/5 complete, output exists
- ch026: 5/5 complete, output exists
- ch027: 5/5 complete, output exists
- ch028: 0/5 complete
- current failed block: `ch028-block-001`
- failed stage: `refining`
- cause: Claude session limit
- current safe recovery: rerun `ch028-block-001` from `refine` or continue bounded resume after provider routing is confirmed

Recent provider symptoms from this run:

- Claude: multiple `refining` failures caused by session limit.
- Codex: successful fallback/refinement and translation route.
- Qwen formatting: several provider-formatted artifacts failed deterministic validation because content changed.
- Gemini: not active in this run, but previously caused slow/quota/command-length issues.

## OpenRouter API Basis

Use OpenRouter directly, not through Qwen CLI, for this experiment.

Relevant OpenRouter endpoints:

- Chat completions: `POST https://openrouter.ai/api/v1/chat/completions`
- Model catalog: `GET https://openrouter.ai/api/v1/models`

The benchmark harness should use `OPENROUTER_API_KEY` from the shell environment. Do not store the key in any file.

## Candidate Models

All candidate slugs below were found in the OpenRouter public model catalog on 2026-06-09.

| Slot | Model | Context | Prompt price | Completion price | Primary test role |
| --- | --- | ---: | ---: | ---: | --- |
| 01 | `deepseek/deepseek-v4-flash` | 1048576 | 0.0000000983 | 0.0000001966 | cheap glossary, literal, formatting |
| 02 | `tencent/hy3-preview` | 262144 | 0.000000063 | 0.00000021 | cheap glossary, literal |
| 03 | `minimax/minimax-m3` | 1048576 | 0.0000003 | 0.0000012 | long-context glossary/refinement |
| 04 | `minimax/minimax-m3` | 1048576 | 0.0000003 | 0.0000012 | repeatability rerun for slot 03 |
| 05 | `xiaomi/mimo-v2.5` | 1048576 | 0.00000014 | 0.00000028 | cheap literal/formatting |
| 06 | `openrouter/owl-alpha` | 1048756 | 0 | 0 | free experimental baseline |
| 07 | `anthropic/claude-sonnet-4.6` | 1000000 | 0.000003 | 0.000015 | Claude-route replacement via OpenRouter |
| 08 | `deepseek/deepseek-v4-pro` | 1048576 | 0.000000435 | 0.00000087 | refinement/QA reasoning |
| 09 | `deepseek/deepseek-v3.2` | 131072 | 0.0000002288 | 0.0000003432 | balanced refinement/QA fallback |
| 10 | `google/gemini-3-flash-preview` | 1048576 | 0.0000005 | 0.000003 | Gemini-route replacement via OpenRouter |

Note: slots 03 and 04 intentionally use the same model. Slot 04 should be a repeatability check, not a separate candidate.

## Benchmark Phases

### Phase A: Availability Smoke

For each model:

- send a tiny Thai JSON-only prompt
- require valid JSON
- record latency, HTTP status, model slug returned, token usage, and error class
- stop a model after two smoke failures

Pass criteria:

- non-empty response
- valid JSON
- latency under the configured timeout
- no auth/quota/provider error

### Phase B: Role-Specific Tasks

Task 1: glossary scan replacement

- Input: source excerpts from ch024-ch028.
- Output: strict JSON candidate list with `original_term`, `category`, `first_seen_block`, and `reason`.
- Pass: finds real proper/lore terms without flooding fragments/generic terms.

Task 2: literal translation replacement

- Input: one medium Chinese block plus approved glossary context.
- Output: sentence-pair JSON compatible with the literal stage.
- Pass: no omissions, no added prose, no mojibake, no unintended body Chinese, glossary preserved.

Task 3: refinement replacement

- Input: literal artifact from a real block.
- Output: refined Thai prose only.
- Pass: Qwen QA or deterministic review finds no omissions, no meaning drift, no over-shortening.

Task 4: QA judge candidate

- Input: known-good and known-bad examples.
- Must include prior failure shapes:
  - perspective drift in internal monologue
  - sentence drop/omission
  - formatter truncation/content rewrite
- Output: strict pass/fail JSON plus concise findings.
- Pass: catches known semantic failures and never sets `passed: true` with failure feedback.

Task 5: formatting candidate

- Input: QA-passed refined Thai.
- Output: formatted Thai only.
- Pass: deterministic validation proves content preservation; no truncation, no provider/meta leakage, no unintended Han text, no quote-only lines.

### Phase C: Bounded Production Probe

Only models passing Phase B may be tested on one bounded block.

Rules:

- use an experiment run ID, not the active production run
- write artifacts only under `04_Work/_experiments/`
- do not modify `06_Logs/`, `04_Work/ch*/`, `05_Output/`, `01_Glossary/`, source files, or production config
- compare results against current Codex/Claude/Qwen behavior on the same fixture

## Scoring

| Criterion | Points |
| --- | ---: |
| availability and transport reliability | 20 |
| semantic preservation | 30 |
| glossary correctness | 15 |
| formatting/content preservation | 10 |
| structured-output compliance | 10 |
| speed/cost practicality | 10 |
| recoverability and useful error behavior | 5 |

Decision thresholds:

- `>= 85`: production replacement candidate if there are no hard fails.
- `75-84`: fallback-only candidate.
- `< 75`: reject for production routing.
- automatic reject: silent truncation, malformed output in core role, persistent timeout, or QA failure incorrectly marked as pass.

## Recommended Role Hypotheses

- First test as Claude refinement replacement:
  - `anthropic/claude-sonnet-4.6`
  - `deepseek/deepseek-v4-pro`
  - `minimax/minimax-m3`
  - `deepseek/deepseek-v3.2`

- First test as Gemini/term-extraction/literal replacement:
  - `deepseek/deepseek-v4-flash`
  - `tencent/hy3-preview`
  - `xiaomi/mimo-v2.5`
  - `google/gemini-3-flash-preview`

- First test as formatting replacement:
  - `deepseek/deepseek-v4-flash`
  - `xiaomi/mimo-v2.5`
  - `tencent/hy3-preview`

- Treat `openrouter/owl-alpha` as experimental only until it proves stable.

## Security Rules

- Never commit API keys.
- Never write the key to `.system/providers.yaml`.
- Never include request headers in reports.
- Set the key only in the running shell, for example:
  - `$env:OPENROUTER_API_KEY = '<redacted>'`
- Reports may include model slug, latency, token usage, cost estimate, and error class.
- Reports must not include bearer token values.

## Stop Conditions

Stop the benchmark immediately if:

- any API key appears in a file, report, command transcript, or git diff
- benchmark code writes outside `04_Work/_experiments/` and `07_Reports/`
- any task modifies production ledger, glossary, source, work artifacts, output chapters, or provider config
- a model silently truncates or rewrites content
- a QA candidate marks a known failure as pass
- OpenRouter returns unstable provider/routing errors that prevent reproducible smoke results

## Next Implementation Step

Implement `scripts/openrouter_provider_benchmark.py` as a non-production harness:

- reads `OPENROUTER_API_KEY`
- supports `--smoke-only`, `--models`, `--roles`, `--max-calls`
- writes raw and scored outputs under `04_Work/_experiments/openrouter_provider_benchmark_<timestamp>/`
- writes final markdown report under `07_Reports/`
- never edits `.system/providers.yaml` or production artifacts

Only after that report exists should `.system/providers.yaml` routing changes be proposed.
