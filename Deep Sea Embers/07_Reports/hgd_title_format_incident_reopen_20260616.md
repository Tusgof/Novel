# HGD Title And Format Incident Reopen - 2026-06-16

Purpose: reopen the HGD V6.17 quality gate from disk evidence before any further speed/concurrency work.

No provider calls were made. No translation artifacts, final outputs, MoonRead files, glossary files, ledger records, or provider config were modified during this audit.

## Files Inspected

- `Horror Game Developer/03_Raw/ch001/source.json`
- `Horror Game Developer/03_Raw/ch014/source.json`
- `Horror Game Developer/03_Raw/ch022/source.json`
- `Horror Game Developer/05_Output/ch001/ch001.md`
- `Horror Game Developer/05_Output/ch014/ch014.md`
- `Horror Game Developer/05_Output/ch022/ch022.md`
- `Horror Game Developer/04_Work/ch022/ch022-block-001.literal.json`
- `Horror Game Developer/04_Work/ch022/ch022-block-001.refined.json`
- `Horror Game Developer/04_Work/ch022/ch022-block-001.qa.json`
- `Horror Game Developer/04_Work/ch022/ch022-block-001.formatted.json`
- `Deep Sea Embers/reader-web/content/generated/books/horror-game-developer/manifest.json`
- `Deep Sea Embers/reader-web/content/generated/books/horror-game-developer/chapters/ch001.md`
- `Deep Sea Embers/reader-web/scripts/generate-chapters.mjs`
- `C:/Users/ASUS/Downloads/good format.md`

## Title Audit

Current count across HGD published scope `ch001-ch035`:

| layer | English-like titles |
| --- | ---: |
| raw source title | 35/35 |
| HGD final output heading | 0/35 |
| MoonRead generated chapter heading | 0/35 |
| MoonRead manifest title | 0/35 |

Representative title path:

| chapter | raw source title | final output heading | MoonRead heading | manifest title |
| --- | --- | --- | --- | --- |
| ch001 | Chapter 1 - Prologue | ตอนที่ 1 - บทนำ | ตอนที่ 1 - บทนำ | ตอนที่ 1 - บทนำ |
| ch002 | Chapter 2 - The Jester [1] | ตอนที่ 2 - ตัวตลก | ตอนที่ 2 - ตัวตลก | ตอนที่ 2 - ตัวตลก |
| ch029 | Chapter 31 - Quest Completed [2] | ตอนที่ 31 - เควสต์สำเร็จ | ตอนที่ 31 - เควสต์สำเร็จ | ตอนที่ 31 - เควสต์สำเร็จ |
| ch035 | Chapter 37 - Velora Art Museum [2] | ตอนที่ 37 - พิพิธภัณฑ์ศิลปะเวลอรา | ตอนที่ 37 - พิพิธภัณฑ์ศิลปะเวลอรา | ตอนที่ 37 - พิพิธภัณฑ์ศิลปะเวลอรา |

Current evidence does not show English titles in the generated reader output. The title risk is still real because HGD raw source titles are English, and MoonRead currently depends on HGD-specific normalization in `reader-web/scripts/generate-chapters.mjs`.

Owning layer for title prevention:

- primary: durable title source or HGD title normalization in the reader/import path
- guardrail: published-scope title fallback check
- not enough: relying on currently generated Markdown cache

## Format Audit

The existing semantic format audit currently reports:

```text
hgd_semantic_format_audit: 0 findings
```

That result proves only the current heuristic checks pass. It does not prove every source beat is preserved.

`good format.md` is useful as a structure reference, but the file itself appears visually mojibake in this environment. Use it for layout principles, not as text to copy directly:

- standalone bold bracketed system panels
- standalone dialogue where it functions as a beat
- italic thoughts and sound effects
- clear divider blocks
- frequent blank lines around horror/UI beats

## Concrete Formatting / Omission Finding

`ch022` contains a real omission, not just a spacing issue.

Source `Horror Game Developer/03_Raw/ch022/source.json` contains:

```text
I had no time to waste.
*
Like that, four days passed.
*Takakakakaka—*
```

Literal artifact preserved the beat as:

```text
* และแล้ว สี่วันก็ผ่านไป *
```

But `Horror Game Developer/04_Work/ch022/ch022-block-001.refined.json` dropped that beat from `refined_text`. The final output jumps directly from:

```text
ผมไม่มีเวลาให้เสียเปล่าอีกแล้ว

*Takakakakaka—*
```

`Horror Game Developer/04_Work/ch022/ch022-block-001.qa.json` still passed with feedback claiming no omissions.

Root cause for this concrete issue:

- not source fetch
- not MoonRead rendering
- not final Markdown import
- refined stage omitted a short time-skip beat
- QA failed to catch the omission

Repair layer:

- rerun or repair from refinement for `ch022-block-001`, then rerun QA and formatting
- add a deterministic source-beat guard for short standalone italic/time-skip beats before trusting QA
- do not patch only MoonRead generated output

