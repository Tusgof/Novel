# V6.34 M5 IRS Treatment Completion

Date: 2026-07-01  
Run ID: `v6-34-m5-irs-treatment-v1`  
Experiment vault: `Infinite Regressor Stories/04_Work/_experiments/v6_34_m5_irs_treatment_v1`

## Scope

Official IRS in-sample treatment chapters:

`ch020`, `ch067`, `ch080`, `ch119`, `ch160`, `ch207`, `ch261`, `ch276`, `ch322`, `ch361`

This was experiment output only. No production `05_Output`, production glossary, production ledger, or MoonRead generated content was modified.

## Final Status

- Completed blocks: `32/32`
- Current failed blocks: none
- Manual actions needed: none
- Final outputs: all 10 chapter Markdown files exist in the experiment vault
- Source parity against production raw: `0` mismatches across all 10 sampled chapters
- Final scoped Sentinel: `blocker/major/minor/info = 0/0/1/0`
- Deterministic output checks:
  - CJK leakage: `0`
  - Thai numeral leakage: `0`
  - provider/meta/glossary-note leakage: `0`
  - quote-only lines: `0`

## Commands Run

```powershell
novel-pipeline --config ".system/config.yaml" resume --run-id v6-34-m5-irs-treatment-v1 --until-chapter ch067 --manual-action-mode stop
novel-pipeline --config ".system/config.yaml" resume --run-id v6-34-m5-irs-treatment-v1 --until-chapter ch080 --manual-action-mode stop
novel-pipeline --config ".system/config.yaml" rerun-block --run-id v6-34-m5-irs-treatment-v1 --block-id ch080-block-003 --from-stage refine
novel-pipeline --config ".system/config.yaml" resume --run-id v6-34-m5-irs-treatment-v1 --until-chapter ch119 --manual-action-mode stop
novel-pipeline --config ".system/config.yaml" resume --run-id v6-34-m5-irs-treatment-v1 --until-chapter ch160 --manual-action-mode stop
novel-pipeline --config ".system/config.yaml" resume --run-id v6-34-m5-irs-treatment-v1 --until-chapter ch207 --manual-action-mode stop
novel-pipeline --config ".system/config.yaml" resume --run-id v6-34-m5-irs-treatment-v1 --until-chapter ch261 --manual-action-mode stop
novel-pipeline --config ".system/config.yaml" rerun-block --run-id v6-34-m5-irs-treatment-v1 --block-id ch261-block-001 --from-stage refine
novel-pipeline --config ".system/config.yaml" resume --run-id v6-34-m5-irs-treatment-v1 --until-chapter ch261 --manual-action-mode stop
novel-pipeline --config ".system/config.yaml" resume --run-id v6-34-m5-irs-treatment-v1 --until-chapter ch276 --manual-action-mode stop
novel-pipeline --config ".system/config.yaml" resume --run-id v6-34-m5-irs-treatment-v1 --until-chapter ch322 --manual-action-mode stop
novel-pipeline --config ".system/config.yaml" resume --run-id v6-34-m5-irs-treatment-v1 --until-chapter ch361 --manual-action-mode stop
novel-pipeline --config ".system/config.yaml" status --run-id v6-34-m5-irs-treatment-v1
python scripts/verify_experiment_source_parity.py --novel-root "D:\Fogust\Workspace\Novel\Infinite Regressor Stories" --experiment-root "D:\Fogust\Workspace\Novel\Infinite Regressor Stories\04_Work\_experiments\v6_34_m5_irs_treatment_v1" --chapters "ch020,ch067,ch080,ch119,ch160,ch207,ch261,ch276,ch322,ch361"
python scripts\sentinel_quality_report.py --scope v6-34-m5-irs-treatment-v1_all_in_sample_final --novel infinite-regressor-stories --chapters ch020,ch067,ch080,ch119,ch160,ch207,ch261,ch276,ch322,ch361 --fail-on major --skip-advisory-english
```

## Measured Outcomes

| Metric | Result |
|---|---:|
| fetched records | 10 |
| glossary_scanned records | 10 |
| glossary_approved records | 10 |
| completed blocks | 32 |
| current failed blocks | 0 |
| historical failed/hard-fail records | 4 |
| OpenRouter translating completed | 32 |
| OpenRouter refining completed | 48 |
| OpenRouter refining failed | 2 |
| OpenRouter QA completed | 32 |
| OpenRouter formatting completed | 26 |
| local formatting completed | 6 |
| local_recovery refining completed | 4 |
| Sentinel completed records | 62 |

## Incidents And Recoveries

### Empty `Footnotes:` marker

Prior blocker from `ch020` was already repaired before this completion round. The prevention stripped only bare trailing `Footnotes:` markers for non-CJK source while preserving real footnotes.

### Missing title sidecars

`ch067` final assembly originally stopped because IRS named English titles after `ch020` had no experiment-local title sidecars. Experiment-only `title.json` files were created for the remaining sampled chapters with roman numerals normalized to Arabic numerals.

### CJK parenthetical leakage

Two blocks hard-failed QA because refined output retained Hanja/Han parenthetical source annotations from the English/Korean source:

- `ch080-block-003`: examples included `君主` and `群主`
- `ch261-block-001`: examples included `千謠話` and `天寥化`

Both were recovered by rerunning from `refine`; the rerun outputs passed QA retry `0`, formatting, final assembly, and scoped Sentinel. This is evidence for a later Layer 1/Layer 0 prevention candidate: non-CJK output should strip or translate source-language parenthetical annotations before final output, while preserving meaning.

### Provider failures

Historical provider failures during the treatment included:

- `ch080-block-003` refining failed once due mojibake Thai output
- `ch207-block-003` refining failed once due empty OpenRouter assistant message

Both were recovered and did not remain current failures.

## Final Sentinel

Final all-sample Sentinel report:

- `Infinite Regressor Stories/04_Work/_experiments/v6_34_m5_irs_treatment_v1/07_Reports/sentinel_quality_v6-34-m5-irs-treatment-v1_all_in_sample_final_20260701_053858.md`
- Result: `blocker/major/minor/info = 0/0/1/0`
- Minor finding: `Complete Memory -> ความทรงจำสมบูรณ์` missing from `ch207` final output despite source containing the approved glossary term.

This minor finding does not block the treatment round under `--fail-on major`, but it should be included in the Milestone 5 comparison.

## Verdict

IRS treatment completed validly. It improved past the `ch020` blocker and completed all 10 sampled chapters, but the run still exposed long-run smoothness risks:

- two QA hard-fails from CJK parenthetical leakage
- two OpenRouter refining failures
- one remaining Sentinel minor glossary coverage miss

Next safe action: compare HGD, DSE, and IRS treatment metrics together before opening Milestone 6 out-of-sample.
