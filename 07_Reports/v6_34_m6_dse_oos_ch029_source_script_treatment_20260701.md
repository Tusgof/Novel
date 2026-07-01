# V6.34 M6 DSE OOS ch029 Treatment: Source-Script Annotation Leakage

Date: 2026-07-01
Run ID: `v6-34-m6-dse-oos-v2`
Block: `ch029-block-005`

## Summary

DSE OOS v2 stopped at `ch029-block-005` after QA hard-failed on untranslated source-script leakage. The leaked text was a bracketed Chinese book title in an author promo line:

```text
"ก้าวสู่ความไม่เป็นวิทยาศาสตร์" [走进不科学]
```

The Thai translation was already present, so the bracketed Chinese annotation was redundant and invalid for final Thai output.

## Root Cause

Layer classification:

- Layer 0 output cleanup / validation: final Thai output must not contain CJK source-script annotations when the Thai wording already exists.
- Run-local trigger: the source chapter contains an author promo/recommendation line with a Chinese title.

Existing non-CJK source cleanup did not cover this case because DSE is Chinese source, but the output-side rule is still generic: source-script bracket annotations should not survive into Thai output.

## Treatment Implemented

Added `_apply_source_script_annotation_repairs()` in `Deep Sea Embers/novel_pipeline/pipeline.py`.

The helper removes narrow leaked source-script annotations:

- `[走进不科学]`
- `（走进不科学）`
- `《走进不科学》`

It is applied in the existing refine retry/recovery cleanup paths before QA validation, alongside glossary rejected-variant repairs, redacted-rank repairs, and source footnote marker repairs.

Regression test added in `Deep Sea Embers/test_translation.py`:

- keeps Thai title text
- removes the bracketed Chinese source title
- records the repair metadata

## Verification

Commands:

```powershell
cd "D:\Fogust\Workspace\Novel\Deep Sea Embers"
python -m compileall novel_pipeline
$env:PYTHONIOENCODING='utf-8'
python test_translation.py
```

Both passed.

Recovery command:

```powershell
cd "D:\Fogust\Workspace\Novel\Deep Sea Embers\04_Work\_experiments\v6_34_m6_dse_oos_v2"
$env:PYTHONIOENCODING='utf-8'
novel-pipeline --config ".system/config.yaml" rerun-block --run-id v6-34-m6-dse-oos-v2 --block-id ch029-block-005 --from-stage refine
```

Result:

- QA passed after retry 2
- `ch029-block-005.formatted.json` exists
- `05_Output/ch029/ch029.md` exists
- refined/formatted/final output contain no Han Chinese characters
- current failed blocks: none

## Next Safe Action

Resume `v6-34-m6-dse-oos-v2` from the next pending chapter `ch047`, keeping the same stop conditions.
