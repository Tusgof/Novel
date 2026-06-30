# บันทึกการวิจัย: V6.34 Cross-Novel Libra Blind Pilot Source Pool

## 1. ข้อมูลพื้นฐาน

- Timestamp UTC: `2026-06-30T20:20:00Z`
- โครงการ: Novel Translation Pipeline
- หัวข้อ: V6.34 source-pool audit and cross-novel blind sampling manifest
- ผู้บันทึก: Codex
- สถานะ: เสร็จสิ้น
- Artifact หลัก:
  - `PROJECT_BRAIN.md`
  - `IMPLEMENT_PLAN.md`
  - `ARCHITECTURE.md`
  - `RESEARCH_LOG_FORMAT.md`

## 2. วัตถุประสงค์

รอบนี้ตอบคำถามว่า Libra - Pilot Gate รอบใหม่ควรสุ่มจาก raw source อย่างไรเพื่อไม่ overfit กับตอนที่เคยแปลหรือเคยมีปัญหาแล้วเท่านั้น

ความสำเร็จของรอบนี้คือมี source-pool audit ที่ตรวจสอบได้ มี seed ที่ reproducible มีรายชื่อตอน in-sample/out-of-sample ของทั้ง 3 นิยาย และยังไม่เริ่ม provider-backed translation ก่อน sampling/source-pool gate เสร็จ

## 3. วิธีการและขั้นตอน

1. ตรวจสถานะ working tree และเอกสารหลัก

```powershell
git status --short --untracked-files=all
rg -n "Libra - Pilot|raw source|RESEARCH_LOG_FORMAT" PROJECT_BRAIN.md IMPLEMENT_PLAN.md ARCHITECTURE.md RESEARCH_LOG_FORMAT.md
```

2. ตรวจ local raw source pool ของทั้ง 3 นิยาย

```powershell
$novels = @('Deep Sea Embers','Horror Game Developers','Infinite Regressor Stories')
foreach ($novel in $novels) {
  $dirs = Get-ChildItem -Directory "$novel\03_Raw" -Filter 'ch*' -ErrorAction SilentlyContinue |
    Where-Object { $_.Name -match '^ch\d+$' }
  $nums = @($dirs | ForEach-Object { [int]$_.Name.Substring(2) } | Sort-Object)
  $missing = @()
  if ($nums.Count -gt 0) {
    foreach ($n in ($nums[0]..$nums[-1])) {
      if ($nums -notcontains $n) { $missing += $n }
    }
  }
}
```

3. สร้าง sampling manifest แบบ reproducible ด้วย seed `634001`

```powershell
@'
import json, random
novels = {
    "deep-sea-embers": (1, 180),
    "horror-game-developer": (1, 270),
    "infinite-regressor-stories": (1, 394),
}
seed = 634001
rng = random.Random(seed)
for slug, (lo, hi) in novels.items():
    chapters = list(range(lo, hi + 1))
    for i in range(10):
        start_idx = round(i * len(chapters) / 10)
        end_idx = round((i + 1) * len(chapters) / 10)
        pool = chapters[start_idx:end_idx]
        picks = rng.sample(pool, 2)
'@ | python -
```

4. บันทึก milestone และ rule ลงในเอกสารหลัก โดยไม่รัน provider และไม่เริ่ม production translation

## 4. ผลการศึกษาและข้อมูลดิบ

### Source Pool Audit

| Novel | Verified raw pool | Count | Missing chapters |
| --- | --- | ---: | ---: |
| Deep Sea Embers | `ch001-ch180` | 180 | 0 |
| Horror Game Developer | `ch001-ch270` | 270 | 0 |
| Infinite Regressor Stories | `ch001-ch394` | 394 | 0 |

ข้อจำกัดสำคัญ: Deep Sea Embers มีตอนต้นฉบับ upstream มากกว่าที่ fetch อยู่ใน workspace ตอนนี้ ดังนั้น V6.34 รอบแรกจะพิสูจน์เฉพาะ verified local pool `ch001-ch180` เว้นแต่ Ferryman จะ fetch และ validate source scope ที่กว้างกว่านี้ก่อน

### Sampling Method

| Parameter | Value |
| --- | --- |
| Seed | `634001` |
| Method | 10 strata per novel; 1 in-sample and 1 out-of-sample chapter from each stratum |
| Source | fetched `03_Raw/` only |
| Total sample | 60 chapters |
| In-sample | 30 chapters |
| Out-of-sample | 30 chapters |

### Selected Chapters

| Novel | In-sample chapters | Out-of-sample chapters |
| --- | --- | --- |
| Deep Sea Embers | `ch008,ch033,ch051,ch061,ch077,ch098,ch110,ch143,ch150,ch176` | `ch016,ch027,ch044,ch072,ch089,ch099,ch125,ch132,ch154,ch180` |
| Horror Game Developer | `ch005,ch046,ch059,ch083,ch131,ch155,ch187,ch205,ch239,ch262` | `ch027,ch041,ch067,ch097,ch124,ch160,ch186,ch204,ch242,ch252` |
| Infinite Regressor Stories | `ch009,ch076,ch086,ch157,ch183,ch201,ch252,ch300,ch338,ch381` | `ch030,ch073,ch093,ch133,ch165,ch236,ch244,ch278,ch348,ch361` |

## 5. ปัญหา อุปสรรค และการแก้ไข

1. What happened: `RESEARCH_LOG_FORMAT.md` still referenced an older unrelated project name.
   How it was resolved: updated it to Novel Translation Pipeline before using it as the format source.
   Outcome after resolution: future logs now point to `novel_pipeline` and `D:\Fogust\Workspace\Novel\01_Research_Log`.

2. What happened: Prior experiment documentation could imply that per-novel Libra - Pilot evidence was enough for cross-novel generalization.
   How it was resolved: added V6.34 as a separate cross-novel blind pilot milestone.
   Outcome after resolution: V6.32 remains historical per-novel pilot evidence; V6.34 is now the active cross-novel generalization experiment.

3. What happened: DSE upstream source likely extends beyond the local fetched `ch001-ch180` pool.
   How it was resolved: recorded the limitation explicitly.
   Outcome after resolution: sampling is valid only for the verified local pool unless a broader fetch/validate step runs first.

## 6. ข้อสรุปและก้าวต่อไป

ข้อสรุป: V6.34 source-pool and sampling round is complete, while the full provider-backed V6.34 experiment remains incomplete because baseline/in-sample/OOS runs have not started.

- The sampling source is now `03_Raw/`, not translated output.
- The sample is distributed across each novel's verified raw range.
- The first round has a fixed seed and reproducible chapter list.
- No provider calls or production translation were started in this round.

ก้าวต่อไป:
1. Run V6.34B read-only baseline analyzers on the 60 selected raw-source chapters.
2. Record per-chapter risk metrics in this research log or a new log if V6.34B is treated as a separate experiment round.
3. Start V6.34C in-sample provider-backed runs only after the baseline risk table exists.
