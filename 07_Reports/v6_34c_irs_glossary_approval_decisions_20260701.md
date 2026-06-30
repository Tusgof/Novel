# V6.34C IRS Glossary Approval Decisions - 2026-07-01

## Scope

- Experiment vault: `Infinite Regressor Stories/04_Work/_experiments/v6_34c_irs_insample_v1`
- Run ID: `v6-34c-irs-insample-v1`
- Chapters: `ch009,ch076,ch086,ch157,ch183,ch201,ch252,ch300,ch338,ch381`
- Source scan artifact: `Infinite Regressor Stories/04_Work/_experiments/v6_34c_irs_insample_v1/04_Work/_batch/v6-34c-irs-insample-v1/glossary_scan.json`
- Approval packet artifact: `Infinite Regressor Stories/04_Work/_experiments/v6_34c_irs_insample_v1/07_Reports/v6_34c_irs_glossary_approval_packet.json`

## Result

Experiment-local glossary approval is complete.

- New experiment-local glossary notes created: `73`
- Existing experiment-local glossary notes updated with aliases: `7`
- `glossary_approved` ledger records appended: `10`
- Translation/refinement/QA/formatting records: `0`
- Production IRS glossary changed: no
- Production output/MoonRead changed: no

## Approved Terms

Approved terms include:

`Akashic Record`, `Anti-Funeral Faction`, `Babel Tower Plaza`, `Bright Night`, `Brother Undertaker`, `Busan Babel Tower Plaza`, `Commander Noh`, `Data Input`, `Dicentra Spectabilis`, `Divine Realm`, `Dream Simulation`, `Eastern Holy State`, `Eight Desires`, `Final Defense War`, `Fullmetal Alchemist`, `Funeral Faction`, `Great Void`, `Hate Pill`, `Holy Grail War`, `Hyakki Yagyo`, `Infernal Hell`, `Infinite Metagame AI`, `Infinite Void`, `Inunaki Tunnel`, `Jagalchi Market`, `Jeongseon Dwarf Mine`, `Jung Seo-ah`, `Kim Ji-soo`, `King Midas`, `Korean Peninsula Awakeners Alliance`, `Kwan Seum Bosal`, `Lee Ha-yul`, `Literary Girl`, `Magical Girl`, `Magical Girl Association`, `Martial King`, `Mastermind Syndrome`, `Mind Reading`, `Monster Wave`, `NPC Creation`, `National Road Management Corps Commander`, `Neutral Faction`, `Never Ending Story`, `Old English Sheepdog`, `Outer God`, `Outer God Mastermind`, `Outer God-class Anomaly`, `Pet Association`, `Preserved Affection Quantity`, `Reaching Rejuvenation`, `Reality Marble`, `Rebirth Project`, `Regression Alliance`, `Research Facility`, `Romance of the Three Kingdoms`, `Saintess Expression Reading`, `Sejong City`, `Seven Feelings`, `Seven-Year Hiatus Incident`, `Shop Owner`, `Simulated Universe`, `Taebaek Mountains`, `The Cursed Song Incantation`, `The Demoness`, `The Pathbreaker`, `The Receiver`, `Three Kingdoms`, `Three Kingdoms Heavenly Demon`, `Total Luck Law`, `True Dictator Club`, `True Ending`, `Void Poison`, `Warrior Race`

## Alias Updates

Alias updates were applied only inside the experiment vault.

| Existing / Canonical Note | Added Alias Intent |
|---|---|
| `Awakener` | plural/article variants such as `The Awakeners`, `All Awakeners` |
| `Magical Girl` | `The Magical Girl`, `The Magical Girls`, `Magical Girls` |
| `Undertaker` | `Regressor Undertaker`, `The Undertaker`, `Awakener Undertaker`, `Undateikeo` |
| `Outer God` | `The Outer God` |
| `Baekwha Girls' High School` | Baekhwa spelling variants |
| `Infinite Void` | `The Infinite Void` |
| `Great Void` | Great Void variant |
| `Guild Leader` | `Your Guild Leader` |
| `Korean Peninsula` | `The Korean Peninsula` |
| `Eastern Holy State` | `The Eastern Holy State` |
| `Noh Do-hwa` | `The Noh Do-hwa` |
| `The Receiver` | `The Receiver XII` |
| `Romance of the Three Kingdoms` | `The Romance` |
| `Funeral Faction` | `The Funeral Faction Members` |
| `Anti-Funeral Faction` | `The Anti-Funeral Faction Members` |
| `Neutral Faction` | `The Neutral Faction Members` |

## Rejected / Held Out

The CJK candidates from the scan were rejected for this experiment because exact-source checks showed they do not appear in the raw English source files. They are AI-inferred or source-context guesses, not actual tokens to match during translation.

Rejected source-aware/noise examples:

`华山`, `北京`, `仁川`, `天津港`, `送葬者`, `北京攻略指南`, `黄海`, `觉醒者`, `北京地铁`, `北京解放突击队`, `圣女`, `千里眼`, `龙之升华`, `救国圣女`, `魔法少女协会`, `异常体`, `深海余烬`, plus `B-but President`.

## Ledger Verification

Experiment ledger now contains:

- `fetched/completed`: `10`
- `glossary_scanned/completed`: `10`
- `glossary_approved/completed`: `10`
- translation/refinement/QA/formatting/completed records: `0`

`glossary_approved` block IDs:

`ch009`, `ch076`, `ch086`, `ch157`, `ch183`, `ch201`, `ch252`, `ch300`, `ch338`, `ch381`

## Next Safe Action

Resume the isolated experiment run from translation:

```powershell
cd "D:\Fogust\Workspace\Novel\Infinite Regressor Stories\04_Work\_experiments\v6_34c_irs_insample_v1"
$env:PYTHONIOENCODING='utf-8'
novel-pipeline --config ".system/config.yaml" resume --run-id v6-34c-irs-insample-v1 --manual-action-mode stop
```

Stop on provider failure, manual QA prompt, command length failure, validation failure, source mismatch, Sentinel blocker/major, or unexpected scope expansion.

