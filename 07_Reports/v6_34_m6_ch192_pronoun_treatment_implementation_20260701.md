# V6.34 M6 ch192 Pronoun Treatment Implementation

Date: 2026-07-01

## Summary

`ch192-block-001` stopped during HGD OOS QA because literal-safe omission recovery preserved peer-dialogue `คุณ` where HGD policy expects casual `นาย`.

Treatment implemented:

- Added a narrow HGD-only peer-address repair helper in `novel_pipeline/pipeline.py`.
- Applied it only after `qa_omission_literal_safe_refined_text` recovery.
- Preserved `คุณ` in normal system/formal contexts by avoiding broad `คุณ -> นาย` replacement.
- Added regression coverage that the helper is scoped to `novel_id: horror-game-developer` and preserves `ขอบคุณ`.

## Cause

The failure was not provider outage and not glossary collision.

Root cause:

1. The normal refinement route omitted major source content.
2. The pipeline correctly invoked literal-safe omission recovery.
3. Literal-safe recovery restores source coverage but bypasses novel-specific prose refinement.
4. That recovery path did not yet reapply HGD peer-address policy.
5. QA caught the resulting `คุณ` / `นาย` drift and stopped.

Layer classification:

- Layer 2: HGD novel-specific pronoun policy.
- Layer 0 hook: shared pipeline recovery path now has a novel-scoped post-recovery cleanup point.

## Files Changed

- `Deep Sea Embers/novel_pipeline/pipeline.py`
- `Deep Sea Embers/test_translation.py`

Experiment artifacts changed only inside isolated vault:

- `Horror Game Developers/04_Work/_experiments/v6_34_m6_hgd_oos_v1/04_Work/ch192/ch192-block-001.refined.json`
- `Horror Game Developers/04_Work/_experiments/v6_34_m6_hgd_oos_v1/04_Work/ch192/ch192-block-001.qa.json`
- `Horror Game Developers/04_Work/_experiments/v6_34_m6_hgd_oos_v1/04_Work/ch192/ch192-block-001.formatted.json`
- `Horror Game Developers/04_Work/_experiments/v6_34_m6_hgd_oos_v1/05_Output/ch192/ch192.md`

## Verification

Commands:

```powershell
cd "D:\Fogust\Workspace\Novel\Deep Sea Embers"
python -m compileall novel_pipeline
$env:PYTHONIOENCODING='utf-8'
python test_translation.py
```

Results:

- `compileall`: passed
- `test_translation.py`: passed

Rerun command:

```powershell
cd "D:\Fogust\Workspace\Novel\Horror Game Developers\04_Work\_experiments\v6_34_m6_hgd_oos_v1"
$env:PYTHONIOENCODING='utf-8'
novel-pipeline --config ".system/config.yaml" rerun-block --run-id v6-34-m6-hgd-oos-v1 --block-id ch192-block-001 --from-stage refine
```

Rerun result:

- QA passed with `retry_count: 2`
- QA feedback: `PASS: The refined preserves all source content, correctly applies glossary terms, uses stable Seth pronouns (ผม), and adjusts peer address to นาย per style, with no omissions or tone drift.`
- Runtime Sentinel: `0/0/0/0`
- Current failed blocks: none
- Completed HGD OOS chapters: 8/10
- Pending HGD OOS chapters: `ch226`, `ch262`

Phrase spot-check in final experiment output:

| Check | Count |
|---|---:|
| `ถ้าคุณมีอุปกรณ์อิเล็กทรอนิกส์` | 0 |
| `ถ้านายมีอุปกรณ์อิเล็กทรอนิกส์` | 1 |
| `คุณฉลาดไม่เบาเลยนะ` | 0 |
| `นายฉลาดไม่เบาเลยนะ` | 1 |
| `ขอบคุณ` | 1 |

## Next Safe Action

Resume HGD OOS from `ch226` and stop on the next QA hard-fail, Sentinel blocker/major, provider failure, validation failure, or scope expansion.

