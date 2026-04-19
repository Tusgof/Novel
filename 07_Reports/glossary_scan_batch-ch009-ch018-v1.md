# Glossary Scan Report: batch-ch009-ch018-v1

## Summary

- **Run ID**: batch-ch009-ch018-v1
- **Chapter range**: ch009-ch018 (10 chapters)
- **Artifact path**: `04_Work/_batch/batch-ch009-ch018-v1/glossary_scan.json`
- **Total candidates**: 30
- **Scan status**: COMPLETED - Pipeline stopped after glossary scan as requested

## Preflight

- **compileall result**: ✅ PASS - No syntax errors in novel_pipeline
- **test_translation.py result**: ✅ PASS - All tests passed
- **Previous batch status**: ✅ batch-ch004-ch008-v2 complete (28/28 blocks, all outputs exist)

## Artifact Details

- **chapter_ids**: ch009, ch010, ch011, ch012, ch013, ch014, ch015, ch016, ch017, ch018
- **item count**: 30 candidate terms

### First 60 Candidate Terms (All 30 shown)

| # | Source Term | Category | Chapter | First Seen Block | Proposed Thai Option |
|---|-------------|----------|---------|------------------|----------------------|
| 1 | 球体 | term | ch009 | ch009-block-001 | (none) |
| 2 | 文明 | term | ch009 | ch009-block-002 | (none) |
| 3 | 些城 | term | ch009 | ch009-block-002 | (none) |
| 4 | 箱子 | term | ch009 | ch009-block-004 | (none) |
| 5 | 火炮 | term | ch010 | ch010-block-002 | (none) |
| 6 | 诅咒人 | term | ch010 | ch010-block-005 | (none) |
| 7 | 海面 | term | ch010 | ch010-block-005 | (none) |
| 8 | 咒人 | term | ch010 | ch010-block-005 | (none) |
| 9 | 幽灵 | term | ch011 | ch011-block-003 | (none) |
| 10 | 汪洋 | term | ch013 | ch013-block-001 | (none) |
| 11 | 深海 | term | ch013 | ch013-block-001 | (none) |
| 12 | 一脸 | term | ch013 | ch013-block-005 | (none) |
| 13 | 航海 | term | ch014 | ch014-block-004 | (none) |
| 14 | 剪影 | term | ch015 | ch015-block-002 | (none) |
| 15 | 罗盘 | term | ch016 | ch016-block-002 | (none) |
| 16 | 毛笔 | term | ch016 | ch016-block-002 | (none) |
| 17 | 光线 | term | ch016 | ch016-block-004 | (none) |
| 18 | 影子 | term | ch016 | ch016-block-005 | (none) |
| 19 | 许多 | term | ch017 | ch017-block-001 | (none) |
| 20 | 睁开眼 | term | ch017 | ch017-block-001 | (none) |
| 21 | 开眼 | term | ch017 | ch017-block-001 | (none) |
| 22 | 阴影 | term | ch017 | ch017-block-002 | (none) |
| 23 | 石头 | term | ch017 | ch017-block-004 | (none) |
| 24 | 尸体 | term | ch017 | ch017-block-004 | (none) |
| 25 | 躯体 | term | ch018 | ch018-block-001 | (none) |
| 26 | 段距 | term | ch018 | ch018-block-003 | (none) |
| 27 | 瓦斯灯 | term | ch018 | ch018-block-003 | (none) |
| 28 | 符号 | term | ch018 | ch018-block-003 | (none) |
| 29 | 斯灯 | term | ch018 | ch018-block-003 | (none) |
| 30 | 文字 | term | ch018 | ch018-block-004 | (none) |

## Candidate Review Notes

### Likely Proper Nouns / Lore Terms (12 terms)
- **球体** (sphere/ball) - Likely refers to the "sun" or celestial body in the novel's cosmology
- **文明** (civilization) - Important concept for world-building
- **火炮** (cannon) - Nautical/military term for the ship's armament
- **诅咒人** (cursed person) - Likely related to "诅咒人偶" (cursed doll)
- **幽灵** (ghost) - Core supernatural concept
- **汪洋** (vast ocean) - Nautical setting term
- **深海** (deep sea) - Nautical/mystical term
- **航海** (navigation) - Core nautical activity
- **剪影** (silhouette) - Descriptive term, may be important for visual imagery
- **罗盘** (compass) - Nautical navigation tool
- **瓦斯灯** (gas lamp) - Period-appropriate technology
- **符号** (symbol) - Likely refers to mystical/magical symbols

### Likely Generic/Common Terms (13 terms)
- **箱子** (box) - Common object
- **海面** (sea surface) - Common nautical description
- **一脸** (face expression) - Common descriptive phrase
- **段距** (segment distance) - Likely measurement term
- **许多** (many) - Common quantifier
- **睁开眼** (open eyes) - Common action
- **躯体** (body) - Common physical description
- **文字** (text) - Common term
- **石头** (stone) - Common object
- **尸体** (corpse) - Common term in horror context
- **阴影** (shadow) - Common descriptive term
- **光线** (light ray) - Common descriptive term
- **影子** (shadow) - Common descriptive term (duplicate of 阴影)

### Likely Substring False Positives (5 terms)
- **些城** - Substring of "那些城邦" (those city-states)
- **咒人** - Substring of "诅咒人偶" (cursed doll)
- **开眼** - Substring of "睁开眼睛" (open eyes)
- **斯灯** - Substring of "瓦斯灯" (gas lamp)
- **毛笔** - Likely misidentified; context suggests "羽毛笔" (feather pen)

### Known Deprecated/Quarantined Hits
- None detected in this scan

### Conflicts with Approved Glossary
- No conflicts detected with existing approved glossary terms
- Checked against: 球体, 文明, 火炮, 诅咒人, 幽灵, 汪洋, 深海, 航海, 剪影, 罗盘, 瓦斯灯, 符号
- None of these terms exist in current approved glossary

## Ledger/Artifact Safety Checks

✅ **Confirmed**:
- glossary_scanned records exist for ch009-ch018 (10 records, lines 444-453 in ledger)
- NO glossary_approved records for this run ID
- NO translation/refinement/QA/formatting records for this run ID
- NO glossary .md notes created/modified by this run (all glossary files last modified April 15-16, 2026)

## Blocker

**None** - Scan completed successfully with no blockers.

## Recommended Next Step

**Proceed to glossary classification/approval gate** with the following considerations:

1. **High-priority terms for approval** (likely proper nouns/lore):
   - 球体, 文明, 火炮, 诅咒人, 幽灵, 汪洋, 深海, 航海, 剪影, 罗盘, 瓦斯灯, 符号

2. **Review needed for generic terms** - Consider whether these need glossary entries or can be translated contextually:
   - 箱子, 海面, 一脸, 段距, 许多, 睁开眼, 躯体, 文字, 石头, 尸体, 阴影, 光线, 影子

3. **Filter out substring false positives**:
   - 些城, 咒人, 开眼, 斯灯, 毛笔 (likely misidentified)

4. **Batch size**: 30 candidates is manageable for human review.

**Recommendation**: Proceed with glossary approval phase for batch-ch009-ch018-v1, focusing first on the 12 high-priority lore terms.