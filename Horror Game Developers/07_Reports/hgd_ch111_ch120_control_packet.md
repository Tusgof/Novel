# HGD ch111-ch120 Control Packet

Date: 2026-06-17
Run ID: `hgd-ch111-ch120-v1`
Range: `ch111-ch120`

## Current State

- Ledger records before glossary approval: 20
- Completed stages: `fetched` 10, `glossary_scanned` 10
- Translation/refinement/QA/formatting/completed records: none
- Current failed blocks: none
- Next pending block: `ch111-block-001` at `translating`
- MoonRead published scope before this batch: HGD `ch001-ch100`

## Glossary Decisions

Approved new notes:

- `Intermediate Node` -> `โหนดระดับกลาง`
- `Time Freeze` -> `หยุดเวลา`
- `Ryan` -> `ไรอัน`
- `Malovia Island` -> `เกาะมาโลเวีย`
- `Game Developer Mode` -> `โหมดนักพัฒนาเกม`
- `Select Game Engine` -> `เลือกเอนจินเกม`
- `Select Game` -> `เลือกเกม`
- `Game Developer Engine` -> `เอนจินนักพัฒนาเกม`
- `Core Items` -> `ไอเทมหลัก`
- `Selected Engine` -> `เอนจินที่เลือก`
- `Unknown Recording` -> `บันทึกปริศนา`
- `Game Adjuster` -> `ตัวปรับแต่งเกม`
- `Undetectable Script` -> `สคริปต์ตรวจจับไม่ได้`
- `Gameplay Tester` -> `ผู้ทดสอบเกมเพลย์`
- `Game Developing System` -> `ระบบพัฒนาเกม`

Approved existing notes / aliases:

- `Hunter’ Decree`, `The Hunter Decree` -> existing `Hunter Decree` / `ประกาศิตนักล่า`
- `Mirille` -> existing `Mirelle` / `มิเรลล์`
- `Time Limit` remains `เวลาจำกัด`
- `Section Chief` remains `หัวหน้าแผนก`

Rejected scan noise:

- `Creaaak Creaaak`: sound effect, translate contextually in formatting
- `How Kyle`: sentence fragment
- `Section`: fragment of `Section Chief` context, not a standalone term
- `Malovia Island Time Limit`: noisy combined phrase; split into `Malovia Island` and existing `Time Limit`
- `Mirille Items`: UI scan merge of character name and section label, not a standalone term

## Title Coverage

Source titles detected:

- `ch111`: `Chapter 116 - A Twisted Game [4]`
- `ch112`: `Chapter 117 - A Twisted Game [5]`
- `ch113`: `Chapter 118 - Escape [1]`
- `ch114`: `Chapter 119 - Escape [2]`
- `ch115`: `Chapter 120 - Escape [3]`
- `ch116`: `Chapter 121 - Aftermath [1]`
- `ch117`: `Chapter 122 - Aftermath [2]`
- `ch118`: `Chapter 123 - Game Developer Mode [1]`
- `ch119`: `Chapter 124 - Game Developer Mode [2]`
- `ch120`: `Chapter 125 - New Project [1]`

Title mappings:

- `A Twisted Game` -> `เกมบิดเบี้ยว`
- `Escape` -> `หลบหนี`
- `Aftermath` -> `ผลพวง`
- `Game Developer Mode` -> `โหมดนักพัฒนาเกม`
- `New Project` -> `โปรเจกต์ใหม่`

The new title mappings were added before resume. Final assembly should write title sidecars automatically.

## Stop Conditions

Stop immediately on:

- manual QA prompt
- provider failure, timeout, nonzero output, or command length failure
- missing HGD title mapping
- formatting validation failure
- output guardrail failure
- any `ch121+` processing during this batch

## Next Safe Command

After glossary approval records are committed and pre-resume gate is green:

```powershell
python -m novel_pipeline.cli --config "D:\Fogust\Workspace\Novel\Horror Game Developers\.system\config.yaml" resume --run-id hgd-ch111-ch120-v1 --until-chapter ch120 --manual-action-mode stop
```
