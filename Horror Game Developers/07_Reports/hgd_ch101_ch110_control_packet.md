# HGD ch101-ch110 Control Packet

Date: 2026-06-17
Run ID: `hgd-ch101-ch110-v1`
Range: `ch101-ch110`

## Current State

- Ledger records before resume: 20
- Completed stages: `fetched` 10, `glossary_scanned` 10
- Translation/refinement/QA/formatting/completed records: none
- Current failed blocks: none
- Next pending block: `ch101-block-001` at `translating`
- MoonRead published scope before this batch: HGD `ch001-ch100`

## Glossary Decisions

Approved existing notes / aliases:

- `The Second Order` -> existing `Second Order` / `ลำดับที่สอง`; alias added to `Second Order.md`
- `Third Order Recruit` -> existing `Third Order` / `ลำดับที่สาม`; alias added to `Third Order.md`

Approved new notes:

- `Hunter Decree` / scan variant `Hunter' Decree` -> `ประกาศิตนักล่า`
- `Raymond` -> `เรย์มอนด์`
- `Allerman` -> `อัลเลอร์แมน`
- `Iris` -> `ไอริส`
- `Enter` / `[Enter]` -> `ปุ่ม Enter`

Rejected scan noise:

- `His Decree`: generic possessive phrase, should be translated contextually
- `Since Raymond`: sentence fragment, not a term
- `Skrrr Skrrr The`: sound/title fragment, not a glossary term

## Title Coverage

Source titles detected:

- `ch101`: `Chapter 106 - Expedition Squad [2]`
- `ch102`: `Chapter 107 - Silence [1]`
- `ch103`: `Chapter 108 - Silence [2]`
- `ch104`: `Chapter 109 - Silence [3]`
- `ch105`: `Chapter 110 - Silence [4]`
- `ch106`: `Chapter 111 - Butcher [1]`
- `ch107`: `Chapter 112 - Butcher [2]`
- `ch108`: `Chapter 113 - A Twisted Game [1]`
- `ch109`: `Chapter 114 - A Twisted Game [2]`
- `ch110`: `Chapter 115 - A Twisted Game [3]`

Title mappings required before final assembly:

- `Expedition Squad` -> `หน่วยสำรวจ` (already present)
- `Silence` -> `ความเงียบ`
- `Butcher` -> `คนเชือด`
- `A Twisted Game` -> `เกมบิดเบี้ยว`

The new title mappings were added before resume. Final assembly should write title sidecars automatically. Unknown HGD English titles must still fail fast.

## Provider Route

- glossary scan: OpenRouter `google/gemini-3-flash-preview`
- glossary option suggestion: OpenRouter `deepseek/deepseek-v4-flash`
- literal translation: OpenRouter `google/gemini-3-flash-preview`
- refinement: OpenRouter `deepseek/deepseek-v4-flash`
- QA primary: OpenRouter `deepseek/deepseek-v4-flash` with reasoning enabled
- QA fallback: Qwen `deepseek-reasoner`, then OpenRouter `deepseek/deepseek-v4-pro`, then Codex emergency fallback
- formatting primary: OpenRouter `deepseek/deepseek-v4-flash`
- formatting fallback/cleanup: local deterministic cleanup only

## Stop Conditions

Stop immediately on:

- manual QA prompt
- provider failure, timeout, nonzero output, or command length failure
- missing HGD title mapping
- formatting validation failure
- output guardrail failure
- any `ch111+` processing during this batch

## Recovery Patterns

QA omission after retry:

1. Inspect `literal.json`, `refined.json`, and `qa.json`.
2. Repair only the affected `refined_text` source beat.
3. Run QA with `--no-auto-refine`.
4. If QA passes, resume. If QA still fails, stop and report.

Force-accept:

1. Use only after Codex/user confirms the current repaired artifact preserves source meaning.
2. Require explicit reason.
3. Preserve recovery metadata.

Title mapping miss:

1. Add the title mapping in both pipeline map and HGD title normalizer.
2. Rerun from the safe stage that writes title sidecar/final output.
3. Do not manually patch MoonRead metadata.

Formatting failure:

1. Rerun AI formatting first.
2. Use local cleanup only for deterministic Markdown cleanup, not semantic dialogue/thought detection.

## Next Safe Command

After glossary approval records are committed and pre-resume gate is green:

```powershell
python -m novel_pipeline.cli --config "D:\Fogust\Workspace\Novel\Horror Game Developers\.system\config.yaml" resume --run-id hgd-ch101-ch110-v1 --until-chapter ch110 --manual-action-mode stop
```
