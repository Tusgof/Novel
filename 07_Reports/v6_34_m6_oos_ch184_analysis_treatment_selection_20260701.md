# V6.34 M6 ch184 Analysis And Treatment Selection

Date: 2026-07-01

## Summary

HGD OOS `ch184-block-001` stopped on QA hard-fail after retry 2. Analysis found two issues:

1. Layer 0 glossary subset resolver false positive: `Enter` matched inside the word `Entering`, so QA expected `ปุ่ม Enter` even though the source did not contain a UI `[Enter]` key.
2. Run-local semantic drift in refined text: internal thought introduced `สะกดรอยตาม`, which is not in the source. The source says Kyle may be the only one who can see the missing person in the photo.

Selected treatment:

- Fix `_resolve_glossary_subset()` to use boundary-aware matching for alphabetic source keys.
- Add regression coverage for `Enter` not matching `Entering`.
- Rerun `ch184-block-001` from `refine` after the resolver fix, so the pipeline can repair semantic drift through normal QA feedback instead of manual output patching.

## Evidence

Source contains:

- `Entering the orphanage, I closed the door behind me.`
- No `[Enter]` UI key in this block.

QA artifact:

- `Horror Game Developers/04_Work/_experiments/v6_34_m6_hgd_oos_v1/04_Work/ch184/ch184-block-001.qa.json`

QA findings:

- Expected term not found: `ปุ่ม Enter`
- Internal thought mistranslation: `สะกดรอยตาม`

Implementation source:

- `Deep Sea Embers/novel_pipeline/pipeline.py`
- `_resolve_glossary_subset()` currently collects candidates with `if entry.status == "approved" and key in text`

## Layer Decision

| Issue | Layer | Decision |
|---|---|---|
| `Enter` matched inside `Entering` | Layer 0 multi-novel | Fix glossary subset resolver boundary matching |
| `สะกดรอยตาม` semantic drift | Layer 3 run-local recovery unless repeated | Rerun from refine after resolver fix; do not add broad prompt change yet |
| MoonRead | Layer 4 | No change |

## Expected Metric Movement

| Metric | Expected movement |
|---|---|
| False glossary expectation | `Enter` should not be included for source text containing only `Entering` |
| QA hard-fail | `ch184` should no longer fail for missing `ปุ่ม Enter` |
| Semantic drift | QA retry should be able to correct or reject the refined text without manual force-accept |

## Next Action

Implement boundary-aware glossary subset matching, run tests, then rerun `ch184-block-001` from `refine`.
