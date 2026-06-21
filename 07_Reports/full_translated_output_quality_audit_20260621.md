# Full Translated Output Quality Audit - 2026-06-21

## Scope

- Deep Sea Embers final output: `ch001-ch150`
- Horror Game Developers final output: `ch001-ch220`
- MoonRead generated reader content for both current novels

## Reason

User correctly pointed out that fixing only HGD `ch149` was not enough. The translated library needed a broader standards check for repeated leakage patterns, mixed English artifacts, malformed Markdown, and reader-facing generated output.

## Hard Failures Found And Repaired

- Deep Sea Embers `ch046`: removed English explanatory leftovers from `สิ่งผิดปกติ (Anomaly)` and `ปรากฏการณ์ประหลาด (Vision)`.
- Deep Sea Embers `ch054`: removed leaked metadata marker `เสียง (term)`.
- HGD `ch177` / `ch199`: removed leaked category labels such as `(rank)`, `(system)`, `(character)`, and `(entity)`.
- HGD `ch186`: repaired inline `***` marker into a clean scene break.
- HGD `ch208` and `ch219`: repaired broken UI choice/menu Markdown that rendered as split `]**` fragments.

## Prevention Added

- `scripts/check_output_quality_guardrails.py` now rejects leaked translation metadata labels: `(character)`, `(entity)`, `(rank)`, `(system)`, `(term)`.
- The same guardrail now catches broken UI bracket wrappers like `]**` / `(...)]**` lines.
- `test_translation.py` has regression coverage for metadata leakage and broken UI marker detection.
- After user clarification, approved HGD glossary entries are now treated as Thai-only product text, not optional bilingual display. The guardrail now rejects approved English originals/aliases that remain as parentheticals or UI labels after the approved Thai term.
- HGD approved glossary notes with mojibake placeholder Thai terms were repaired so deterministic glossary enforcement has usable Thai targets.

## Validation

- DSE output guardrail for `ch001-ch150`: passed.
- HGD output guardrail for `ch001-ch220`: passed.
- Known hard-fail scan for metadata labels, malformed `]**`, stale `(term)`, and DSE `(Anomaly)` / `(Vision)` leftovers: no hits in final output.
- `python test_translation.py`: passed.
- MoonRead `npm.cmd run generate:chapters`: passed.
- MoonRead `npm.cmd run lint`: passed.
- MoonRead `npm.cmd run build`: passed.
- MoonRead `npm.cmd run smoke`: passed.

## Glossary Policy Clarification

No extra policy choice is needed for approved glossary terms. If a term is approved in `01_Glossary`, final output and MoonRead should use the approved `thai_term`; the English original/alias should not remain as a parenthetical or UI label unless a future explicit glossary field says bilingual display is intended.

Remaining English that is not covered by an approved glossary entry must be handled by the glossary gate: approve a Thai term, reject it as ordinary text, or add an explicit exception.
