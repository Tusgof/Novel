# Immortality System Libra - Pilot Provider Health Check

Date: 2026-08-28
Scope: bounded pre-resume checks for the isolated Libra - Pilot Gate

## Checks

| Route | Result | Evidence |
| --- | --- | --- |
| OpenRouter `deepseek/deepseek-v4-flash` term suggestion | primary failed closed | Empty assistant message; no term was accepted |
| OpenRouter `google/gemini-3-flash-preview` term suggestion fallback | passed | Returned three parseable Thai options |
| local Gemini CLI `pro` fallback | unavailable | Client rejected the current individual free-tier session as unsupported |
| OpenRouter `deepseek/deepseek-v4-flash` title refinement | output rejected | Returned JSON whose title was not valid Thai |
| OpenRouter `google/gemini-3-flash-preview` title refinement fallback | passed | Returned parseable JSON with a Thai title and no Chinese characters |
| Pilot title sidecars | passed | Exact title validator passed `20/20` locked sample sidecars |

## Decision

The configured OpenRouter fallback routes are usable for the two previously blocking surfaces, so the existing in-sample run may resume. Primary provider failures remain recorded as recoverable incidents; the pipeline must continue to fail closed if all configured routes fail, output is unparseable, or a blocking Sentinel finding remains.

The local Gemini CLI remains an unavailable fallback and was not repaired or silently removed from routing in this check. No provider routing change was made.

## Safety

- Checks used tiny prompts and did not write production output, production glossary notes, MoonRead content, or pilot ledger records.
- The API key was read from `NOVEL_OPENROUTER_API` by the shim and was not printed or written to this report.
- The Pilot remains experiment-only until both in-sample and out-of-sample gates complete.
