# Concurrency Benchmark Report - deep-sea-embers-retranslate-ch001-ch050-v2

Read-only V6.18A benchmark planning report. It does not enable parallel runtime, execute providers, edit ledger, or change artifacts.

## Benchmark Summary
| stage | provider | configured limit | duration records | failed | projected saved seconds | projected reduction % | decision | next action |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| formatting | local | 2 | 0 | 3 | 0.00 | 0.0 | not_ready | collect cleaner timing data or review failed records |
| formatting | openrouter | 2 | 268 | 0 | 1912.71 | 32.6 | ready_for_small_benchmark | run an explicitly approved small non-production benchmark |
| refining | codex | 2 | 0 | 0 | 0.00 | 0.0 | not_ready | collect cleaner timing data or review failed records |
| refining | openrouter | 2 | 7 | 7 | 0.00 | 0.0 | not_ready | collect cleaner timing data or review failed records |
| translating | codex | 2 | 0 | 0 | 0.00 | 0.0 | not_ready | collect cleaner timing data or review failed records |
| translating | openrouter | 2 | 2 | 2 | 0.00 | 0.0 | not_ready | collect cleaner timing data or review failed records |

## Execution Policy
| stage | configured limit | effective limit | concurrency enabled |
| --- | ---: | ---: | --- |
| formatting | 2 | 1 | false |
| qa | 1 | 1 | false |
| refining | 2 | 1 | false |
| translating | 2 | 1 | false |

## Recommendations
| stage | provider | duration records | average seconds | failed | recommendation | confidence |
| --- | --- | ---: | ---: | ---: | --- | --- |
| formatting | local | 0 | n/a | 3 | keep sequential until failures are reviewed | low |
| formatting | openrouter | 268 | 21.90 | 0 | benchmark concurrency=2 on a small approved range | medium |
| refining | codex | 0 | n/a | 0 | collect more timing metadata before concurrency | low |
| refining | openrouter | 7 | 19.43 | 7 | keep sequential until failures are reviewed | low |
| translating | codex | 0 | n/a | 0 | collect more timing metadata before concurrency | low |
| translating | openrouter | 2 | 12.10 | 2 | keep sequential until failures are reviewed | low |

## Simulation
| stage | provider | timing records | configured limit | sequential seconds | projected seconds | estimated saved seconds | reduction % | note |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| formatting | local | 0 | 2 | 0.00 | 0.00 | 0.00 | 0.0 | simulation withheld because stage/provider has failed records |
| formatting | openrouter | 268 | 2 | 5868.58 | 3955.88 | 1912.71 | 32.6 | simulation only; runtime remains sequential |
| qa | local | 0 | 1 | 0.00 | 0.00 | 0.00 | 0.0 | simulation withheld because stage/provider has failed records |
| qa | openrouter | 0 | 1 | 0.00 | 0.00 | 0.00 | 0.0 | simulation withheld because stage/provider has failed records |
| refining | codex | 0 | 2 | 0.00 | 0.00 | 0.00 | 0.0 | insufficient completed timing records |
| refining | openrouter | 0 | 2 | 0.00 | 0.00 | 0.00 | 0.0 | simulation withheld because stage/provider has failed records |
| translating | codex | 0 | 2 | 0.00 | 0.00 | 0.00 | 0.0 | insufficient completed timing records |
| translating | openrouter | 0 | 2 | 0.00 | 0.00 | 0.00 | 0.0 | simulation withheld because stage/provider has failed records |

## Safety Notes
- This report is not approval to set `execution.concurrency_enabled: true`.
- Glossary approval remains sequential and human-gated.
- QA and AI formatting must remain enabled in any benchmark.
- Stop on first hard failure, provider failure spike, command_too_long, or final-output guardrail regression.
