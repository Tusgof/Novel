# Libra - Pilot Gate DSE Completion Report

Date: 2026-06-29

## Scope

- Novel: Deep Sea Embers
- Experiment vault: `Deep Sea Embers/04_Work/_experiments/libra_pilot_dse_v1`
- Raw source pool: `03_Raw/ch001` through `03_Raw/ch160`
- Raw source count before sampling: 160 chapters
- Sampling seed: `632160`
- Rule confirmed: sampling was from fetched `03_Raw`, not from translated/problem chapters only.

## Sample

In-sample chapters:

`ch129,ch033,ch012,ch084,ch111,ch036,ch150,ch047,ch043,ch040`

Out-of-sample chapters:

`ch027,ch124,ch126,ch141,ch085,ch114,ch122,ch060,ch003,ch050`

Sample artifacts:

- `Deep Sea Embers/07_Reports/libra_pilot_gate_dse_sample_20260629.json`
- `Deep Sea Embers/07_Reports/libra_pilot_gate_dse_sample_20260629.md`

## Runs

In-sample run:

- Run ID: `dse-libra-pilot-insample-v1`
- Result: 54/54 blocks completed
- Current failed blocks: none
- Historical failed records: 2
- Outputs: all 10 chapter outputs exist

Out-of-sample run:

- Run ID: `dse-libra-pilot-oos-v1`
- Result: 56/56 blocks completed
- Current failed blocks: none
- Historical failed records: 2
- Outputs: all 10 chapter outputs exist

## Glossary Decisions

In-sample approved terms:

- `世界之创` -> `รอยแผลแห่งโลก`
- `无垠海域` -> `ทะเลไร้ขอบเขต`

Out-of-sample approved terms:

- `葛莫娜` -> `เกอมอน่า`
- `黑太阳` -> `ดวงอาทิตย์ทมิฬ`
- `太阳异端` -> `พวกนอกรีตแห่งดวงอาทิตย์`
- `幽灵船长` -> `กัปตันเรือผี`

All approvals were experiment-local until separately promoted to production glossary.

## Incidents And Fixes

1. Reasoning-enabled OpenRouter QA returned an empty assistant message on the first in-sample QA call.
   - Cause: long QA prompt instability on `openrouter_reasoning` with `deepseek/deepseek-v4-flash`.
   - Experiment fix: QA route inside the isolated vault was changed to non-reasoning OpenRouter `deepseek/deepseek-v4-flash` with Gemini Flash fallback.
   - Prevention: do not promote reasoning-enabled QA for long prompts without a focused provider probe.

2. Final assembly failed when title sidecars were missing inside the isolated experiment vault.
   - Cause: the experiment copied raw/work state but not the required `04_Work/chXXX/title.json` sidecars.
   - Fix: copied title sidecars for all 20 sample chapters into the experiment vault.
   - Prevention: Libra - Pilot Gate setup must copy or generate title sidecars for sampled chapters before translation.

3. Experiment assembly expected the registry at the experiment parent path.
   - Cause: registry lookup resolved to `Deep Sea Embers/04_Work/_experiments/00_Config/novel_registry.json`.
   - Fix: copied the root registry into that experiment parent.
   - Prevention: isolated experiment vault creation should include registry path compatibility.

4. Output guardrail found duplicate plain title paragraphs under H1 in in-sample chapters.
   - Cause: provider formatting sometimes preserved a plain `ตอนที่/บทที่ ...` title line as body text while assembly also wrote the H1.
   - Fix: final assembly now removes only an immediate title-like first paragraph below the H1.
   - Prevention: regression test added.

5. Output guardrail found one dense paragraph in `ch027`.
   - Cause: provider formatting left a long thought/prose paragraph without punctuation boundaries.
   - Fix: final assembly now applies conservative long-paragraph reflow after AI formatting, splitting only at punctuation or whitespace and preserving words.
   - Prevention: regression test added.

6. Throughput was slow.
   - Evidence: OOS serial resume took roughly hours for 56 blocks despite no current failures.
   - Cause: translation/refinement/QA stages are still serial; only formatting has limited parallel support.
   - Prevention: future speed work should target bounded parallelism for translation/refinement/QA after per-stage isolation and ledger safety are designed.

## Verification

Commands run in the experiment vault:

```powershell
python -m novel_pipeline.cli --config ".system/config.yaml" status --run-id dse-libra-pilot-insample-v1
python -m novel_pipeline.cli --config ".system/config.yaml" status --run-id dse-libra-pilot-oos-v1
python scripts\check_output_quality_guardrails.py --novel deep-sea-embers --chapters ch129,ch033,ch012,ch084,ch111,ch036,ch150,ch047,ch043,ch040,ch027,ch124,ch126,ch141,ch085,ch114,ch122,ch060,ch003,ch050
python scripts\sentinel_quality_report.py --scope dse_libra_pilot_gate_20 --novel deep-sea-embers --chapters ch129,ch033,ch012,ch084,ch111,ch036,ch150,ch047,ch043,ch040,ch027,ch124,ch126,ch141,ch085,ch114,ch122,ch060,ch003,ch050 --fail-on major --skip-advisory-english
```

Results:

- In-sample status: all 54/54 blocks complete, current failed blocks none.
- Out-of-sample status: all 56/56 blocks complete, current failed blocks none.
- Output quality guardrails: passed.
- Sentinel report: blocker/major/minor/info `0/0/0/0`.
- Custom audit: 0 issues for provider/meta leakage, Han body text, question-mark placeholders, dense paragraphs, and title duplication.
- Production outputs, production ledger, and MoonRead were not modified by this experiment.

## Decision

DSE Libra - Pilot Gate passed.

Recommended next action:

- Do not start a long DSE production batch solely from this result.
- First promote the two generic fixes already proven here:
  - duplicate title paragraph removal
  - final long-paragraph reflow after AI formatting
- Keep the throughput bottleneck as a dedicated speed/parallelism milestone because serial translation/refinement/QA remains too slow for long unattended batches.

