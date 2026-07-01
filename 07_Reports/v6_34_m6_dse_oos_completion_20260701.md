# V6.34 M6 DSE OOS Completion

Date: 2026-07-01
Run ID: `v6-34-m6-dse-oos-v2`
Experiment vault: `Deep Sea Embers/04_Work/_experiments/v6_34_m6_dse_oos_v2`

## Summary

DSE OOS completed validly after rebuilding the experiment vault from current production raw/title sidecars.

This remains experiment output only. It was not published to MoonRead and did not modify production translation outputs.

## Scope

Locked DSE OOS chapters:

`ch009`, `ch029`, `ch047`, `ch070`, `ch088`, `ch095`, `ch124`, `ch143`, `ch148`, `ch174`

## Final Status

- Ledger records: 332
- Completed blocks: 55/55
- Current failed blocks: none
- Manual actions needed: none
- Historical failed records: 1
- Final outputs exist for all 10 sampled chapters
- Source parity: `0` mismatches
- Deterministic output guardrails: passed
- Runtime Sentinel: completed for all 10 sampled chapters

## Incidents And Treatments

### Invalid v1 vault

The first DSE OOS attempt, `v6-34-m6-dse-oos-v1`, was invalid because its raw source files were stale/off-by-one against production raw. It was stopped and recorded separately.

Prevention: use `scripts/verify_experiment_source_parity.py` from the repository root before provider calls and require `0` mismatches.

### `ch029-block-005` Chinese annotation leakage

QA hard-failed because the output retained `[走进不科学]` after a Thai translated book title.

Treatment: added narrow output-side source-script annotation cleanup in the pipeline. Rerun from refine passed QA retry 2.

### `ch174` duplicate title-like body paragraph

Final output guardrail caught a hallucinated standalone title paragraph:

```text
**[ บทที่ 174 ก่อนพายุโหมกระหน่ำ ]**
```

The source body did not contain a chapter title. The line came from provider output in `ch174-block-003`.

Treatment: final assembly now removes standalone title-like paragraphs anywhere in the body when the H1 title is authoritative. Rerun final assembly rewrote `ch174.md`, and output guardrails passed.

## Verification Commands

```powershell
cd "D:\Fogust\Workspace\Novel"
$env:PYTHONIOENCODING='utf-8'
python scripts\verify_experiment_source_parity.py --novel-root "Deep Sea Embers" --experiment-root "Deep Sea Embers\04_Work\_experiments\v6_34_m6_dse_oos_v2" --chapters "ch009,ch029,ch047,ch070,ch088,ch095,ch124,ch143,ch148,ch174"

cd "D:\Fogust\Workspace\Novel\Deep Sea Embers"
python -m compileall novel_pipeline
python test_translation.py

cd "D:\Fogust\Workspace\Novel\Deep Sea Embers\04_Work\_experiments\v6_34_m6_dse_oos_v2"
python scripts\check_output_quality_guardrails.py --chapters ch009,ch029,ch047,ch070,ch088,ch095,ch124,ch143,ch148,ch174
novel-pipeline --config ".system/config.yaml" status --run-id v6-34-m6-dse-oos-v2
```

Results:

- Source parity: `0` mismatches
- Compile: passed
- Test suite: passed
- Output guardrails: passed
- Status: all 55 blocks complete; current failed blocks none; manual actions none

## Provider/Routing Notes

- `openrouter_reasoning` QA was used heavily.
- `deepseek/deepseek-v4-pro` appeared as a QA fallback in some blocks and was slower but returned usable results.
- `google/gemini-3-flash-preview` appeared as QA/format fallback in some blocks.
- The only hard-fail was the `ch029-block-005` local QA hard-fail before treatment.

## Next Safe Action

Run IRS OOS in the isolated experiment vault after verifying source parity and title sidecar readiness. Do not publish DSE OOS experiment output.