## Current Representative Format Metrics

Sampled final outputs:

| chapter | paragraph count | paragraphs > 500 chars | max paragraph chars |
| --- | ---: | ---: | ---: |
| ch001 | 76 | 0 | 392 |
| ch014 | 110 | 0 | 255 |
| ch022 | 63 | 0 | 420 |
| ch031 | 67 | 0 | 424 |
| ch035 | 51 | 0 | 398 |

This confirms the current problem is not broad paragraph density. The active risk is semantic layout and short-beat preservation.

## Required Next Repair

1. Repair `ch022-block-001` from refinement or rerun it from refinement with explicit instruction to preserve the four-day time skip.
2. Rerun QA and formatting for `ch022-block-001`.
3. Reassemble/publish HGD `ch022` and regenerate MoonRead.
4. Add a guardrail or test that flags source standalone beats such as `Like that, four days passed.` when the refined/final output has no corresponding Thai time-skip phrase.
5. Run:
   - `python -m compileall novel_pipeline`
   - `python test_translation.py`
   - `python scripts/check_output_quality_guardrails.py`
   - `python scripts/audit_hgd_semantic_format.py`
   - `cd reader-web; npm.cmd run generate:chapters; npm.cmd run lint; npm.cmd run build; npm.cmd run smoke`

## Stop Conditions

Stop before applying repairs if:

- repairing `ch022` would require broad rewriting of the chapter
- a provider rerun changes unrelated wording
- output repair cannot preserve source meaning exactly
- MoonRead generation rejects any chapter
- guardrail changes create noisy false positives across valid chapters

## Decision

Initial audit decision: V6.17 remained reopened until the `ch022` omission was repaired and the prevention guard was added.

## Repair Result

Repair completed in the same bounded gate.

Files changed outside the nested Git repo:

- `Horror Game Developer/04_Work/ch022/ch022-block-001.refined.json`
- `Horror Game Developer/04_Work/ch022/ch022-block-001.qa.json`
- `Horror Game Developer/04_Work/ch022/ch022-block-001.formatted.json`
- `Horror Game Developer/05_Output/ch022/ch022.md`
- `Horror Game Developer/04_Work/ch001/title.json` through `Horror Game Developer/04_Work/ch035/title.json`
- `Horror Game Developer/06_Logs/run_ledger.jsonl`

Files changed inside the nested Git repo:

- `scripts/check_output_quality_guardrails.py`
- `test_translation.py`
- `reader-web/content/generated/books/horror-game-developer/chapters/ch022.md`
- reader generated manifests/import report timestamp and count metadata
- this report

Exact repair:

- Added the missing time-skip beat back to `ch022-block-001.refined.json` before the keyboard sound beat:
  - `*และแล้ว สี่วันก็ผ่านไป*`
- Reran:
  - `novel-pipeline --config ".system\config.yaml" rerun-block --run-id horror-game-developer-ch001-ch050-v3 --block-id ch022-block-001 --from-stage qa`
  - QA passed with retry 0.
  - Formatting completed and final chapter output was rewritten.
- Created durable HGD title sidecars for `ch001-ch035` from the current Thai MoonRead manifest titles so future single-block reruns do not fall back to English source titles.
- Reran:
  - `novel-pipeline --config ".system\config.yaml" rerun-block --run-id horror-game-developer-ch001-ch050-v3 --block-id ch022-block-001 --from-stage format`
  - Final `ch022` output was rewritten with Thai title `ตอนที่ 22 - พัฒนาเกม [4]`.
- Regenerated MoonRead:
  - `npm.cmd run generate:chapters`
  - Result: 2 books, 85 available, 0 missing, 0 rejected.

Prevention:

- Added `check_hgd_required_source_beats()` to `scripts/check_output_quality_guardrails.py`.
- Added `test_hgd_required_source_beat_guardrail_flags_missing_time_skip()` to `test_translation.py`.
- The guardrail now fails if HGD `ch022` source contains `Like that, four days passed.` but final output lacks `สี่วันก็ผ่านไป`.

Validation:

- `python -m compileall novel_pipeline scripts test_translation.py`: passed
- `python test_translation.py`: passed
- `python scripts/check_output_quality_guardrails.py`: passed
- `python scripts/audit_hgd_semantic_format.py`: passed with 0 findings
- `npm.cmd run generate:chapters`: passed
- `npm.cmd run lint`: passed
- `npm.cmd run build`: passed
- `npm.cmd run smoke`: first attempt timed out waiting for the temporary local server; immediate rerun passed with no console errors

Current decision:

V6.17 HGD title/format incident is closed for published scope `ch001-ch035`.

Do not infer that HGD `ch037-ch050` are complete. The HGD run still has pending chapters beyond the published MoonRead scope, and this gate did not translate or publish them.
