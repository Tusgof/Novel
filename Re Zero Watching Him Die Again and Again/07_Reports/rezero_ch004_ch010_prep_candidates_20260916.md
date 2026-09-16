# Re:Zero ch004-ch010 Sequential Prep Proposal

- Order: `rezero-ch004-ch010-sequential-prep-20260916-v2`
- Status: prepared at glossary-scan gate; no glossary approval, body translation, refinement, QA, formatting, publication, commit, or push was performed.
- Scope: Re:Zero ch004-ch010 only.

## 1. Source and Title Validation

| Chapter | Chapter ID | Source chars | URL chapter match | Anti-bot markers | Title hash | Title checks |
|:--|:--|--:|:--:|:--|:--|:--|
| ch004 | ch004 | 157747 | PASS | none | `a56c64852994eb4df631e927d270a8d6513fbf1bcd34e99f2b4b6fb4c47793d2` | PASS |
| ch005 | ch005 | 226789 | PASS | none | `3fd8811f8caa7de69fef7994bb37e5418ad3307141289bf2888e49357d4f97de` | PASS |
| ch006 | ch006 | 165078 | PASS | none | `5cc45019c98c55a088eb8bff34d540598b8930909aaf963ce315aa6fc7289c61` | PASS |
| ch007 | ch007 | 142466 | PASS | none | `51bd5aa710b54a81240b4c6556a243bfb2eb9ac98eb771ea9151b384b8cadc56` | PASS |
| ch008 | ch008 | 169192 | PASS | none | `623bcbd65f918ee71af0eac0c102bc0d10719e49dd9e834d4e16a9bc94e6077c` | PASS |
| ch009 | ch009 | 206500 | PASS | none | `f704391523ffb6067a8e8a60ce216178ee3a4be1908ad3da87f911677fae8853` | PASS |
| ch010 | ch010 | 314123 | PASS | none | `1ee606622c1385cadb9f2f0999203911c1cef47126145f63cee1c51aabdaf69a` | PASS |

All seven raw sources were readable, non-empty, chapter-id matched, URL matched, and free of the configured anti-bot markers. The title sidecars contain source/literal/Thai titles, Thai characters, and both provider metadata fields.

## 2. Scan Runs

| Chapter | Run ID | Status | Candidates | Artifact |
|:--|:--|:--|--:|:--|
| ch004 | `rezero-ch004-production-v1` | `glossary_scanned/completed` | 47 | `04_Work/ch004/glossary_scan.json` |
| ch005 | `rezero-ch005-production-v1` | `glossary_scanned/completed` | 59 | `04_Work/ch005/glossary_scan.json` |
| ch006 | `rezero-ch006-production-v1` | `glossary_scanned/completed` | 35 | `04_Work/ch006/glossary_scan.json` |
| ch007 | `rezero-ch007-production-v1` | `glossary_scanned/completed` | 42 | `04_Work/ch007/glossary_scan.json` |
| ch008 | `rezero-ch008-production-v1` | `glossary_scanned/completed` | 50 | `04_Work/ch008/glossary_scan.json` |
| ch009 | `rezero-ch009-production-v1` | `glossary_scanned/completed` | 61 | `04_Work/ch009/glossary_scan.json` |
| ch010 | `rezero-ch010-production-v1` | `glossary_scanned/completed` | 81 | `04_Work/ch010/glossary_scan.json` |
| **Total** | 7 unique runs | **completed** | **375** | chapter-scoped artifacts |

The first `run --range ch004-ch004 --stop-after glossary-scan` attempt stopped before glossary scan because the default FanFiction adapter received an anti-bot response. To preserve the read-only raw gate, the remaining scans used the existing raw source directly with `scan-terms`; no raw refetch was performed.

## 3. Proposal Policy

- `APPROVE` means propose a canonical named entity/concept or an alias mapping for later Inspector review. It does not mutate the glossary.
- `REJECT` means keep the phrase out of the glossary because it is extraction noise, a dialogue/prose fragment, a generic description, or a context-only label.
- Honorific variants are proposed as aliases to the canonical name, never as independent glossary entries.

## 4. Candidate Proposals

### ch004

- Artifact: `04_Work/ch004/glossary_scan.json`
- Proposal totals: APPROVE 27; REJECT 20.

