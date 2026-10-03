# DSE Lean retranslation checkpoint: ch011–ch020

Order: `DSE-LEAN-REST-20261003`  
Repository base: `79c3e0ad360bd76a16981a25e1707e62c0e9581b` on `main`  
Range: `ch011–ch020`  
Status: **complete**

All ten chapters passed QA, deterministic output guardrails, and blocking Sentinel, then were promoted to `Deep Sea Embers/05_Output`. Neither bounded run has a failed chapter or remaining quarantine.

## Bounded runs and metering

| Run ID | Range | Status | Promoted | Provider calls | Provider failures | Measured cost |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| `dse-lean-rest-20261003-ch011-ch015-v1` | ch011–ch015 | complete | 5 | 56 | 10 | 0.1944300360 |
| `dse-lean-rest-20261003-ch016-ch020-v1` | ch016–ch020 | complete after resume | 5 | 60 | 9 | 0.2074246142 |
| **Total** | **ch011–ch020** | **complete** | **10** | **116** | **19** | **0.4018546502** |

Provider failures were recovered through configured routes; global route exhaustion did not occur. The ch016–ch020 run initially quarantined ch020 after QA reported: `QA disagreement unresolved: the fallback PASS did not quote a source passage and its corresponding Thai passage verbatim.` Resuming the same run reused ch020's valid literal and refined checkpoints and retried QA. The primary QA route returned an empty response at its completion limit; the configured fallback returned PASS, after which ch020 passed Sentinel and was promoted. No manual override or force-accept was used.

## Repairs

- Restored the approved `人偶爱丽丝 → ตุ๊กตาอลิซ` mapping in ch012.
- Removed the source-unsupported `ฟูลสต็อป` reference and invented standalone ellipsis dialogue from ch013; checked against the source. Neither remains in the final chapter.
- Reflowed only the previously reported dense paragraphs in ch011, ch013, ch015–ch018, and ch020, preserving wording and meaning.

## Gates and spot-check

- **Chapter QA:** pass for ch011–ch020. Every per-chapter run result is `promoted` with `qa_passed=true`.
- **Per-chapter Sentinel:** pass for all ten chapters; zero blockers and majors.
- **Deterministic output guardrails:** `scripts/check_output_quality_guardrails.py --config "Deep Sea Embers/.system/config.yaml" --chapters ch011-ch020` — passed.
- **Independent blocking Sentinel:** `scripts/sentinel_quality_report.py --novel deep-sea-embers --chapters ch011-ch020 --scope dse-lean-rest-20261003-ch011-ch020-final --fail-on major` — passed with 0 blockers, 0 majors, 0 minors, and 0 info findings.
- **Source-aligned spot-check:** reviewed titles plus opening, middle, and ending passages in ch011, ch012, ch015, ch018, and ch020. Sampled source details, character names, dialogue, and chapter endings align with the Thai output. Also rechecked ch013's localized repairs against its source.

## Evidence

- Run checkpoints and reports: `Deep Sea Embers/04_Work/_lean_runs/dse-lean-rest-20261003-ch011-ch015-v1/lean_run_report.json` and `Deep Sea Embers/04_Work/_lean_runs/dse-lean-rest-20261003-ch016-ch020-v1/lean_run_report.json`.
- Per-run Sentinel reports: `07_Reports/sentinel_quality_lean-dse-lean-rest-20261003-ch011-ch015-v1_20261003_125531.md`, `07_Reports/sentinel_quality_lean-dse-lean-rest-20261003-ch011-ch015-v1_20261003_125532.md`, and `07_Reports/sentinel_quality_lean-dse-lean-rest-20261003-ch016-ch020-v1_20261003_131020.md`.
- Independent Sentinel report: `07_Reports/sentinel_quality_dse-lean-rest-20261003-ch011-ch020-final_20261003_131245.md` and its JSON companion.
- Final translated chapters: `Deep Sea Embers/05_Output/ch011/ch011.md` through `Deep Sea Embers/05_Output/ch020/ch020.md`.

Verification used UTF-8 console settings for every Python invocation. No routing change, force-accept, publication, commit, or push was performed.
