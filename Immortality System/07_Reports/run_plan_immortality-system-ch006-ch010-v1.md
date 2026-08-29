# Run Plan Report - immortality-system-ch006-ch010-v1

## Summary
- read_only: yes
- preflight_status: degraded
- current_failed_blocks: none
- manual_actions: none
- recommended_batch_size: 1-3 chapters
- recommended_checkpoint: next bounded range after ch010

## Suggested Commands
- `novel-pipeline --config "D:\Fogust\Workspace\Novel\Immortality System\.system\config.yaml" status --run-id immortality-system-ch006-ch010-v1`
- `novel-pipeline --config "D:\Fogust\Workspace\Novel\Immortality System\.system\config.yaml" report checkpoint --run-id immortality-system-ch006-ch010-v1`
- `novel-pipeline --config "D:\Fogust\Workspace\Novel\Immortality System\.system\config.yaml" report provider-usage --run-id immortality-system-ch006-ch010-v1`
- `novel-pipeline --config "D:\Fogust\Workspace\Novel\Immortality System\.system\config.yaml" resume --run-id immortality-system-ch006-ch010-v1 --manual-action-mode stop`

## Provider Readiness
| provider | status | stages | transport |
| --- | --- | --- | --- |
| claude | ready | term_suggestion:fallback | stdin |
| codex | ready | fetch, literal_translation:fallback, project_setup, refinement:fallback, term_extraction:fallback | stdin |
| openrouter | ready | formatting, formatting:fallback, literal_translation, literal_translation:fallback, qa_judge:fallback, refinement, refinement:fallback, refinement:fallback, term_extraction, term_extraction:fallback, term_suggestion, term_suggestion:fallback | stdin |
| openrouter_reasoning | ready | qa_judge, qa_judge:fallback | stdin |
| qwen | ready | refinement:fallback | stdin |

## Routing And Fallbacks
| stage | provider | model | fallbacks | timeout |
| --- | --- | --- | --- | --- |
| fetch | codex | gpt-5.4 | none | default |
| formatting | openrouter | deepseek/deepseek-v4-flash | openrouter/google/gemini-3-flash-preview | default |
| literal_translation | openrouter | google/gemini-3-flash-preview | openrouter/deepseek/deepseek-v4-flash, codex/gpt-5.4 | default |
| project_setup | codex | gpt-5.4 | none | default |
| qa_judge | openrouter_reasoning | deepseek/deepseek-v4-flash | openrouter_reasoning/deepseek/deepseek-v4-pro, openrouter/google/gemini-3-flash-preview | default |
| refinement | openrouter | deepseek/deepseek-v4-flash | openrouter/google/gemini-3-flash-preview, openrouter/anthropic/claude-sonnet-4.6, codex/gpt-5.4, qwen/deepseek-reasoner | default |
| term_extraction | openrouter | google/gemini-3-flash-preview | openrouter/deepseek/deepseek-v4-flash, codex/gpt-5.4 | 120.0 |
| term_suggestion | openrouter | deepseek/deepseek-v4-flash | openrouter/google/gemini-3-flash-preview, claude/sonnet | 120.0 |

## Recent Failures
| block | stage | provider | status | message |
| --- | --- | --- | --- | --- |
| ch008-block-001 | refining | openrouter | failed | Provider 'openrouter' returned unusable output (nonzero_exit). OpenRouter shim error after 42.18s: OpenRouter returned an empty assistant message. |
| ch010-block-004 | refining | openrouter | failed | Provider 'openrouter' returned unusable output (nonzero_exit). OpenRouter shim error after 44.78s: OpenRouter returned an empty assistant message. |

## Cache Readiness
| stage | completed | artifact exists | input hash | output hash | hash-cache ready |
| --- | ---: | ---: | ---: | ---: | ---: |
| translating | 20 | 20 | 20 | 20 | 20 |
| refining | 20 | 20 | 18 | 20 | 18 |
| qa | 20 | 20 | 0 | 0 | 0 |
| formatting | 20 | 20 | 0 | 20 | 0 |

## Cache Policy
| mode | runtime skip | stages | rule |
| --- | --- | --- | --- |
| report_only | false | none | skip only when stage input hash, output hash, and artifact validation match |

## Speed Savings Estimate
| stage | cache-ready artifacts | average seconds | estimated seconds saved | confidence | note |
| --- | ---: | ---: | ---: | --- | --- |
| translating | 20 | n/a | n/a | low | insufficient clean timing baseline |
| refining | 18 | n/a | n/a | low | insufficient clean timing baseline |
| qa | 0 | n/a | n/a | low | insufficient clean timing baseline |
| formatting | 0 | 30.50 | 0.00 | low | read-only estimate; runtime cache skip is not enabled |

## Timing Baseline
| stage | provider | records | completed | failed | duration records | total seconds | average seconds |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| completed | local | 20 | 20 | 0 | 0 | 0.00 | n/a |
| fetched | local | 5 | 5 | 0 | 0 | 0.00 | n/a |
| formatting | openrouter | 20 | 20 | 0 | 20 | 609.97 | 30.50 |
| glossary_approved | local | 5 | 5 | 0 | 0 | 0.00 | n/a |
| glossary_scanned | local | 5 | 5 | 0 | 0 | 0.00 | n/a |
| qa | openrouter | 14 | 14 | 0 | 0 | 0.00 | n/a |
| qa | openrouter_reasoning | 6 | 6 | 0 | 0 | 0.00 | n/a |
| refining | openrouter | 26 | 24 | 2 | 2 | 88.64 | 44.32 |
| sentinel | local | 5 | 5 | 0 | 0 | 0.00 | n/a |
| translating | openrouter | 20 | 20 | 0 | 0 | 0.00 | n/a |

## Concurrency Benchmark Recommendations
| stage | provider | duration records | average seconds | failed | recommendation | confidence |
| --- | --- | ---: | ---: | ---: | --- | --- |
| formatting | openrouter | 20 | 30.50 | 0 | benchmark concurrency=2 on a small approved range | medium |
| refining | openrouter | 2 | 44.32 | 2 | keep sequential until failures are reviewed | low |
| translating | openrouter | 0 | n/a | 0 | collect more timing metadata before concurrency | low |

## Concurrency Simulation
| stage | provider | timing records | configured limit | sequential seconds | projected seconds | estimated saved seconds | reduction % | note |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| none | none | 0 | 1 | 0.00 | 0.00 | 0.00 | 0.0 | no configured concurrency limits |

## Execution Policy
| stage | configured limit | effective limit | concurrency enabled |
| --- | ---: | ---: | --- |
| formatting | 1 | 1 | false |
| qa | 1 | 1 | false |
| refining | 1 | 1 | false |
| translating | 1 | 1 | false |

## Benchmark Scope Plan
| stage | provider | target limit | scope | prerequisite | stop condition |
| --- | --- | ---: | --- | --- | --- |
| formatting | openrouter | 1 | next approved 1-chapter bounded range after ch010 | user-approved scan/glossary gate and no current failed blocks | first provider failure, QA hard-fail, formatting validation failure, or scope expansion |

## Guardrail Policy
| guardrail | mode | runtime blocking | threshold |
| --- | --- | --- | --- |
| pre_qa | report_only | false | dense paragraph warning >900 chars |

## Pre-QA Guardrail Preview
- report_only: yes
- refined_artifacts_checked: 20
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