| Candidate | First block | Category | Proposal | Rationale |
|:--|:--|:--|:--|:--|
| `Old Man Wil` | ch004-block-001 | term | **APPROVE** | Known character/entity variant; normalize spelling and honorific handling to the canonical glossary key before approval. |
| `Emilia-sama` | ch004-block-001 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Natsuki-kun` | ch004-block-001 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Betty-san` | ch004-block-001 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Otto-kun` | ch004-block-001 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Garfiel-san` | ch004-block-001 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `The Silver-haired` | ch004-block-002 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `Sanctuary Garf` | ch004-block-002 | term | **APPROVE** | Known character/entity variant; normalize spelling and honorific handling to the canonical glossary key before approval. |
| `Yeeees Subaru-kun` | ch004-block-002 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Sir Natsuki` | ch004-block-002 | term | **APPROVE** | Known character/entity variant; normalize spelling and honorific handling to the canonical glossary key before approval. |
| `Crush` | ch004-block-002 | character | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Natsuki` | ch004-block-002 | character | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Subaru-kun` | ch004-block-002 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Stupid Barusu` | ch004-block-003 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `Natsuki Subaru-kun` | ch004-block-003 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Margrave Mathers` | ch004-block-003 | term | **APPROVE** | Known character/entity variant; normalize spelling and honorific handling to the canonical glossary key before approval. |
| `Cap'n` | ch004-block-003 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `Ignoring Julius` | ch004-block-004 | term | **REJECT** | The candidate begins as a prose or dialogue fragment rather than a stable lexical entity. |
| `Margrave Roswaal` | ch004-block-004 | term | **APPROVE** | Known character/entity variant; normalize spelling and honorific handling to the canonical glossary key before approval. |
| `Especially Anastasia` | ch004-block-005 | term | **REJECT** | The candidate begins as a prose or dialogue fragment rather than a stable lexical entity. |
| `Was Subaru` | ch004-block-005 | term | **REJECT** | The candidate begins as a prose or dialogue fragment rather than a stable lexical entity. |
| `The Sword-Saint` | ch004-block-005 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `The Duchess` | ch004-block-005 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Beatrice-sama` | ch004-block-005 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Ros-chi` | ch004-block-005 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Roswaal-sama` | ch004-block-005 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `The Margrave` | ch004-block-006 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `One Puck` | ch004-block-006 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `Two Pucks` | ch004-block-006 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `Roswaal Mansion Family` | ch004-block-006 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Door Crossing` | ch004-block-006 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Garf` | ch004-block-006 | character | **APPROVE** | Known character/entity variant; normalize spelling and honorific handling to the canonical glossary key before approval. |
| `EMA` | ch004-block-006 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `Stupid Roswaal` | ch004-block-007 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `One Emilia-tan` | ch004-block-007 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `Had Otto` | ch004-block-008 | term | **REJECT** | The candidate begins as a prose or dialogue fragment rather than a stable lexical entity. |
| `Alram Village` | ch004-block-008 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Lady Felt-sama` | ch004-block-008 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Senpai` | ch004-block-008 | character | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `Both Ram` | ch004-block-009 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `Including Emilia` | ch004-block-009 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `Styx Helix` | ch004-block-009 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `His Cap'n` | ch004-block-009 | term | **REJECT** | Generic description, relationship, sound, structural label, or one-off phrase; it should remain translated by context rather than enter the glossary. |
| `The Morning` | ch004-block-009 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `Our Promise` | ch004-block-009 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `Still Distant` | ch004-block-009 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `CRACK COCAAAAAINE` | ch004-block-009 | term | **REJECT** | Stammer, shout, sound cue, or sentence fragment; it is not a reusable glossary entry. |

### ch005

- Artifact: `04_Work/ch005/glossary_scan.json`
- Proposal totals: APPROVE 32; REJECT 27.

