# V6.34 M6 DSE OOS Stop: Source Parity Failure

Date: 2026-07-01
Run ID: `v6-34-m6-dse-oos-v1`
Experiment vault: `Deep Sea Embers/04_Work/_experiments/v6_34_m6_dse_oos_v1`

## Summary

DSE OOS translation must stop. The run completed five sampled chapters worth of blocks, but final assembly for `ch088` exposed that the experiment vault was using stale/off-by-one raw source files.

This is not production output. No MoonRead publication was performed.

## Current Run State

- Records: 182
- Completed blocks: 28
- Completed chapter blocks:
  - `ch009`: 5/5
  - `ch029`: 5/5
  - `ch047`: 6/6
  - `ch070`: 6/6
  - `ch088`: 6/6
- Current failed blocks: none
- Historical failed records: 0
- `ch088` final output: missing because final assembly is blocked

## Stop Trigger

Attempted bounded final assembly via:

```powershell
novel-pipeline --config ".system/config.yaml" rerun-block --run-id v6-34-m6-dse-oos-v1 --block-id ch088-block-006 --from-stage formatting
```

The command stopped with:

```text
Chapter title violates approved glossary for ch088: 凡娜 -> ฟานน่า; got 'บทที่ 88: มีของจริงอยู่ชิ้นหนึ่ง'
```

Inspection showed the deeper cause:

| Chapter | Production raw title | Experiment raw title | Experiment title sidecar |
|---|---|---|---|
| `ch088` | `第八十八章 有一件真货` | `第八十七章 凡娜的调查结论` | `第八十八章 有一件真货` |

The final assembly guard correctly blocked because the raw source in the experiment vault contained `凡娜`, while the stale title sidecar belonged to the next source chapter.

## Source Parity Verification

Command:

```powershell
python scripts\verify_experiment_source_parity.py --novel-root "Deep Sea Embers" --experiment-root "Deep Sea Embers\04_Work\_experiments\v6_34_m6_dse_oos_v1" --chapters "ch009,ch029,ch047,ch070,ch088,ch095,ch124,ch143,ch148,ch174"
```

Result:

```text
Checked 10 chapters
Mismatches: 10
```

All 10 locked DSE OOS chapters had `title_mismatch`, `source_url_mismatch`, and `raw_text_hash_mismatch`.

## Root Cause

The experiment vault copied stale DSE `03_Raw` source files that are one chapter behind the current production vault. The existing parity checker detects this correctly, but the DSE OOS resume was started without a confirmed fresh parity pass immediately before provider calls.

Layer classification:

- Layer 0 / workflow guard: parity must be enforced immediately before experiment provider calls.
- Layer 2 / DSE vault state: this specific DSE OOS experiment vault is stale and invalid for measurement.

## Prevention

Do not continue this DSE OOS vault. Rebuild a fresh DSE OOS experiment vault from current production:

- `03_Raw/`
- `04_Work/<chapter>/title.json`
- `03_Raw/manifest.json` if used by the setup step

Then rerun `scripts\verify_experiment_source_parity.py` from the repository root against the exact locked OOS chapters. Provider calls may resume only if mismatches are `0`.

## Next Safe Action

Rebuild `Deep Sea Embers/04_Work/_experiments/v6_34_m6_dse_oos_v1` or create a fresh `v6_34_m6_dse_oos_v2` from current production raw/title sidecars, verify source parity `0`, then restart DSE OOS from the beginning. Treat the existing partial DSE OOS output as invalid measurement data.
