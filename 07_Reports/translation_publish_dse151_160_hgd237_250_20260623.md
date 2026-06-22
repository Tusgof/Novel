# Translation And MoonRead Publish Checkpoint - 2026-06-23

## Scope

- Deep Sea Embers: `dse-ch151-ch160-v1`, chapters `ch151` through `ch160`
- Horror Game Developer: `hgd-ch237-ch250-v2`, chapters `ch237` through `ch250`
- MoonRead publication: Deep Sea Embers through `ch160`; Horror Game Developer through `ch250`

## Results

- DSE: 60/60 blocks complete, no current failed blocks, final outputs exist.
- HGD: 14/14 blocks complete, no current failed blocks, final outputs exist.
- MoonRead generated reader library: 2 books, 410 available chapters, 0 missing, 0 rejected.

## HGD Source Mapping Incident

`hgd-ch237-ch250-v1` was abandoned because the fetch resolver selected manifest ordinal IDs. Local `ch237` incorrectly fetched source Chapter 253. Runtime artifacts from the bad run were removed before `hgd-ch237-ch250-v2`.

Prevention added:

- `resolve_chapter_meta()` now prefers `metadata.site_chapter` when the requested local id is numeric.
- `check_source_chapter_sequence.py` now fails if local chapter id and source chapter number differ.
- Verified after repair: `ch237` source Chapter 237 through `ch250` source Chapter 250.

## Bounded Repairs

- DSE `ch158-block-006`: repaired `ค้างคาใจ` meaning drift to `เหม่อลอย`; QA passed after rerun.
- HGD `ch243-block-001`: repaired Seth first-person pronoun drift to `ผม` and normalized `Squad Leader` to `หัวหน้ากลุ่ม`; QA passed after rerun.
- HGD `ch244-block-001`: removed hallucinated `ระดับ E`; QA passed after rerun.
- HGD `ch246-block-001`: removed hallucinated `<D>/<C>` rank values and normalized Team Leader wording to `หัวหน้ากลุ่ม`; QA passed after rerun.
- HGD final Markdown: removed approved-glossary English parentheticals and normalized paragraph spacing for MoonRead.

## Validation

- `python -m compileall novel_pipeline`: passed.
- `PYTHONIOENCODING=utf-8 python test_translation.py`: passed.
- DSE output guardrail for `ch151-ch160`: passed.
- HGD output guardrail for `ch237-ch250`: passed.
- DSE Sentinel: `0/0/0/0`, report `07_Reports/sentinel_quality_dse-ch151-ch160-20260623_20260622_205216.md`.
- HGD Sentinel final: `0/0/0/0`, report `07_Reports/sentinel_quality_hgd-ch237-ch250-20260623-final_20260622_205328.md`.
- MoonRead `npm run generate:chapters`: passed.
- MoonRead `npm run lint`: passed.
- MoonRead `npm run build`: passed.
- MoonRead `npm run smoke`: passed (`ok: true`, HGD available `250`).

## Spot Check

Sampled chapter openings/endings:

- DSE `ch151`, `ch157`, `ch158`, `ch160`
- HGD `ch237`, `ch243`, `ch246`, `ch250`

No blocker-level issue was found in the sampled title/opening/ending checks after deterministic repairs.
