# Glossary Classification: batch-ch009-ch018-v1

## Summary
- **Run ID**: batch-ch009-ch018-v1
- **Total candidates**: 30
- **Auto Approve count**: 0
- **Auto Reject count**: 23
- **Ask Human count**: 7
- **Recommendation**: Proceed with auto-reject list; seek human input for 7 ambiguous terms before approval phase.

## Auto Approve
No terms meet the strict criteria for auto-approval (clear proper nouns, named ships/organizations/places, or unequivocally central recurring lore terms).

## Auto Reject
| Source Term | Reason | First Seen Chapter | First Seen Block | Related Longer Term |
|-------------|--------|-------------------|------------------|---------------------|
| 球体 | Generic descriptive term ("sphere"), not a proper noun | ch009 | ch009-block-001 | |
| 文明 | Generic noun ("civilization") | ch009 | ch009-block-002 | |
| 些城 | Substring false positive of "那些城邦" | ch009 | ch009-block-002 | 那些城邦 |
| 箱子 | Generic object ("box") | ch009 | ch009-block-004 | |
| 火炮 | Generic nautical term ("cannon") | ch010 | ch010-block-002 | |
| 诅咒人 | Substring fragment of "诅咒人偶" | ch010 | ch010-block-005 | 诅咒人偶 |
| 海面 | Generic term ("sea surface") | ch010 | ch010-block-005 | |
| 咒人 | Substring fragment of "诅咒人偶" | ch010 | ch010-block-005 | 诅咒人偶 |
| 一脸 | Generic descriptive phrase ("face expression") | ch013 | ch013-block-005 | |
| 剪影 | Generic descriptive term ("silhouette") | ch015 | ch015-block-002 | |
| 罗盘 | Generic item ("compass") | ch016 | ch016-block-002 | |
| 毛笔 | Likely misidentified; context suggests "羽毛笔" (feather pen) | ch016 | ch016-block-002 | |
| 光线 | Generic term ("light ray") | ch016 | ch016-block-004 | |
| 影子 | Generic term ("shadow") | ch016 | ch016-block-005 | |
| 许多 | Generic quantifier ("many") | ch017 | ch017-block-001 | |
| 睁开眼 | Generic phrase ("open eyes") | ch017 | ch017-block-001 | |
| 开眼 | Substring fragment of "睁开眼睛" | ch017 | ch017-block-001 | 睁开眼睛 |
| 阴影 | Generic term ("shadow") | ch017 | ch017-block-002 | |
| 石头 | Generic object ("stone") | ch017 | ch017-block-004 | |
| 躯体 | Generic term ("body") | ch018 | ch018-block-001 | |
| 段距 | Likely measurement term ("segment distance") | ch018 | ch018-block-003 | |
| 斯灯 | Substring fragment of "瓦斯灯" | ch018 | ch018-block-003 | 瓦斯灯 |
| 文字 | Generic term ("text") | ch018 | ch018-block-004 | |

## Ask Human
| Source Term | Possible Thai Options | Category Guess | First Seen Chapter | First Seen Block | Context Summary | Question for User | Risk if Wrong |
|-------------|----------------------|----------------|-------------------|------------------|-----------------|-------------------|---------------|
| 幽灵 | 1) ผี (ghost) 2) วิญญาณ (spirit) 3) ภูต (phantom) | entity / phenomenon | ch011 | ch011-block-003 | Appears in "幽灵烈焰" (ghostly flames) and "幽灵船长" (ghost captain). Core supernatural concept in dark fantasy setting. | Should "幽灵" be added as a glossary term? If yes, what Thai rendering (ผี, วิญญาณ, ภูต) best fits the novel's tone? | Inconsistent translation of "ghost/phantom" concepts across chapters. |
| 汪洋 | 1) มหาสมุทรไร้ขอบเขต (boundless ocean) 2) ทะเลกว้างใหญ่ (vast sea) 3) มหาสมุทร (ocean) | phenomenon | ch013 | ch013-block-001 | Poetic term for "vast ocean", appears in "无尽汪洋" (endless vast ocean). May recur as setting descriptor. | Is "汪洋" important enough for glossary consistency, or can it be translated contextually? If glossary, what Thai poetic equivalent? | Minor stylistic inconsistency in ocean descriptions. |
| 深海 | 1) ทะเลลึก (deep sea) 2) มหาสมุทรลึก (deep ocean) | phenomenon / location | ch013 | ch013-block-001 | Appears in "深海是值得恐惧的" (the deep sea is worthy of fear). May be a recurring domain term distinct from "幽邃深海". | "深海" is a substring of approved "幽邃深海". Should it have its own entry? If yes, what Thai term? | Potential conflict with "幽邃深海"; may cause double‑matching issues. |
| 航海 | 1) การเดินเรือ (navigation) 2) การแล่นเรือ (sailing) | activity / title | ch014 | ch014-block-004 | Core nautical activity; appears in "航海桌" (navigation table). May recur in compound terms. | Is "航海" a glossary‑worthy term, or generic enough for contextual translation? | Inconsistent rendering of navigation‑related terms. |
| 尸体 | 1) ศพ (corpse) 2) ซากศพ (dead body) | entity | ch017 | ch017-block-004 | Horror context; appears in descriptions of corpses in a cave. May recur in grim scenes. | Should "尸体" be glossaried for consistency in horror descriptions, or treated as generic? | Minor inconsistency in corpse/body terminology. |
| 瓦斯灯 | 1) โคมไฟแก๊ส (gas lamp) 2) ตะเกียงแก๊ส (gas lantern) | item | ch018 | ch018-block-003 | Period‑appropriate technology; appears in underground tunnel setting. Likely recurs as setting detail. | Should "瓦斯灯" be added as a glossary item for consistent rendering? | Inconsistent technology terminology. |
| 符号 | 1) สัญลักษณ์ (symbol) 2) เครื่องหมาย (mark) 3) อักษร (character) | item | ch018 | ch018-block-003 | Appears in context of mystical symbols on gas lamps; likely refers to magical/religious symbols. | Is "符号" a glossary‑worthy term for mystical symbols, or generic? | Inconsistent translation of symbol/mark concepts. |

## Substring / Noise Analysis
Detected substring clusters:
1. **城邦 group**: 些城 (fragment of 那些城邦)
2. **诅咒人偶 group**: 诅咒人, 咒人 (fragments of 诅咒人偶)
3. **睁开眼睛 group**: 睁开眼, 开眼 (fragments of 睁开眼睛)
4. **瓦斯灯 group**: 斯灯 (fragment of 瓦斯灯)

Noisy fragments:
- 毛笔 (likely misidentification of 羽毛笔)
- 段距 (likely measurement fragment)

## Existing Glossary Conflicts
- **深海**: Substring of approved term "幽邃深海" (ทะเลลึกอันเร้นลับ). This may cause longest‑match issues if both terms appear. No other conflicts detected.

## Recommendation
**Recommended next action**:
1. **Approve auto‑reject list immediately** – 23 terms are clearly generic/substring/false positives and can be rejected without human review.
2. **Present ask‑human list to user** – 7 terms need human decision on glossary worthiness and Thai rendering.
3. **After human decisions**, proceed with glossary approval phase for batch‑ch009‑ch018‑v1.

**Classification confidence**: High for auto‑reject list; medium for ask‑human list (terms have plausible arguments both for and against inclusion).

**Note**: No auto‑approve terms identified under strict policy; all proper‑noun‑like terms (e.g., 球体, 火炮) were judged generic upon context inspection.