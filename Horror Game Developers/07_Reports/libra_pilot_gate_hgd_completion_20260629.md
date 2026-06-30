# Libra - Pilot Gate HGD Completion

Date: 2026-06-29

Experiment vault: `Horror Game Developers/04_Work/_experiments/libra_pilot_hgd_v1`

## Verdict

PASS for HGD as a controlled Libra - Pilot Gate experiment.

Do not treat the experiment output as production publication. It proves the current pipeline can complete a representative HGD 20-chapter sample with bounded recovery, deterministic guardrails, and Sentinel clean.

## Sample

Raw source pool: `Horror Game Developers/03_Raw/ch001-ch250`

Source sequence check: passed for `ch001-ch250`.

Seed: `632250`

In-sample chapters:

- `ch230`, `ch164`, `ch185`, `ch067`, `ch199`, `ch047`, `ch065`, `ch079`, `ch010`, `ch249`

Out-of-sample chapters:

- `ch111`, `ch103`, `ch182`, `ch015`, `ch013`, `ch070`, `ch232`, `ch168`, `ch179`, `ch172`

Out-of-sample glossary was run as two 5-chapter batches:

- `hgd-libra-pilot-oos-a-v1`: `ch111,ch103,ch182,ch015,ch013`
- `hgd-libra-pilot-oos-b-v1`: `ch070,ch232,ch168,ch179,ch172`

## Runs

| Run | Scope | Result | Notes |
| --- | --- | --- | --- |
| `hgd-libra-pilot-insample-v1` | 10 in-sample chapters | 10/10 complete | 2 historical failed records, no current failures |
| `hgd-libra-pilot-oos-a-v1` | 5 OOS-A chapters | 5/5 complete | 2 historical QA hard-fail records, no current failures |
| `hgd-libra-pilot-oos-b-v1` | 5 OOS-B chapters | 5/5 complete | `ch232` used literal-safe QA recovery; no current failures |

## Verification

- Current failed blocks: none across all three runs.
- Final output files: all 20 sampled chapters exist in the experiment vault.
- Output guardrails: passed for all 20 sampled chapters.
- Aggregate Sentinel: `0/0/0/0`.
- Sentinel report: `Horror Game Developers/04_Work/_experiments/07_Reports/sentinel_quality_hgd-libra-pilot-all-v1_20260629_164543.md`
- Canonical compile after promoted fix: required before production continuation.

## Findings And Layer Classification

| Finding | Layer | Cause | Fix / Prevention |
| --- | --- | --- | --- |
| Experiment vault initially lacked shared Sentinel/guardrail scripts | Multi-novel setup | Experiment vault copying was incomplete | Future isolated experiment creation must include scripts used by pipeline post-output gates |
| `ch067` mistranslated source `hit` | Run-local / QA evidence | Ambiguous English word in music-performance context | QA caught it; bounded repair changed the phrase to the song-hit meaning before passing |
| `ch079` had `Reward` / `Time Limit` glossary gate issue | Multi-novel glossary coverage | Retry artifact state lagged behind latest refined text | Rerun from QA confirmed latest refined output contained required terms; Libra coverage gate is useful |
| `ch010`, `ch015` missing Thai title mappings | HGD novel layer | HGD English title normalization required explicit map entries | Promoted `The world has changed`, `Exit`, and `Orientation Day` to canonical `HGD_TITLE_MAP` |
| `ch182` QA caught `head` -> `heart` drift | Language / QA evidence | Provider mistranslated a concrete body-part control beat | QA blocked; rerun passed after latest artifact correction |
| `ch015` QA caught Seth pronoun drift | HGD novel layer | Seth POV can drift from `ผม` to `เรา` under provider refinement | QA blocked; HGD pronoun policy remains necessary |
| `ch232` needed literal-safe omission recovery | Multi-novel recovery | Ordinary refine retries still risk omission | Existing literal-safe QA recovery worked and completed without manual JSON rewrite |
| Glossary scanner produced generic/noisy candidates | Multi-novel glossary | Scanner still surfaces phrases like `Both Kyle`, `The TV`, generic `Guild` | Batch approval should stay human/Codex reviewed; reject generic/noisy terms and prefer existing glossary coverage |

## Production Recommendation

HGD passed the 20-chapter Libra - Pilot Gate. It is safe to continue HGD in bounded production increments, but not as long unmonitored parallel production.

Required production rules after this experiment:

- Use glossary batches of 5 chapters.
- Keep Sentinel as a blocking stage.
- Keep HGD title mapping fail-fast behavior.
- Run output guardrails and aggregate Sentinel after each large run.
- Treat QA hard-fails as data: repair from the earliest broken stage, then rerun QA without force-accept unless a separate review approves it.

## Next Work Requested By User

After this experiment:

1. Translate HGD 20 more chapters.
2. Translate DSE 20 more chapters.
3. For IRS, discard the old translation attempt and start a clean retranslation from `ch001-ch050`.
4. Use glossary batch size 5 for all three novels.

This should be planned as a new production milestone, not mixed into the experiment vault.