| Candidate | First block | Category | Proposal | Rationale |
|:--|:--|:--|:--|:--|
| `Web Novel` | ch005-block-001 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Light Novel` | ch005-block-001 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Side Stories` | ch005-block-001 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Had Betty` | ch005-block-001 | term | **REJECT** | The candidate begins as a prose or dialogue fragment rather than a stable lexical entity. |
| `Isn't Roswaal-sama` | ch005-block-001 | term | **REJECT** | The candidate begins as a prose or dialogue fragment rather than a stable lexical entity. |
| `Lady Crusch` | ch005-block-001 | term | **APPROVE** | Known character/entity variant; normalize spelling and honorific handling to the canonical glossary key before approval. |
| `The Emilia` | ch005-block-002 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `The Duchess` | ch005-block-002 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Opening Theme` | ch005-block-002 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Roswaal-sama` | ch005-block-002 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Rem-chan` | ch005-block-002 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Oni` | ch005-block-002 | character | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Subaru-kun` | ch005-block-002 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Emilia-sama` | ch005-block-002 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Poor Beako-chan` | ch005-block-003 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Did Subaru` | ch005-block-003 | term | **REJECT** | The candidate begins as a prose or dialogue fragment rather than a stable lexical entity. |
| `Stupid Subaru` | ch005-block-003 | term | **APPROVE** | Known character/entity variant; normalize spelling and honorific handling to the canonical glossary key before approval. |
| `Crusch-sama` | ch005-block-003 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Garfiel-kun` | ch005-block-003 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Couldn't Subaru` | ch005-block-004 | term | **REJECT** | The candidate begins as a prose or dialogue fragment rather than a stable lexical entity. |
| `Lost Totems Hoshin` | ch005-block-004 | term | **APPROVE** | Known character/entity variant; normalize spelling and honorific handling to the canonical glossary key before approval. |
| `Forbidden Library` | ch005-block-004 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Anastasia-sama` | ch005-block-004 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Subaru-dono` | ch005-block-004 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Like The Red Ogre Who Cried` | ch005-block-005 | term | **REJECT** | The candidate begins as a prose or dialogue fragment rather than a stable lexical entity. |
| `Told Beatrice` | ch005-block-005 | term | **REJECT** | The candidate begins as a prose or dialogue fragment rather than a stable lexical entity. |
| `The Red Ogre Who Cried` | ch005-block-005 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Red Ogre-kun` | ch005-block-005 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `Blue Ogre` | ch005-block-005 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Beautiful Darkness` | ch005-block-005 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `Lia` | ch005-block-005 | character | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Wilhelm-dono` | ch005-block-005 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Both Rem` | ch005-block-006 | term | **REJECT** | The candidate begins as a prose or dialogue fragment rather than a stable lexical entity. |
| `B-But Ram-sama` | ch005-block-006 | term | **REJECT** | Stammer, shout, sound cue, or sentence fragment; it is not a reusable glossary entry. |
| `Morning Star` | ch005-block-006 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Nee-sama` | ch005-block-006 | term | **REJECT** | Generic description, relationship, sound, structural label, or one-off phrase; it should remain translated by context rather than enter the glossary. |
| `Roswaal Estate` | ch005-block-007 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Does Ram` | ch005-block-007 | term | **APPROVE** | Known character/entity variant; normalize spelling and honorific handling to the canonical glossary key before approval. |
| `Sorry Cap` | ch005-block-008 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `Forgive Betty` | ch005-block-008 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `Emilia-tan` | ch005-block-008 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `YOU'RE WRONG` | ch005-block-009 | term | **REJECT** | Stammer, shout, sound cue, or sentence fragment; it is not a reusable glossary entry. |
| `T-The Witch` | ch005-block-010 | term | **REJECT** | Stammer, shout, sound cue, or sentence fragment; it is not a reusable glossary entry. |
| `The Witch` | ch005-block-010 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Head Interior` | ch005-block-011 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `HOLD ON` | ch005-block-011 | term | **REJECT** | Stammer, shout, sound cue, or sentence fragment; it is not a reusable glossary entry. |
| `WHAT ARE YOU DOING` | ch005-block-011 | term | **REJECT** | Stammer, shout, sound cue, or sentence fragment; it is not a reusable glossary entry. |
| `YOU STARTED WITH` | ch005-block-011 | term | **REJECT** | Stammer, shout, sound cue, or sentence fragment; it is not a reusable glossary entry. |
| `HHH BUT NOW YOU'RE JUST NOT` | ch005-block-011 | term | **REJECT** | Stammer, shout, sound cue, or sentence fragment; it is not a reusable glossary entry. |
| `PAUSING OR ANYTHING` | ch005-block-011 | term | **REJECT** | Stammer, shout, sound cue, or sentence fragment; it is not a reusable glossary entry. |
| `Help Rem` | ch005-block-012 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `Was Ram` | ch005-block-013 | term | **REJECT** | The candidate begins as a prose or dialogue fragment rather than a stable lexical entity. |
| `Sir Natsuki` | ch005-block-013 | term | **APPROVE** | Known character/entity variant; normalize spelling and honorific handling to the canonical glossary key before approval. |
| `Straight Bet` | ch005-block-013 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `Hey Subaru` | ch005-block-013 | term | **APPROVE** | Known character/entity variant; normalize spelling and honorific handling to the canonical glossary key before approval. |
| `Styx Helix` | ch005-block-014 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Natsuki Subaru-kun` | ch005-block-014 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Heyyyyyy Sorry` | ch005-block-014 | term | **REJECT** | Generic description, relationship, sound, structural label, or one-off phrase; it should remain translated by context rather than enter the glossary. |
| `Rewrite Moe` | ch005-block-014 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |

### ch006

- Artifact: `04_Work/ch006/glossary_scan.json`
- Proposal totals: APPROVE 24; REJECT 11.

| Candidate | First block | Category | Proposal | Rationale |
|:--|:--|:--|:--|:--|
| `Forgive Betty` | ch006-block-001 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `Inspecting Emilia` | ch006-block-001 | term | **REJECT** | The candidate begins as a prose or dialogue fragment rather than a stable lexical entity. |
| `Candidate Barielle` | ch006-block-001 | term | **APPROVE** | Known character/entity variant; normalize spelling and honorific handling to the canonical glossary key before approval. |
| `Registered Mathers` | ch006-block-001 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `White Whaaaaale` | ch006-block-001 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `The Karsten` | ch006-block-001 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Was Roswaal` | ch006-block-002 | term | **REJECT** | The candidate begins as a prose or dialogue fragment rather than a stable lexical entity. |
| `Gluttony` | ch006-block-002 | character | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `The Second` | ch006-block-003 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `Lady Crusch` | ch006-block-003 | term | **APPROVE** | Known character/entity variant; normalize spelling and honorific handling to the canonical glossary key before approval. |
| `The Duchess` | ch006-block-003 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Subaru-kun` | ch006-block-003 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Al-kun` | ch006-block-003 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Oni` | ch006-block-003 | character | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Beatrice-sama` | ch006-block-004 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Emilia-tan` | ch006-block-004 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Felt-sama` | ch006-block-004 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Lia` | ch006-block-004 | character | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Natsuki-san` | ch006-block-004 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `The Witch` | ch006-block-005 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Garfiel Tanzeil` | ch006-block-005 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Scene Change` | ch006-block-005 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `Beako` | ch006-block-005 | character | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `The Emilia-tan` | ch006-block-006 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Natsuki` | ch006-block-006 | character | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Lungs Out` | ch006-block-007 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `Stopped Crying` | ch006-block-007 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `Surprising Subaru` | ch006-block-008 | term | **REJECT** | The candidate begins as a prose or dialogue fragment rather than a stable lexical entity. |
| `Muraosa` | ch006-block-008 | character | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Senpai` | ch006-block-008 | character | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `Irlam` | ch006-block-008 | character | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `The Meaning` | ch006-block-010 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `Styx Helix` | ch006-block-010 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `SLEEP IS FOR THE WEAK` | ch006-block-010 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `Senku IF` | ch006-block-010 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |

