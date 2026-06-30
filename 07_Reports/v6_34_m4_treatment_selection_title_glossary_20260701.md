# V6.34 M4 Treatment Selection: Title Glossary Guard

Date: 2026-07-01

## Summary

Milestone 4 selected the smallest treatment for the HGD `ch037` baseline stop:

1. Fix the HGD canonical title map for `Velora Art Museum` from `พิพิธภัณฑ์ศิลปะเวลอรา` to approved glossary `พิพิธภัณฑ์ศิลปะเวโลรา`.
2. Add deterministic runtime validation before final chapter assembly: if a source title contains an approved glossary original term or alias, the resolved Thai title/H1 must contain the approved `thai_term`.

This does not change translation prose. It only prevents a known title/glossary drift from entering final Markdown.

## Evidence From Baseline

| Item | Evidence |
|---|---|
| Source title | `Chapter 37 - Velora Art Museum [2]` |
| Approved glossary | `Velora Art Museum -> พิพิธภัณฑ์ศิลปะเวโลรา`; alias `Art Museum` |
| Baseline title sidecar | `ตอนที่ 37 - พิพิธภัณฑ์ศิลปะเวลอรา` |
| Baseline final H1 | `# ตอนที่ 37 - พิพิธภัณฑ์ศิลปะเวลอรา` |
| Sentinel result | major glossary coverage miss |

## Layer Classification

| Treatment | Layer | Reason |
|---|---|---|
| Runtime title/H1 glossary validation | Layer 0 shared guardrail | Any novel with source titles and approved glossary can hit this drift |
| HGD `Velora Art Museum` map correction | Layer 2 HGD profile/artifact policy | The wrong Thai spelling is HGD-specific |

## Expected Metric Movement

| Metric | Expected Movement |
|---|---|
| Sentinel glossary coverage major findings | HGD title-related misses should decrease |
| Manual repairs | Fewer one-off title sidecar repairs |
| Translation quality | No negative effect; treatment does not alter body prose |
| Long-run sustainability | Better early stop before invalid title/H1 output is assembled |

## Implementation

Files changed:

- `Deep Sea Embers/novel_pipeline/pipeline.py`
- `Deep Sea Embers/test_translation.py`
- `Deep Sea Embers/scripts/repair_user_reported_quality_issues.py`
- `Horror Game Developers/scripts/normalize_hgd_titles.py`

## Verification

- `python -m compileall novel_pipeline scripts\sentinel_quality_report.py scripts\translate_chapter_titles.py scripts\repair_user_reported_quality_issues.py`: passed
- `python test_translation.py`: passed

## Next Step

Run Milestone 5 treatment rerun in isolated experiment state. Do not publish experiment output to MoonRead.
