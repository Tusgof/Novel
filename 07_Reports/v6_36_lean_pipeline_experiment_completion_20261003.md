# V6.36 Lean Pipeline Experiment Completion

Date: 2026-10-03

## Scope

This was an experiment-only evaluation of the simplified pipeline:

1. project approved, chapter-relevant glossary terms into a source copy;
2. translate transport-safe blocks literally;
3. assemble the chapter and refine it once;
4. run chapter QA and local formatting;
5. harvest new terms as `proposed` only.

No experiment output was published to MoonRead or copied into production output,
glossary, ledger, or reader content.

## Results

| Novel | Scope | Result | Provider calls | Failures | Cost reported |
|:--|:--|:--|--:|--:|--:|
| Horror Game Developer | `ch001` smoke | complete, QA/Sentinel passed | 4 | 0 | `$0.031301576` |
| One Hit Kill Swordmaster | locked 10-chapter sample | complete, all 10 outputs passed final checks | 30 | 3 recovered | `$0.357507432` |

OHKS sample: `ch001,ch004,ch014,ch019,ch037,ch044,ch064,ch068,ch079,ch080`.
The first four chapters came from the valid `pilot_v6`; `ch037` came from the
adjudicated `pilot_v9`; and the final five came from `pilot_v10`.

OHKS aggregate usage was `230,728` reported tokens and `1,485.629` provider
seconds. HGD reported `28,572` tokens and `155.256` provider seconds. The
provider-reported costs are measurements, not estimates.

## Verification

- OHKS final combined output: 10 chapters under
  `One Hit Kill Swordmaster/04_Work/_experiments/v6_36_ohks_lean_v1/05_Output/pilot_combined/`.
- HGD experiment output: `Horror Game Developers/04_Work/_experiments/v6_36_minimal_hgd_v6/05_Output/pilot/ch001/`.
- Deterministic experiment scan: all 10 OHKS files and HGD `ch001` had no
  omission placeholders, provider/meta leakage, CJK body leakage, Thai-digit
  drift, or short-output failure.
- Sentinel OHKS: `0/0/0/0` blocker/major/minor/info.
- Sentinel HGD: `0/0/0/0` blocker/major/minor/info.
- Spot-check covered OHKS first, last, early/middle, late/middle, and the
  provider-recovery chapter, checking title, opening, middle, ending, density,
  dialogue/thought markers, named terms, and truncation signs.
- Full `python test_translation.py` passed after adding QA adjudication coverage.

## Findings

### What improved

- Chapter-level refinement preserved context across the entire assembled
  chapter while keeping block splitting only as a transport concern.
- Glossary projection kept approved terms out of the literal prompt's long
  glossary list and still produced measurable replacement records.
- Local formatting avoided extra provider calls and did not introduce content
  drift in this sample.
- A valid QA `FAIL` is now independently adjudicated by the configured fallback
  instead of being treated as a provider failure or silently accepted. A
  deterministic rule failure still blocks immediately.
- OHKS `ch037` demonstrated why this matters: the pre-adjudication v8 run had a
  DeepSeek false rejection that cited omissions absent from the refined trace.
  The final v9 retry then hit a provider timeout and Gemini fallback passed it.
  This is a QA false-rejection finding, not evidence that the chapter was
  manually repaired.

### Remaining limitations

- OHKS required three recovered QA events: DeepSeek timeouts/valid rejection
  were handled by Gemini fallback. The pipeline is therefore not yet proven for
  unattended long production runs.
- OHKS experiment H1/H2/H3 are supported by a bounded quality result, not a
  production adoption decision. The HGD sample is only a one-chapter smoke and
  does not prove cross-novel generalization.
- The lean harness uses the source title for its experimental H1. Production
  title sidecars remain a separate production concern and were not bypassed.
- The harness still reruns literal/refinement after an interrupted chapter;
  stage checkpoint reuse is a future efficiency task, not claimed here.
- Harvested glossary candidates remain `proposed`; none were promoted by this
  experiment.

## Decision

The simplified pipeline is viable as an experiment workflow and is materially
smaller than the previous prompt-heavy design. It is **not yet approved to
replace production routing**. The next safe step is a separately approved
bounded production comparison, after provider health and QA fallback stability
are reviewed. No OOS or Libra Pilot Gate is required for this novel-specific
pilot; cross-novel promotion would require its own evidence.

## Evidence

- OHKS run artifacts: `.../05_Output/pilot_v6`, `.../pilot_v9`, and
  `.../pilot_v10`, with local traces under the matching `trace/` directories.
- HGD run artifacts: `.../v6_36_minimal_hgd_v6/`.
- Sentinel reports: `sentinel_quality_v6-36-ohks-lean-all10_20261002_212949.md`,
  `sentinel_quality_v6-36-hgd-lean-final_20261002_212816.md`.
- Recursive cleanup record: `workspace_recursive_organization_20261003.md`.