### ch007

- Artifact: `04_Work/ch007/glossary_scan.json`
- Proposal totals: APPROVE 26; REJECT 16.

| Candidate | First block | Category | Proposal | Rationale |
|:--|:--|:--|:--|:--|
| `Lord Roswaal` | ch007-block-001 | term | **APPROVE** | Known character/entity variant; normalize spelling and honorific handling to the canonical glossary key before approval. |
| `How Reinhard` | ch007-block-001 | term | **REJECT** | The candidate begins as a prose or dialogue fragment rather than a stable lexical entity. |
| `The Warden` | ch007-block-001 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Beside Otto` | ch007-block-001 | term | **REJECT** | The candidate begins as a prose or dialogue fragment rather than a stable lexical entity. |
| `Beatrice-sama` | ch007-block-001 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Natsuki-kun` | ch007-block-001 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Oni` | ch007-block-001 | character | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Subaru-kun` | ch007-block-001 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Has Emilia` | ch007-block-002 | term | **REJECT** | The candidate begins as a prose or dialogue fragment rather than a stable lexical entity. |
| `Both Ram` | ch007-block-002 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `Did Puck` | ch007-block-002 | term | **REJECT** | The candidate begins as a prose or dialogue fragment rather than a stable lexical entity. |
| `Forget Bubby` | ch007-block-002 | term | **APPROVE** | Known character/entity variant; normalize spelling and honorific handling to the canonical glossary key before approval. |
| `Bubby` | ch007-block-002 | character | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Beako` | ch007-block-002 | character | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Knowing Natsuki` | ch007-block-003 | term | **REJECT** | The candidate begins as a prose or dialogue fragment rather than a stable lexical entity. |
| `Because Rem` | ch007-block-003 | term | **REJECT** | The candidate begins as a prose or dialogue fragment rather than a stable lexical entity. |
| `Big Bro` | ch007-block-003 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `Unlike Rem` | ch007-block-003 | term | **REJECT** | The candidate begins as a prose or dialogue fragment rather than a stable lexical entity. |
| `The Duchess` | ch007-block-003 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Miss Hoshin` | ch007-block-003 | term | **APPROVE** | Known character/entity variant; normalize spelling and honorific handling to the canonical glossary key before approval. |
| `Natsuki` | ch007-block-003 | character | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Rem-san` | ch007-block-003 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Stupid Barusu` | ch007-block-004 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `The Witch` | ch007-block-004 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `The Sword` | ch007-block-004 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `Ram-chi` | ch007-block-004 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Rem-rin` | ch007-block-004 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `The Roswaal` | ch007-block-005 | term | **APPROVE** | Known character/entity variant; normalize spelling and honorific handling to the canonical glossary key before approval. |
| `Demonically Inspired Methods` | ch007-block-005 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `THUNDER NOISES` | ch007-block-006 | term | **REJECT** | Stammer, shout, sound cue, or sentence fragment; it is not a reusable glossary entry. |
| `Potatoes Rem` | ch007-block-006 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `Little Rem` | ch007-block-006 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `Natsuki-sama` | ch007-block-007 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Natsuki-san` | ch007-block-007 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Holy Dragon` | ch007-block-008 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Big Sis` | ch007-block-008 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `Styx Helix` | ch007-block-009 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Second Arc` | ch007-block-009 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `The Tumultuous Week` | ch007-block-009 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `OVA Episode Memory Snow` | ch007-block-009 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Frozen Bonds` | ch007-block-009 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Senku IF` | ch007-block-009 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |

### ch008

- Artifact: `04_Work/ch008/glossary_scan.json`
- Proposal totals: APPROVE 26; REJECT 24.

| Candidate | First block | Category | Proposal | Rationale |
|:--|:--|:--|:--|:--|
| `B-Because S-Subaru` | ch008-block-001 | term | **REJECT** | Stammer, shout, sound cue, or sentence fragment; it is not a reusable glossary entry. |
| `Lady Felt` | ch008-block-001 | term | **APPROVE** | Known character/entity variant; normalize spelling and honorific handling to the canonical glossary key before approval. |
| `Lady Felt-sama` | ch008-block-001 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Emilia-tan` | ch008-block-001 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `B-But Emilia-sama` | ch008-block-002 | term | **REJECT** | Stammer, shout, sound cue, or sentence fragment; it is not a reusable glossary entry. |
| `Because Wilhelm` | ch008-block-003 | term | **REJECT** | The candidate begins as a prose or dialogue fragment rather than a stable lexical entity. |
| `LET ME INNNNNN` | ch008-block-003 | term | **REJECT** | Stammer, shout, sound cue, or sentence fragment; it is not a reusable glossary entry. |
| `Rick Sanchez` | ch008-block-003 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `LET THEM OOUUUUUTTT` | ch008-block-003 | term | **REJECT** | Stammer, shout, sound cue, or sentence fragment; it is not a reusable glossary entry. |
| `I-Is Subaru` | ch008-block-003 | term | **REJECT** | Stammer, shout, sound cue, or sentence fragment; it is not a reusable glossary entry. |
| `Memory Snow` | ch008-block-003 | term | **REJECT** | Generic description, relationship, sound, structural label, or one-off phrase; it should remain translated by context rather than enter the glossary. |
| `Did Subaru` | ch008-block-003 | term | **REJECT** | The candidate begins as a prose or dialogue fragment rather than a stable lexical entity. |
| `Like Emilia` | ch008-block-003 | term | **REJECT** | The candidate begins as a prose or dialogue fragment rather than a stable lexical entity. |
| `Beako-chan` | ch008-block-003 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Kazuma` | ch008-block-003 | character | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Ulgarm Mabeast` | ch008-block-004 | term | **REJECT** | Generic description, relationship, sound, structural label, or one-off phrase; it should remain translated by context rather than enter the glossary. |
| `Fashion Police` | ch008-block-004 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Did Natsuki-sama` | ch008-block-004 | term | **REJECT** | The candidate begins as a prose or dialogue fragment rather than a stable lexical entity. |
| `The Emilia` | ch008-block-004 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `Quiet Aldebaran` | ch008-block-004 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `F-U-C-K TATOES` | ch008-block-004 | term | **REJECT** | Stammer, shout, sound cue, or sentence fragment; it is not a reusable glossary entry. |
| `Stop Barusu` | ch008-block-004 | term | **APPROVE** | Known character/entity variant; normalize spelling and honorific handling to the canonical glossary key before approval. |
| `Roswaal-sama` | ch008-block-004 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Lady Roswaal` | ch008-block-005 | term | **APPROVE** | Known character/entity variant; normalize spelling and honorific handling to the canonical glossary key before approval. |
| `Drunken Emilia-tan` | ch008-block-005 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `Eminem Emilia` | ch008-block-005 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `Yeah- Wait` | ch008-block-005 | term | **REJECT** | Generic description, relationship, sound, structural label, or one-off phrase; it should remain translated by context rather than enter the glossary. |
| `Natsuki-san` | ch008-block-005 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Otto-kun` | ch008-block-005 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Ros-chi` | ch008-block-005 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Nee-sama` | ch008-block-006 | term | **REJECT** | Generic description, relationship, sound, structural label, or one-off phrase; it should remain translated by context rather than enter the glossary. |
| `Subaru-kun` | ch008-block-006 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Operation Hot Springs` | ch008-block-007 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Forbidden Library` | ch008-block-007 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Door Crossing` | ch008-block-007 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Chiki Chiki` | ch008-block-007 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `Lady Liberty` | ch008-block-007 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `New York` | ch008-block-007 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Man Subaru` | ch008-block-007 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `Preistella` | ch008-block-007 | character | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Bueno Aires` | ch008-block-008 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Beako` | ch008-block-008 | character | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Snow Rabbit` | ch008-block-009 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Poor Subaru` | ch008-block-009 | term | **APPROVE** | Known character/entity variant; normalize spelling and honorific handling to the canonical glossary key before approval. |
| `Subaru-kun Subaru-kun Subaru-kun` | ch008-block-009 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `FUCK APPAS TOO` | ch008-block-009 | term | **REJECT** | Stammer, shout, sound cue, or sentence fragment; it is not a reusable glossary entry. |
| `The Appa` | ch008-block-009 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `Mother Fortuna` | ch008-block-010 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Third Arc` | ch008-block-010 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Roswaal Hector Emilia Garfiel` | ch008-block-010 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |

