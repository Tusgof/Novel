# HGD English/Glossary Leakage Repair - 2026-06-21

## Trigger

User reported that HGD chapter 149 translated `Twisted Man` as `ทวิสเต็ดแมน` and `Anomaly` as `อโนมาลี`, despite earlier output using natural Thai. The same pattern appeared in other chapters through English parentheticals and role labels.

## Root Cause

- `Horror Game Developers/01_Glossary/The Anomaly.md` approved the transliteration `อโนมาลี`, which let later translation/refinement preserve an unnatural term.
- `Horror Game Developers/01_Glossary/Squad Leader.md` contained mojibake in `thai_term`, so the approved Thai term was unusable.
- `scripts/check_output_quality_guardrails.py` did not yet reject this repeated leakage set in HGD final output or MoonRead generated content.

## Repairs Applied

- Updated glossary:
  - `The Anomaly` -> `ความผิดปกติ`
  - `Squad Leader` -> `หัวหน้ากลุ่ม`
- Repaired HGD final Markdown and formatted artifacts for repeated leakage variants, including:
  - `ทวิสเต็ดแมน` / `(Twisted Man)` -> `ชายบิดเบี้ยว`
  - `อโนมาลี` / `(Anomaly)` -> `ความผิดปกติ`
  - `Squad Leader` -> `หัวหน้ากลุ่ม`
  - selected English parentheticals such as `(Scenario)`, `(Hidden Scenario)`, `(Jester)`, `(Crownfall Guild)`, and `Game Developer System`
- Regenerated MoonRead content after repairing the source Markdown.

## Prevention

- Extended `HGD_FORBIDDEN_ENGLISH_OUTPUT` with the reported leakage variants.
- Added regression coverage in `test_translation.py` so known HGD leakage terms are flagged by the output guardrail.
- The next time a repeated glossary leak is found, repair the glossary note first, then repair all affected output, then add the exact leak to the guardrail.

## Validation

- `rg` found no remaining known leakage variants in `Horror Game Developers/05_Output` or `MoonRead/content/generated/books/horror-game-developer/chapters`.
- `python scripts\check_output_quality_guardrails.py --config "D:\Fogust\Workspace\Novel\Horror Game Developers\.system\config.yaml" --chapters ch001-ch220` passed.
- `python -m compileall novel_pipeline` passed.
- `python test_translation.py` passed with `PYTHONIOENCODING=utf-8`.
- MoonRead `npm.cmd run lint`, `npm.cmd run build`, and `npm.cmd run smoke` passed.
