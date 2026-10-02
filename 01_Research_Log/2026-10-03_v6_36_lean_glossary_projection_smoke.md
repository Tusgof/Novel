# V6.36 Lean Glossary Projection Smoke

- Date: 2026-10-03 (Asia/Bangkok)
- Scope: experiment harness only; HGD `ch001`; no production output or MoonRead publication
- Run: `v6-36-lean-hgd-ch001-v4-projected`
- Artifacts: `Horror Game Developers/04_Work/_experiments/v6_36_lean_hgd_ch001_v4_projected_20261003/`

## Change under test

Approved, chapter-relevant glossary entries are replaced directly in a projected source copy before the literal Gemini call. Terms are replaced longest-first, English terms use word boundaries, and the original source remains available to refinement and QA. The literal prompt receives no glossary list. Harvested terms remain `proposed`.

## Evidence

- The literal call completed and its trace contained `Use the glossary exactly where applicable: none`.
- The literal trace did not contain the original `Nightmare Forge Studios` source term and did contain the projected Thai glossary text.
- Refinement completed, but blocking QA stopped the run because refinement removed the approved `Nightmare Forge Studios` mapping.
- Provider metrics: 2 calls, 0 provider failures, 12,737 total tokens, measured cost `$0.01822778305`.
- No final chapter output, production glossary mutation, or MoonRead publication occurred.

## Interpretation

The simplified projection path works at the literal-input boundary and removes the need to attach a glossary list to that call. The smoke is not a quality pass because chapter-level refinement dropped an approved term. This remains an isolated treatment finding to classify and address before the locked A/B sample.
