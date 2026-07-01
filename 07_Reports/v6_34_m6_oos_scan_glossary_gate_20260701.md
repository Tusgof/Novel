# V6.34 M6 OOS Scan And Glossary Gate

Date: 2026-07-01

## Summary

V6.34 Milestone 6.1 completed for the locked out-of-sample chapters across Deep Sea Embers, Horror Game Developer, and Infinite Regressor Stories.

This was an experiment-only scan/glossary gate. No production output, MoonRead content, or production glossary state was changed.

## Scope

| Novel | Experiment vault | Run ID | OOS chapters |
|---|---|---|---|
| Deep Sea Embers | `Deep Sea Embers/04_Work/_experiments/v6_34_m6_dse_oos_v1` | `v6-34-m6-dse-oos-v1` | `ch009,ch029,ch047,ch070,ch088,ch095,ch124,ch143,ch148,ch174` |
| Horror Game Developer | `Horror Game Developers/04_Work/_experiments/v6_34_m6_hgd_oos_v1` | `v6-34-m6-hgd-oos-v1` | `ch015,ch046,ch060,ch101,ch131,ch153,ch184,ch192,ch226,ch262` |
| Infinite Regressor Stories | `Infinite Regressor Stories/04_Work/_experiments/v6_34_m6_irs_oos_v1` | `v6-34-m6-irs-oos-v1` | `ch012,ch053,ch095,ch144,ch187,ch208,ch258,ch290,ch323,ch372` |

## Source Parity

Before the scan gate, every experiment vault was verified against the current production raw source for the exact OOS chapters.

| Novel | Result |
|---|---:|
| Deep Sea Embers | `0` mismatches |
| Horror Game Developer | `0` mismatches |
| Infinite Regressor Stories | `0` mismatches |

## Scan Results

| Novel | Fetched records | Glossary scanned records | Candidate terms | Scan command result |
|---|---:|---:|---:|---|
| Deep Sea Embers | 10 | 10 | 34 | exit 0 |
| Horror Game Developer | 10 | 10 | 17 | exit 0 |
| Infinite Regressor Stories | 10 | 10 | 155 | exit 0 |

Decision report files were created inside each experiment vault:

- `Deep Sea Embers/04_Work/_experiments/v6_34_m6_dse_oos_v1/07_Reports/v6_34_m6_oos_glossary_gate_decisions_v6-34-m6-dse-oos-v1.md`
- `Horror Game Developers/04_Work/_experiments/v6_34_m6_hgd_oos_v1/07_Reports/v6_34_m6_oos_glossary_gate_decisions_v6-34-m6-hgd-oos-v1.md`
- `Infinite Regressor Stories/04_Work/_experiments/v6_34_m6_irs_oos_v1/07_Reports/v6_34_m6_oos_glossary_gate_decisions_v6-34-m6-irs-oos-v1.md`

## OOS Glossary Policy

No new glossary terms were approved from OOS candidates.

Reason: M6 is a generalization check. Approving new OOS terms before translation would tune the experiment on out-of-sample data and weaken the measurement.

Action taken:

- All new OOS candidates were held as a watchlist.
- `glossary_approved` records were committed for the batch so translation can proceed using the existing copied glossary state.
- No production `01_Glossary/` files were created or modified.

## Ledger Status After Approval

| Novel | Ledger records | Fetched | Scanned | Approved | Translation/refine/QA/format/completed | Current failed blocks |
|---|---:|---:|---:|---:|---:|---:|
| Deep Sea Embers | 30 | 10 | 10 | 10 | 0 | 0 |
| Horror Game Developer | 30 | 10 | 10 | 10 | 0 | 0 |
| Infinite Regressor Stories | 30 | 10 | 10 | 10 | 0 | 0 |

Next effective action for each run is `resume --run-id <run-id>`.

## Guardrails Confirmed

- No translation, refinement, QA, formatting, Sentinel, or completed records exist yet for the OOS runs.
- No production `05_Output/` files were created.
- No MoonRead files were changed.
- No production ledger or glossary files were edited.
- Experiment vaults remain isolated from product output.

## Next Action

Proceed to M6.2 only after preparing any required experiment-local title sidecars, especially for Infinite Regressor Stories chapters whose production `04_Work/<chapter>/title.json` sidecars were not present when the OOS vault was created.

Then run OOS translation/refine/QA/format/Sentinel without tuning on OOS failures mid-round.
