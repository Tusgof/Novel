# Cache Benchmark Report - deep-sea-embers-retranslate-ch001-v1

Read-only V6.18B benchmark planning report. It does not enable cache, skip provider calls, edit ledger, or change artifacts.

## Cache Policy
| mode | runtime skip | stages | rule |
| --- | --- | --- | --- |
| report_only | false | title_translation, term_suggestion, translating | skip only when stage input hash, output hash, and artifact validation match |

## Benchmark Summary
| stage | records | eligible | blocked | average seconds | estimated saved seconds | confidence | decision | note |
| --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| translating | 5 | 5 | 0 | n/a | n/a | low | not_ready | insufficient clean translating timing baseline |

## Translating Cache Eligibility
| block | provider | input hash | output hash | artifact | eligible | reason |
| --- | --- | --- | --- | --- | --- | --- |
| ch001-block-001 | gemini | yes | yes | yes | yes | ready |
| ch001-block-002 | gemini | yes | yes | yes | yes | ready |
| ch001-block-003 | gemini | yes | yes | yes | yes | ready |
| ch001-block-004 | gemini | yes | yes | yes | yes | ready |
| ch001-block-005 | gemini | yes | yes | yes | yes | ready |

## Safety Notes
- Only `translating` is assessed because it is the only runtime cache-skip stage currently implemented.
- Refinement, QA, and formatting cache skip remain disabled.
- This report is not approval to switch `.system/config.yaml` to `enabled`.
