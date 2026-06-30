# V6.34 Milestone 2: Source Pool Audit And Cross-Novel Sample Manifest

Date: 2026-07-01  
Seed: `634001`  
Scope: Deep Sea Embers, Horror Game Developer, Infinite Regressor Stories  
Mode: read-only audit and manifest generation; no provider calls; no translation; no MoonRead publication

## Source Pool Audit

| Novel | Raw Path | Count | Min | Max | Gaps | Missing `source.json` | Unreadable `source.json` |
|---|---|---:|---:|---:|---:|---:|---:|
| Deep Sea Embers | `Deep Sea Embers/03_Raw` | 180 | 1 | 180 | 0 | 0 | 0 |
| Horror Game Developer | `Horror Game Developers/03_Raw` | 270 | 1 | 270 | 0 | 0 | 0 |
| Infinite Regressor Stories | `Infinite Regressor Stories/03_Raw` | 394 | 1 | 394 | 0 | 0 | 0 |

Conclusion: all three raw source pools are locally complete within their verified boundaries. No fetch is required before this V6.34 sample.

## Sampling Method

- Fixed seed: `634001`
- Sampling source: verified `03_Raw/` directories only
- Strata: 10 equal chapter-number strata per novel
- Selection: 2 random chapters per stratum, first assigned to `in_sample`, second assigned to `out_of_sample`
- Total sample size: 60 chapters
  - 30 in-sample chapters
  - 30 out-of-sample chapters
- Production isolation: these selections are experiment targets only and must not be published to MoonRead during V6.34

## Sample Manifest

| Novel | Stratum | Range | In-Sample | Out-Of-Sample |
|---|---:|---|---|---|
| DSE | 1 | ch001-ch018 | ch017 | ch009 |
| DSE | 2 | ch019-ch036 | ch034 | ch029 |
| DSE | 3 | ch037-ch054 | ch048 | ch047 |
| DSE | 4 | ch055-ch072 | ch060 | ch070 |
| DSE | 5 | ch073-ch090 | ch081 | ch088 |
| DSE | 6 | ch091-ch108 | ch094 | ch095 |
| DSE | 7 | ch109-ch126 | ch114 | ch124 |
| DSE | 8 | ch127-ch144 | ch142 | ch143 |
| DSE | 9 | ch145-ch162 | ch161 | ch148 |
| DSE | 10 | ch163-ch180 | ch168 | ch174 |
| HGD | 1 | ch001-ch027 | ch024 | ch015 |
| HGD | 2 | ch028-ch054 | ch037 | ch046 |
| HGD | 3 | ch055-ch081 | ch066 | ch060 |
| HGD | 4 | ch082-ch108 | ch103 | ch101 |
| HGD | 5 | ch109-ch135 | ch132 | ch131 |
| HGD | 6 | ch136-ch162 | ch142 | ch153 |
| HGD | 7 | ch163-ch189 | ch170 | ch184 |
| HGD | 8 | ch190-ch216 | ch196 | ch192 |
| HGD | 9 | ch217-ch243 | ch225 | ch226 |
| HGD | 10 | ch244-ch270 | ch250 | ch262 |
| IRS | 1 | ch001-ch039 | ch020 | ch012 |
| IRS | 2 | ch040-ch078 | ch067 | ch053 |
| IRS | 3 | ch079-ch118 | ch080 | ch095 |
| IRS | 4 | ch119-ch157 | ch119 | ch144 |
| IRS | 5 | ch158-ch197 | ch160 | ch187 |
| IRS | 6 | ch198-ch236 | ch207 | ch208 |
| IRS | 7 | ch237-ch275 | ch261 | ch258 |
| IRS | 8 | ch276-ch315 | ch276 | ch290 |
| IRS | 9 | ch316-ch354 | ch322 | ch323 |
| IRS | 10 | ch355-ch394 | ch361 | ch372 |

## Validation

- Every selected chapter is inside the verified raw source boundary for its novel.
- Every selected chapter has a readable `source.json`.
- The manifest includes all three novels equally.
- No selected chapter was chosen from `05_Output/`, MoonRead generated content, or a hand-picked known-problem list.

## Next Step

Proceed to V6.34 Milestone 3: run the full baseline round on the 30 in-sample chapters in isolated experiment state, starting with scan-only and glossary gates. Do not apply systemic fixes during the baseline round.