### ch009

- Artifact: `04_Work/ch009/glossary_scan.json`
- Proposal totals: APPROVE 44; REJECT 17.

| Candidate | First block | Category | Proposal | Rationale |
|:--|:--|:--|:--|:--|
| `Third Arc` | ch009-block-001 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Big Bro` | ch009-block-001 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `The Duchess` | ch009-block-001 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Cap'n` | ch009-block-001 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `Natsuki` | ch009-block-001 | character | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Subaru-dono` | ch009-block-001 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Sloth` | ch009-block-001 | character | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Old Man Wil` | ch009-block-002 | term | **APPROVE** | Known character/entity variant; normalize spelling and honorific handling to the canonical glossary key before approval. |
| `Fuck You` | ch009-block-002 | term | **REJECT** | Generic description, relationship, sound, structural label, or one-off phrase; it should remain translated by context rather than enter the glossary. |
| `Making Subaru` | ch009-block-002 | term | **REJECT** | The candidate begins as a prose or dialogue fragment rather than a stable lexical entity. |
| `Emilia-sama` | ch009-block-002 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Emilia-tan` | ch009-block-002 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Subaru-san` | ch009-block-002 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Secret Technique` | ch009-block-003 | term | **REJECT** | Generic description, relationship, sound, structural label, or one-off phrase; it should remain translated by context rather than enter the glossary. |
| `Duchess` | ch009-block-003 | character | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Lady Felt` | ch009-block-004 | term | **APPROVE** | Known character/entity variant; normalize spelling and honorific handling to the canonical glossary key before approval. |
| `Julius Juukilous` | ch009-block-004 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Think Natsuki-kun` | ch009-block-004 | term | **REJECT** | The candidate begins as a prose or dialogue fragment rather than a stable lexical entity. |
| `WHY ARE YOU ASKING ME THAT` | ch009-block-004 | term | **REJECT** | Stammer, shout, sound cue, or sentence fragment; it is not a reusable glossary entry. |
| `Crusch-sama` | ch009-block-004 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Julius-kun` | ch009-block-004 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Petra-chan` | ch009-block-004 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Sir Natsuki` | ch009-block-005 | term | **APPROVE** | Known character/entity variant; normalize spelling and honorific handling to the canonical glossary key before approval. |
| `Lady Crusch` | ch009-block-005 | term | **APPROVE** | Known character/entity variant; normalize spelling and honorific handling to the canonical glossary key before approval. |
| `Princess` | ch009-block-005 | character | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `Witchling` | ch009-block-005 | character | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Miss Emilia` | ch009-block-006 | term | **APPROVE** | Known character/entity variant; normalize spelling and honorific handling to the canonical glossary key before approval. |
| `Now Garfiel` | ch009-block-006 | term | **REJECT** | The candidate begins as a prose or dialogue fragment rather than a stable lexical entity. |
| `Grandpa Cromwell` | ch009-block-006 | term | **APPROVE** | Known character/entity variant; normalize spelling and honorific handling to the canonical glossary key before approval. |
| `Barialle-sama` | ch009-block-006 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Oni` | ch009-block-006 | character | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `The House` | ch009-block-007 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `YOU BIG FUCKIN` | ch009-block-007 | term | **REJECT** | Stammer, shout, sound cue, or sentence fragment; it is not a reusable glossary entry. |
| `Miss Felt-sama` | ch009-block-007 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Market Street` | ch009-block-007 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Felt-sama` | ch009-block-007 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Miss Hoshin` | ch009-block-008 | term | **APPROVE** | Known character/entity variant; normalize spelling and honorific handling to the canonical glossary key before approval. |
| `Priscilla Barielle-sama` | ch009-block-009 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Imperial Knights` | ch009-block-009 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Lord Miklotov` | ch009-block-009 | term | **APPROVE** | Known character/entity variant; normalize spelling and honorific handling to the canonical glossary key before approval. |
| `Continue Marcos` | ch009-block-010 | term | **REJECT** | The candidate begins as a prose or dialogue fragment rather than a stable lexical entity. |
| `Knight Reinhard` | ch009-block-010 | term | **APPROVE** | Known character/entity variant; normalize spelling and honorific handling to the canonical glossary key before approval. |
| `Dragon Stone` | ch009-block-010 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `All Royal Knights` | ch009-block-010 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Heavenly Dragon Sword` | ch009-block-010 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Crusch Karsten-sama` | ch009-block-010 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Anastasia Hoshin-sama` | ch009-block-010 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Julius Euclius` | ch009-block-010 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Margrave Roswaal` | ch009-block-010 | term | **APPROVE** | Known character/entity variant; normalize spelling and honorific handling to the canonical glossary key before approval. |
| `The Astrea` | ch009-block-010 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Margrave Mathers` | ch009-block-010 | term | **APPROVE** | Known character/entity variant; normalize spelling and honorific handling to the canonical glossary key before approval. |
| `Filthy Woman` | ch009-block-010 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `Damn Barusu` | ch009-block-010 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `Dragon Throne` | ch009-block-010 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Natsuki Subaru-dono` | ch009-block-011 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Why Subaru` | ch009-block-011 | term | **REJECT** | The candidate begins as a prose or dialogue fragment rather than a stable lexical entity. |
| `Don't Subaru` | ch009-block-011 | term | **REJECT** | The candidate begins as a prose or dialogue fragment rather than a stable lexical entity. |
| `Stay Alive` | ch009-block-012 | term | **REJECT** | The candidate begins as a prose or dialogue fragment rather than a stable lexical entity. |
| `Self-Proclaimed Knight Natsuki Subaru` | ch009-block-012 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `The Witch` | ch009-block-012 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Senku IF` | ch009-block-012 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |

### ch010

- Artifact: `04_Work/ch010/glossary_scan.json`
- Proposal totals: APPROVE 38; REJECT 43.

| Candidate | First block | Category | Proposal | Rationale |
|:--|:--|:--|:--|:--|
| `FAIR WARNING` | ch010-block-001 | term | **REJECT** | Stammer, shout, sound cue, or sentence fragment; it is not a reusable glossary entry. |
| `Priscilla Barialle` | ch010-block-001 | term | **APPROVE** | Known character/entity variant; normalize spelling and honorific handling to the canonical glossary key before approval. |
| `Natsuki Subaru-kun` | ch010-block-002 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Both Beatrice` | ch010-block-002 | term | **REJECT** | The candidate begins as a prose or dialogue fragment rather than a stable lexical entity. |
| `The Margrave` | ch010-block-002 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Leave Ram` | ch010-block-002 | term | **REJECT** | The candidate begins as a prose or dialogue fragment rather than a stable lexical entity. |
| `Beatrice-sama` | ch010-block-002 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Ram-sama` | ch010-block-002 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `GET WHAT YOU GAVE MY CAP'N` | ch010-block-003 | term | **REJECT** | Stammer, shout, sound cue, or sentence fragment; it is not a reusable glossary entry. |
| `MINE AMAZIN' SELFS IS MORE THAN` | ch010-block-003 | term | **REJECT** | Stammer, shout, sound cue, or sentence fragment; it is not a reusable glossary entry. |
| `HAPPY TO PAY YA BACK` | ch010-block-003 | term | **REJECT** | Stammer, shout, sound cue, or sentence fragment; it is not a reusable glossary entry. |
| `DUN TELL ME` | ch010-block-003 | term | **REJECT** | Stammer, shout, sound cue, or sentence fragment; it is not a reusable glossary entry. |
| `CONTAIN SHIT` | ch010-block-003 | term | **REJECT** | Stammer, shout, sound cue, or sentence fragment; it is not a reusable glossary entry. |
| `YER THE ONE THAT TREATED MY` | ch010-block-003 | term | **REJECT** | Stammer, shout, sound cue, or sentence fragment; it is not a reusable glossary entry. |
| `HURT JUST BECAUSE HE BROUGHT UP` | ch010-block-003 | term | **REJECT** | Stammer, shout, sound cue, or sentence fragment; it is not a reusable glossary entry. |
| `WE'RE GOIN' NOW YA SON'OVA` | ch010-block-003 | term | **REJECT** | Stammer, shout, sound cue, or sentence fragment; it is not a reusable glossary entry. |
| `Garf-san` | ch010-block-003 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `The Greatest Knight` | ch010-block-004 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `M-My Master` | ch010-block-004 | term | **REJECT** | Stammer, shout, sound cue, or sentence fragment; it is not a reusable glossary entry. |
| `Emilia-sama` | ch010-block-004 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Julius-san` | ch010-block-004 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Natsuki-san` | ch010-block-004 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Oni` | ch010-block-004 | character | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `The Duchess` | ch010-block-005 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Crusch-sama` | ch010-block-005 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Priscilla-sama` | ch010-block-005 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Duchess` | ch010-block-005 | character | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Barielle` | ch010-block-005 | character | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Boss Ricardo` | ch010-block-006 | term | **APPROVE** | Known character/entity variant; normalize spelling and honorific handling to the canonical glossary key before approval. |
| `WHO ARE YOU` | ch010-block-006 | term | **REJECT** | Stammer, shout, sound cue, or sentence fragment; it is not a reusable glossary entry. |
| `YOU SWORE TO GOD` | ch010-block-006 | term | **REJECT** | Stammer, shout, sound cue, or sentence fragment; it is not a reusable glossary entry. |
| `PERFECT EXPLANATION` | ch010-block-006 | term | **REJECT** | Stammer, shout, sound cue, or sentence fragment; it is not a reusable glossary entry. |
| `Demi-Human` | ch010-block-006 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Hetaro` | ch010-block-006 | character | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Mama` | ch010-block-006 | character | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `The Karsten` | ch010-block-007 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Hello Emilia-sama` | ch010-block-007 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `House Karsten` | ch010-block-007 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Opening Theme` | ch010-block-007 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Said Rem` | ch010-block-007 | term | **REJECT** | The candidate begins as a prose or dialogue fragment rather than a stable lexical entity. |
| `Wilhelm-dono` | ch010-block-007 | term | **APPROVE** | Address form or nickname of a known entity; approve only as an alias mapping, not as a separate Thai glossary key. |
| `Will Subaru-kun` | ch010-block-008 | term | **REJECT** | The candidate begins as a prose or dialogue fragment rather than a stable lexical entity. |
| `Asked Garfiel` | ch010-block-008 | term | **REJECT** | The candidate begins as a prose or dialogue fragment rather than a stable lexical entity. |
| `Yet Felix` | ch010-block-008 | term | **REJECT** | The candidate begins as a prose or dialogue fragment rather than a stable lexical entity. |
| `Patrasche` | ch010-block-008 | character | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Old Man Wil` | ch010-block-009 | term | **APPROVE** | Known character/entity variant; normalize spelling and honorific handling to the canonical glossary key before approval. |
| `CAN YA ALL SHUT TH' HELL` | ch010-block-009 | term | **REJECT** | Stammer, shout, sound cue, or sentence fragment; it is not a reusable glossary entry. |
| `Big Bro` | ch010-block-009 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `The Apple` | ch010-block-010 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `Novel Scene` | ch010-block-010 | term | **REJECT** | Generic description, relationship, sound, structural label, or one-off phrase; it should remain translated by context rather than enter the glossary. |
| `Lady Crusch` | ch010-block-010 | term | **APPROVE** | Known character/entity variant; normalize spelling and honorific handling to the canonical glossary key before approval. |
| `Promise Crusch-sama` | ch010-block-011 | term | **REJECT** | The candidate begins as a prose or dialogue fragment rather than a stable lexical entity. |
| `Has Rem` | ch010-block-011 | term | **REJECT** | The candidate begins as a prose or dialogue fragment rather than a stable lexical entity. |
| `The Archbishop` | ch010-block-011 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `The Rem` | ch010-block-012 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `Witch Cultists` | ch010-block-013 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `WHO WOULD DO THIS` | ch010-block-014 | term | **REJECT** | Stammer, shout, sound cue, or sentence fragment; it is not a reusable glossary entry. |
| `WHAT KIND OF MONSTER` | ch010-block-014 | term | **REJECT** | Stammer, shout, sound cue, or sentence fragment; it is not a reusable glossary entry. |
| `The Baroness` | ch010-block-014 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `The Sickness Called Despair` | ch010-block-014 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Damn Cult` | ch010-block-014 | term | **REJECT** | Generic description, relationship, sound, structural label, or one-off phrase; it should remain translated by context rather than enter the glossary. |
| `I'MMA KILL THESE FUCKIN' MONSTEEEEEEERS` | ch010-block-014 | term | **REJECT** | Stammer, shout, sound cue, or sentence fragment; it is not a reusable glossary entry. |
| `Petra Lyte` | ch010-block-014 | term | **APPROVE** | Known character/entity variant; normalize spelling and honorific handling to the canonical glossary key before approval. |
| `Both Rem` | ch010-block-015 | term | **REJECT** | The candidate begins as a prose or dialogue fragment rather than a stable lexical entity. |
| `Give Emilia` | ch010-block-015 | term | **REJECT** | The candidate begins as a prose or dialogue fragment rather than a stable lexical entity. |
| `Big Brother` | ch010-block-015 | term | **REJECT** | Known extraction noise, generic label, or one-off descriptive phrase; keep it in context and do not add it to the glossary. |
| `Making Crusch` | ch010-block-015 | term | **REJECT** | The candidate begins as a prose or dialogue fragment rather than a stable lexical entity. |
| `Carrying Subaru` | ch010-block-016 | term | **REJECT** | The candidate begins as a prose or dialogue fragment rather than a stable lexical entity. |
| `Betelgeuse Romanee-Conti` | ch010-block-016 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `HOPE SUBARU KILLS YOU AND NEVER` | ch010-block-016 | term | **REJECT** | Stammer, shout, sound cue, or sentence fragment; it is not a reusable glossary entry. |
| `LOOKS BACK` | ch010-block-016 | term | **REJECT** | Stammer, shout, sound cue, or sentence fragment; it is not a reusable glossary entry. |
| `Father Guese` | ch010-block-016 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `Will Rem` | ch010-block-016 | term | **REJECT** | The candidate begins as a prose or dialogue fragment rather than a stable lexical entity. |
| `COME ON` | ch010-block-017 | term | **REJECT** | Stammer, shout, sound cue, or sentence fragment; it is not a reusable glossary entry. |
| `Unseen Hand` | ch010-block-017 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `DON'T SAY THAT` | ch010-block-017 | term | **REJECT** | Stammer, shout, sound cue, or sentence fragment; it is not a reusable glossary entry. |
| `The Ordeal` | ch010-block-017 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `The Outside` | ch010-block-018 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `The Warden` | ch010-block-018 | term | **APPROVE** | Stable proper name, epithet, place, faction, item, work, arc, or named concept; normalize to the canonical glossary key before approval. |
| `DON'T WANT YOU TO SUFFER WHAT` | ch010-block-018 | term | **REJECT** | Stammer, shout, sound cue, or sentence fragment; it is not a reusable glossary entry. |
| `FUCKING LAUGH` | ch010-block-019 | term | **REJECT** | Stammer, shout, sound cue, or sentence fragment; it is not a reusable glossary entry. |

## 5. Incidents and Next Action

- Recoverable execution incident: the first title command was run from the DSE working directory without an explicit Re:Zero config, so it used the DSE default config and touched DSE title/log paths. The corrected command used `--config ..\Re Zero Watching Him Die Again and Again\.system\config.yaml` and produced the Re:Zero sidecars.
- Recoverable fetch incident: the first batch scan attempt used the configured FanFiction adapter and stopped on anti-bot before glossary work. The safe local-raw scan path completed all seven scan gates.
- Provider incidents during the successful title/scan work: none surfaced as command failures or manual prompts. The scan ledger records the gate commit as `provider=local`; it does not expose per-block fallback telemetry.
- Next action: Inspector reviews this proposal, then separately approves or rejects terms. Only after approval may body translation begin.
