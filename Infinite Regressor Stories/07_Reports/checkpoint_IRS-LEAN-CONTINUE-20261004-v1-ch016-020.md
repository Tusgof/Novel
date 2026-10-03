# Lean checkpoint report — IRS ch016–ch020

- Run ID: `IRS-LEAN-CONTINUE-20261004-v1-ch016-020`
- Novel: Infinite Regressor Stories
- Range: ch016–ch020
- Final status: `complete`
- Promoted: ch016, ch017, ch018, ch019, ch020
- Quarantined: none
- Scope: no ch021+ work started; no routing, control-document, registry, MoonRead, git, or publication changes.

## Recovery record

The prior run quarantined ch016/ch018/ch019 on duplicate title/density guardrails, ch017 on the leaked source-script signature `天寥化`, and ch020 on narrator pronoun drift. The saved refined checkpoints were repaired deterministically and source-faithfully, then resumed without rerunning healthy literal/refinement stages:

- ch016: removed the duplicate body `บทที่ 16` line and split the numbered Store Rules into bounded paragraphs.
- ch017: removed the duplicate body `ตอนที่ 17` line and transliterated the leaked signature to `เทียนเหลียวฮว่า`.
- ch018: removed the duplicate body `บทที่ 18` line.
- ch019: retained the translated title subtitle with `Ⅱ` and `บทที่ 19`, removed the duplicate title line, and restored the terminal `เชิงอรรถ:` header.
- ch020: removed the duplicate body `บทที่ 20` line, normalized the narrator to `ผม`, corrected the source-backed speaker attribution, and split two dense narrative paragraphs.

The first recovery attempt exposed a glossary-title invariant; the title subtitle was restored while the duplicate chapter-number line remained removed. No force-accept was used.

## Chapter gates

| Chapter | Status | QA | Guardrails/Sentinel | Reused stages |
| --- | --- | --- | --- | --- |
| ch016 | promoted | PASS (fallback route after primary timeout) | 0 blocker / 0 major / 0 minor / 0 info | literal, refinement, QA, formatting, harvest |
| ch017 | promoted | PASS (fallback route after primary timeout) | 0 / 0 / 0 / 0 | literal, refinement, QA, formatting, harvest |
| ch018 | promoted | PASS (fallback route) | 0 / 0 / 0 / 0 | literal, refinement, QA, formatting, harvest |
| ch019 | promoted | PASS after title/footer repair | 0 / 0 / 0 / 0 | literal, refinement |
| ch020 | promoted | PASS after voice/speaker repair | 0 / 0 / 0 / 0 | literal, refinement, QA, formatting, harvest |

## Provider and verification evidence

- Final run metrics: 53 provider calls, 10 provider failures, 4,000.461 provider seconds; all failures used configured fallback behavior or were historical retry failures. No global provider exhaustion occurred.
- Known fallback incidents include the earlier ch016 refinement timeout and QA primary-route empty responses; final QA passed on configured fallback routes.
- Final scoped deterministic guardrail: `python -X utf8 scripts/check_output_quality_guardrails.py --novel infinite-regressor-stories --chapters ch016-ch020` → `output_quality_guardrails: passed`.
- Final aggregate blocking Sentinel: `python -X utf8 scripts/sentinel_quality_report.py --scope lean-IRS-LEAN-CONTINUE-20261004-v1-ch016-020-blocking-final --novel infinite-regressor-stories --chapters ch016-ch020 --fail-on major --skip-advisory-english` → 0/0/0/0. Report: `D:\Fogust\Workspace\Novel\07_Reports\sentinel_quality_lean-IRS-LEAN-CONTINUE-20261004-v1-ch016-020-blocking-final_20261003_184308.md` (JSON sibling has the same stem).
- Per-chapter blocking Sentinel reports were emitted for ch016–ch020 at `D:\Fogust\Workspace\Novel\07_Reports\sentinel_quality_lean-IRS-LEAN-CONTINUE-20261004-v1-ch016-020-ch016_20261003_183723.json` through the ch020 `20261003_183724.json` report; each has zero blocker/major/minor/info findings.

## Five-chapter spot-check

All five promoted outputs were inspected at title/opening, early-middle, late-middle, and ending points. Every sample had no source-script leakage, no runaway repeated characters, and maximum paragraph length below the guardrail threshold:

- ch016: 12,924 chars; 133 body paragraphs; max 625; title `# นักสากลนิยม 2`; ending records the Samcheon guild loss.
- ch017: 12,153 chars; 109 body paragraphs; max 604; title `# นักสากลนิยม 3`; ending returns to the regression narrative.
- ch018: 14,874 chars; 151 body paragraphs; max 441; title `# สหายร่วมทาง 1`; ending contains the three translated footnotes.
- ch019: 13,382 chars; 111 body paragraphs; max 386; title `# สหายร่วมทาง 2`; ending contains the restored `เชิงอรรถ:` header.
- ch020: 16,637 chars; 130 body paragraphs; max 533; title `# สหายร่วมทาง 3`; ending preserves the formal `ผม` narrator voice.

## Artifacts

- Run report: `Infinite Regressor Stories/04_Work/_lean_runs/IRS-LEAN-CONTINUE-20261004-v1-ch016-020/lean_run_report.json`
- Promoted outputs: `Infinite Regressor Stories/05_Output/ch016/ch016.md` through `ch020/ch020.md`
- Checkpoint report: `Infinite Regressor Stories/07_Reports/checkpoint_IRS-LEAN-CONTINUE-20261004-v1-ch016-020.md`

Next safe action: remain idle and await the Inspector’s next bounded order; no chapters outside ch016–ch020 were started.
