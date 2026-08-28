# Immortality System Libra - Pilot Gate: Provider Stop

Date: 2026-08-28
Status: blocked before translation
Scope: isolated in-sample glossary approval for `immortality-libra-v1-insample`

## Verified State

- Novel543 raw source is complete through `ch2570` (`2570/2570` usable chapters).
- The locked 20-chapter sample was copied from raw source and source parity passed: `20 checked`, `0 mismatches`.
- In-sample scan completed for 10 chapters and produced `73` candidates.
- Out-of-sample scan completed for 10 chapters and produced `66` candidates.
- No translation, refinement, QA, formatting, final output, or MoonRead publication was created by this pilot.
- Pilot experiment output remains isolated under `04_Work/_experiments/`.

## Stop Evidence

The first glossary approval attempt stopped at `仙尊境`. The second bounded retry stopped at `關萍`.
Both provider paths returned no parseable Thai options, so the run was stopped instead of accepting
Chinese or provider-fallback text as glossary output.

Bounded provider probes:

| Probe | Result |
|:--|:--|
| `deepseek/deepseek-v4-flash`, normal request | exit `1`, empty assistant message |
| `deepseek/deepseek-v4-flash`, reasoning enabled | returned `OK` |
| `google/gemini-3-flash-preview`, short request | returned `OK` |
| Gemini term suggestion probe for `仙尊境` | returned three parseable Thai lines |

## Root Causes

1. The configured term-suggestion primary calls DeepSeek V4 Flash without reasoning. The model can
   return an empty assistant message in that mode.
2. `build_term_suggestion()` converts an unavailable or unparseable provider response into
   deterministic fallback options. For a Chinese term those options can still contain Chinese,
   which is unsafe and should not be accepted as a glossary decision.
3. The Immortality System term template was missing the opening YAML frontmatter delimiter and had
   `source_language: zh` in a template that the writer also fills. Approved notes could not be
   parsed and were repeatedly treated as pending. The production and experiment templates were
   corrected, and a regression test now verifies a write/parse round trip.

## Prevention And Next Safe Action

- Keep this pilot stopped until the term-suggestion provider returns parseable Thai options or an
  explicitly approved routing/treatment change is made.
- Do not accept deterministic fallback options for non-curated CJK terms.
- On resume, use the existing run ID and verify that newly written glossary notes parse before
  allowing translation stages to run.
- Do not publish, copy pilot glossary intent into production, or start `ch001-ch060` until the
  20-chapter Pilot Gate has completed its measured in-sample and out-of-sample rounds.

## Artifacts

- `07_Reports/libra_pilot_gate_sample_20260828.json`
- `07_Reports/libra_pilot_gate_sample_20260828.md`
- `04_Work/_experiments/libra_pilot_immortality_system_v1/04_Work/_batch/immortality-libra-v1-insample/glossary_scan.json`
- `04_Work/_experiments/libra_pilot_immortality_system_v1/06_Logs/run_ledger.jsonl`
- `Immortality System/00_Templates/Term-Template.md`
- `Deep Sea Embers/test_translation.py::test_immortality_term_template_round_trips_written_note`
