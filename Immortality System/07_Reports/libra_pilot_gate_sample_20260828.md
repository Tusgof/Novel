# Libra - Pilot Gate Sample

Date: 2026-08-28

## Locked Gate

- Novel: Immortality System
- Raw pool: `03_Raw/ch001-ch2570`
- Usable raw chapters: 2,570
- Seed: `20260828`
- Sampling source: raw source files only
- Experiment output: isolated; not production and not MoonRead

The pool was divided into five consecutive strata of 514 chapters. Four chapters were selected from each stratum, with two assigned to in-sample and two to out-of-sample. The two sets were shuffled independently after selection. Full hashes and source lengths are in `libra_pilot_gate_sample_20260828.json`.

## In-Sample: Tune Only

`ch1307, ch1765, ch2439, ch2307, ch741, ch1424, ch1631, ch376, ch338, ch984`

Stratum coverage: 1=2, 2=2, 3=2, 4=2, 5=2.

## Out-Of-Sample: Generalization Only

`ch1410, ch1020, ch2313, ch2358, ch1149, ch1653, ch1984, ch213, ch544, ch282`

Stratum coverage: 1=2, 2=2, 3=2, 4=2, 5=2.

## Rules

1. Run scan-only and glossary approval before translating either set.
2. Tune or repair only from in-sample evidence.
3. Do not tune from OOS findings until the OOS round is complete.
4. Keep all pilot artifacts in `04_Work/_experiments/`.
5. Do not publish pilot output or merge pilot glossary notes into production glossary intent.
6. Stop on provider failure, manual prompt, source mismatch, Sentinel blocker/major, or unsafe output.

## Next Checkpoint

Create an isolated experiment vault from the exact raw files listed in the JSON manifest, verify the recorded hashes, then run the in-sample scan/glossary gate.
