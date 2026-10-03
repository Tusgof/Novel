# V6.37 OHKS Five-Chapter Checkpoint Review

> Superseded by `v6_37_ohks_five_chapter_checkpoint_review_v2_20261003.md`. The v11 run is retained as historical evidence; its original narrative overstated which prompt changes were active in that run.

Date: 2026-10-03

## What changed

This was the historical v11 experiment-only OHKS slice using `ch002,ch017,ch032,ch055,ch090`.
It verified checkpoint artifacts, deterministic candidate evidence review, and retry-inclusive trace totals. The narrative claims that the isolated QA prompt carried adjudication feedback and that the full compact-profile/feedback-loop changes were active were not valid for v11; those gaps were corrected and rerun in v2. See `v6_37_ohks_five_chapter_checkpoint_review_v2_20261003.md` for the authoritative result.

## Result

All five chapters completed. No production files or MoonRead content changed.

| Metric | Result |
|:--|--:|
| Provider calls | 24 |
| Provider failures/retries | 4 |
| Provider time | 994.842 seconds |
| Reported tokens | 200,099 |
| Reported cost | `$0.288340960` |
| QA fallback use | 4 of 5 chapters |
| Output guardrail issues | 0 |
| Sentinel blocker/major/minor/info | `0/0/0/0` blocking run; `0/0/19/0` with advisory English scan |
| Glossary candidates rejected by evidence review | 0 |

The explicit resume verification ran the same five chapters again with
`--resume`: trace files remained `24 -> 24`, so it added zero provider calls.
That proves checkpoint reuse works for a completed chapter. The first attempt
also stopped before provider calls when the isolated vault lacked the five raw
files; after copying the verified raw files, the same run resumed safely.

## Human/Inspector spot-check

The first, middle, and final passages of all five chapters were inspected.
The outputs had readable paragraphs, dialogue/thought markers, endings, and no
obvious truncation. Deterministic scans found no omission placeholders, CJK
body leakage, Thai numerals, provider metadata, or short output.

The advisory Sentinel findings are real review items: experimental H1 titles
remain English (`Chapter ...`) and some game/system terms remain English, such
as `MAX`, `RPG`, `Abyss`, and `Word Magic`. They are not blocking under the
current generic Sentinel because this OHKS experiment has no completed title
sidecars or full approved term policy. This means the pipeline core passed, but
the OHKS novel profile is not ready for direct reader publication yet.

## Comparison with the previous five-chapter slice

Compared with the previous OHKS `pilot_v10` slice (`ch044,ch064,ch068,ch079,ch080`):

- calls: `24` vs `23`, slightly worse;
- provider failures: `4` vs `2`, worse;
- reported cost: `$0.288` vs `$0.264`, slightly worse;
- provider time: `994.8s` vs `919.5s`, slightly worse.

Therefore this round does **not** prove a cost or speed improvement. The
checkpoint mechanism improves recoverability and prevents duplicate calls after
an interruption, but this uninterrupted five-chapter run still suffered from
QA-provider instability. The quality gates remained clean, with the title and
term-profile gap exposed rather than hidden.

## Decision and next improvements

The five changes should be retained. The most useful improvement was checkpoint
reuse; it directly prevents paying for literal/refinement again after a later
stage fails. The targeted QA adjudication is also safer than accepting the first
PASS/FAIL blindly, but it still depends on a fallback provider.

Before OHKS production publication, add a novel-specific title sidecar flow and
review the 19 advisory English findings into a small approved glossary/profile.
Do not add one-off prompt rules for each word. Keep the profile focused on title
translation, game UI, named entities, and the novel's voice. A later bounded
comparison should measure whether this profile reduces advisory findings without
raising cost or provider failures.

## Evidence

- Output: `One Hit Kill Swordmaster/04_Work/_experiments/v6_36_ohks_lean_v1/05_Output/pilot_v11/`
- Trace: `One Hit Kill Swordmaster/04_Work/_experiments/v6_36_ohks_lean_v1/trace/pilot_v11/`
- Blocking Sentinel: `07_Reports/sentinel_quality_v6-37-ohks-pilot-v1_20261003_014947.md`
- Advisory Sentinel: `07_Reports/sentinel_quality_v6-37-ohks-pilot-v1-advisory_20261003_015114.md`
