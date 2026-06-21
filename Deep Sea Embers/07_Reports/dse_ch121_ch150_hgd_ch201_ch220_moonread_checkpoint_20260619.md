# DSE ch121-ch150 + HGD ch201-ch220 MoonRead Checkpoint

Date: 2026-06-19

## Scope

- Deep Sea Embers: `dse-ch121-ch150-v1`
- Horror Game Developer: `hgd-ch201-ch220-v1`
- MoonRead publication target: DSE through `ch150`, HGD through `ch220`

## Run Status

- DSE status: all `ch121-ch150` blocks complete, current failed blocks none, manual actions none.
- HGD status: all `ch201-ch220` blocks complete, current failed blocks none, manual actions none.
- HGD status bug fixed: `qa force_accepted` is now treated as terminal QA success for pending-stage/status calculation.

## Repairs Before Publication

- DSE: removed duplicate plain title paragraphs under H1 headings for affected `ch121-ch150` outputs and formatted artifacts.
- HGD: reflowed dense paragraphs in `ch201-ch220` outputs and formatted artifacts using the existing safe HGD layout helper.
- HGD: removed lone empty emphasis marker lines in `ch217` and `ch220`.
- HGD: closed `ch215` ending punctuation to match the source chapter's terminal sentence.

## Verification

- `python -m compileall novel_pipeline`: passed.
- `PYTHONIOENCODING=utf-8 python test_translation.py`: passed.
- DSE output guardrails for `ch121-ch150`: passed.
- HGD output guardrails for `ch201-ch220`: passed.
- Major-run spot-check samples:
  - DSE: `ch121`, `ch126`, `ch129`, `ch141`, `ch150`
  - HGD: `ch201`, `ch206`, `ch211`, `ch215`, `ch217`, `ch220`
- MoonRead generation: `Generated reader library: 2 books, 370 available, 0 missing, 0 rejected.`
- MoonRead `npm.cmd run lint`: passed.
- MoonRead `npm.cmd run build`: passed, 377 static pages.
- MoonRead `npm.cmd run smoke`: passed with `ok: true`.

## Deployment

- Vercel production deployment: succeeded.
- Alias: `https://novel-pink-nu.vercel.app`
- Live checks:
  - `https://novel-pink-nu.vercel.app/read/ch150`: HTTP 200, contains `ความลับในวิหารใต้ดิน`.
  - `https://novel-pink-nu.vercel.app/books/horror-game-developer/read/ch220`: HTTP 200, contains `วันแรกในฐานะหัวหน้ากลุ่ม`.
  - `https://novel-pink-nu.vercel.app/books/horror-game-developer/chapters`: HTTP 200, contains `ch220`.

## Current Published Scope

- Deep Sea Embers: `ch001-ch150`
- Horror Game Developer: `ch001-ch220`

