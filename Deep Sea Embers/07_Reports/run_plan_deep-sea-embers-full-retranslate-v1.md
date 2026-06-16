# Run Plan Report - deep-sea-embers-full-retranslate-v1

## Summary
- read_only: yes
- preflight_status: degraded
- current_failed_blocks: none
- manual_actions: resume --run-id deep-sea-embers-full-retranslate-v1.
- recommended_batch_size: 1-3 chapters
- recommended_checkpoint: resume --run-id deep-sea-embers-full-retranslate-v1.

## Suggested Commands
- `novel-pipeline --config "D:\Fogust\Workspace\Novel\Deep Sea Embers\.system\config.yaml" status --run-id deep-sea-embers-full-retranslate-v1`
- `novel-pipeline --config "D:\Fogust\Workspace\Novel\Deep Sea Embers\.system\config.yaml" report checkpoint --run-id deep-sea-embers-full-retranslate-v1`
- `novel-pipeline --config "D:\Fogust\Workspace\Novel\Deep Sea Embers\.system\config.yaml" report provider-usage --run-id deep-sea-embers-full-retranslate-v1`
- `novel-pipeline --config "D:\Fogust\Workspace\Novel\Deep Sea Embers\.system\config.yaml" resume --run-id deep-sea-embers-full-retranslate-v1 --manual-action-mode stop`

## Provider Readiness
| provider | status | stages | transport |
| --- | --- | --- | --- |
| claude | ready | term_suggestion:fallback | stdin |
| codex | ready | fetch, literal_translation:fallback, project_setup, qa_judge:fallback, refinement:fallback, term_extraction:fallback | stdin |
| openrouter | ready | formatting, formatting:fallback, literal_translation, literal_translation:fallback, qa_judge:fallback, refinement, refinement:fallback, refinement:fallback, term_extraction, term_extraction:fallback, term_suggestion, term_suggestion:fallback | stdin |
| openrouter_reasoning | ready | qa_judge | stdin |
| qwen | ready | qa_judge:fallback, refinement:fallback | stdin |

## Routing And Fallbacks
| stage | provider | model | fallbacks | timeout |
| --- | --- | --- | --- | --- |
| fetch | codex | gpt-5.4 | none | default |
| formatting | openrouter | deepseek/deepseek-v4-flash | openrouter/google/gemini-3-flash-preview | default |
| literal_translation | openrouter | google/gemini-3-flash-preview | openrouter/deepseek/deepseek-v4-flash, codex/gpt-5.4 | default |
| project_setup | codex | gpt-5.4 | none | default |
| qa_judge | openrouter_reasoning | deepseek/deepseek-v4-flash | qwen/deepseek-reasoner, openrouter/deepseek/deepseek-v4-pro, codex/gpt-5.4 | default |
| refinement | openrouter | deepseek/deepseek-v4-flash | openrouter/google/gemini-3-flash-preview, openrouter/anthropic/claude-sonnet-4.6, codex/gpt-5.4, qwen/deepseek-reasoner | default |
| term_extraction | openrouter | google/gemini-3-flash-preview | openrouter/deepseek/deepseek-v4-flash, codex/gpt-5.4 | 120.0 |
| term_suggestion | openrouter | deepseek/deepseek-v4-flash | openrouter/google/gemini-3-flash-preview, claude/sonnet | 120.0 |

## Recent Failures
| block | stage | provider | status | message |
| --- | --- | --- | --- | --- |
| none | none | none | none | none |

## Cache Readiness
| stage | completed | artifact exists | input hash | output hash | hash-cache ready |
| --- | ---: | ---: | ---: | ---: | ---: |
| translating | 0 | 0 | 0 | 0 | 0 |
| refining | 0 | 0 | 0 | 0 | 0 |
| qa | 0 | 0 | 0 | 0 | 0 |
| formatting | 0 | 0 | 0 | 0 | 0 |

## Cache Policy
| mode | runtime skip | stages | rule |
| --- | --- | --- | --- |
| report_only | false | title_translation, term_suggestion, translating | skip only when stage input hash, output hash, and artifact validation match |

## Speed Savings Estimate
| stage | cache-ready artifacts | average seconds | estimated seconds saved | confidence | note |
| --- | ---: | ---: | ---: | --- | --- |
| translating | 0 | n/a | n/a | low | insufficient clean timing baseline |
| refining | 0 | n/a | n/a | low | insufficient clean timing baseline |
| qa | 0 | n/a | n/a | low | insufficient clean timing baseline |
| formatting | 0 | n/a | n/a | low | insufficient clean timing baseline |

## Timing Baseline
| stage | provider | records | completed | failed | duration records | total seconds | average seconds |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| fetched | local | 6 | 6 | 0 | 0 | 0.00 | n/a |
| glossary_approved | local | 3 | 3 | 0 | 0 | 0.00 | n/a |
| glossary_scanned | local | 6 | 6 | 0 | 0 | 0.00 | n/a |

## Concurrency Benchmark Recommendations
| stage | provider | duration records | average seconds | failed | recommendation | confidence |
| --- | --- | ---: | ---: | ---: | --- | --- |
| none | none | 0 | n/a | 0 | no eligible stage data | low |

## Execution Policy
| stage | configured limit | effective limit | concurrency enabled |
| --- | ---: | ---: | --- |
| formatting | 2 | 1 | false |
| qa | 1 | 1 | false |
| refining | 2 | 1 | false |
| translating | 2 | 1 | false |

## Benchmark Scope Plan
| stage | provider | target limit | scope | prerequisite | stop condition |
| --- | --- | ---: | --- | --- | --- |
| none | none | 1 | no concurrency benchmark recommended from current evidence | collect more timing data or resolve failed records | n/a |

## Guardrail Policy
| guardrail | mode | runtime blocking | threshold |
| --- | --- | --- | --- |
| pre_qa | report_only | false | dense paragraph warning >900 chars |

## Pre-QA Guardrail Preview
- report_only: yes
- refined_artifacts_checked: 0
- missing_refined_artifacts: 0
- hard_error_blocks: 0
- warning_blocks: 0

| block | hard errors | warnings | artifact |
| --- | --- | --- | --- |
| none | none | none | none |

## Speed-Safety Notes
- glossary approval remains human-gated and sequential
- QA and AI formatting stay enabled; this report does not replace either gate
- cache readiness is report-only; execution still uses existing ledger skip behavior
- pre-QA guardrail preview is report-only; it does not block or skip AI QA yet
- keep risky stages sequential until a benchmark proves stability
- use bounded resume/checkpoints rather than open-ended production runs
