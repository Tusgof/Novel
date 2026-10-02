# V6.36 HGD Lean Follow-up: Cleaner Regression And Provider Block

## 1. Scope

- Novel: Horror Game Developer
- Experiment only: `04_Work/_experiments/`
- Target: `ch001`
- Runs: `v6_36_lean_hgd_ch001_v4_projected_20261003`, then
  `v6_36_lean_hgd_ch001_v5_cleaner_20261003`

## 2. Finding

The v4 run stopped at deterministic QA with:

`Approved glossary term was removed during refinement: Nightmare Forge Studios -> สตูดิโอไนต์แมร์ฟอร์จ`

The provider trace showed that the Thai term was present in the provider's
refinement response. The shared refinement cleaner treated every line starting
with `*` as disposable metadata. In this chapter, a review/prose line started
with Markdown emphasis and contained the approved term, so the cleaner removed
the complete line before QA saw it.

## 3. Change

`Deep Sea Embers/novel_pipeline/stages/refine.py` now removes only list/fence
markers (`- `, `* `, headings, and code fences). It preserves story lines that
begin with `*`, including sound effects and italicized prose. This is a
deterministic shared fix because it affects any novel using the refinement
cleaner, while the HGD prompt remains novel-specific.

Regression coverage was added to `Deep Sea Embers/test_translation.py` and the
full test runner invokes it.

## 4. Verification

- `python -m compileall novel_pipeline scripts\\run_lean_pipeline_experiment.py`: passed
- `python test_translation.py`: passed, `All tests passed!`
- `git diff --check`: passed
- HGD v5 provider rerun: blocked, not accepted

## 5. Provider block

HGD v5 completed literal translation, then the refinement provider returned an
empty assistant response after `328.65s` with `finish_reason=length` and
`completion_tokens=12000`. Metrics: 2 provider calls, 1 provider failure,
measured cost `$0.0317234286`. No final chapter, formatting, Sentinel, or
publication artifact was accepted.

## 6. Decision

The cleaner diagnosis and repair are verified by code tests, but Lean is **not
ready for adoption**. The locked A/B/OOS evidence is incomplete and provider
reliability remains a blocking risk. Do not publish the HGD experiment output or
change production provider routing without a separate approved work order.
