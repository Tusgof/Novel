# V6.34 M5 DSE Treatment Source Mismatch Stop

Date: 2026-07-01

## Summary

DSE treatment measurement was started in isolated vault `Deep Sea Embers/04_Work/_experiments/v6_34_m5_dse_treatment_v1`, but stopped at `ch017` before final output assembly. The invalid vault was then quarantined to `Deep Sea Embers/04_Work/_experiments/v6_34_m5_dse_treatment_v1_invalid_source_mismatch_20260701` to prevent accidental resume.

The immediate error was:

```text
Chapter title violates approved glossary for ch017: 灵界 -> มิติวิญญาณ; 灵界行走 -> การเดินทางในมิติวิญญาณ; got 'บทที่ 17: ถ้ำ'
```

Inspection showed the deeper cause: the experiment vault raw source for all 10 sampled DSE chapters was stale/off-by-one compared with current production raw source. Therefore the `ch017` translation artifacts created during this attempt are invalid experiment data and must not be used for measurement or publication.

## Raw Source Parity Findings

The new read-only checker `scripts/verify_experiment_source_parity.py` was added to prevent this class of failure.

Command:

```powershell
python scripts/verify_experiment_source_parity.py --novel-root "Deep Sea Embers" --experiment-root "Deep Sea Embers/04_Work/_experiments/v6_34_m5_dse_treatment_v1" --chapters "ch017,ch034,ch048,ch060,ch081,ch094,ch114,ch142,ch161,ch168"
```

Result: 10 mismatches / 10 checked chapters.

| Chapter | Experiment title | Current production title |
|---|---|---|
| `ch017` | `第十六章 灵界行走` | `第十七章 洞穴` |
| `ch034` | `第三十三章 鱼` | `第三十四章 丰收` |
| `ch048` | `第四十七章 在圣像前` | `第四十八章 警觉` |
| `ch060` | `第五十九章 此门通往失乡号` | `第六十章 门对面` |
| `ch081` | `第八十章 家访？` | `第八十一章 记忆偏差` |
| `ch094` | `第九十三章 “这是常识”` | `第九十四章 妮娜的怪梦` |
| `ch114` | `第114章 寻找一场大火` | `第115章 被抹去的痕迹` |
| `ch142` | `第142章 诚实可靠邓肯先生` | `第143章 问询与治疗` |
| `ch161` | `第161章 最杰出的人偶师` | `第162章 另一重联系` |
| `ch168` | `第168章 高规格举报` | `第169章 警兆蔓延` |

## Status At Stop

- `ch017-block-001` through `ch017-block-005`: completed in ledger, but based on stale experiment raw.
- `05_Output/ch017/ch017.md`: missing because final assembly stopped.
- `ch034` through `ch168`: not translated in this treatment vault.
- Production `05_Output`: unchanged.
- MoonRead: unchanged.

## Cause

The DSE experiment vault was copied from the M3 baseline experiment state. That baseline experiment state contained stale raw files whose chapter IDs no longer matched the current DSE production raw source. The existing gate checked ledger readiness but did not compare experiment raw files against the current production raw files before treatment resume.

## Prevention

Before any treatment or OOS experiment resume:

1. Run `scripts/verify_experiment_source_parity.py` for the exact sampled chapter list.
2. Require `mismatch_count = 0`.
3. If mismatches exist, rebuild the experiment vault from current production `03_Raw` and title sidecars before provider calls.
4. Treat any provider output generated from mismatched raw as invalid experiment data.

## Next Step

Rebuild a fresh DSE treatment vault from current production raw source, verify source parity, then restart DSE treatment measurement from `ch017`.
