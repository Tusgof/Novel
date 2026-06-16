# HGD Semantic Format Audit

Scope: Horror Game Developer output formatting warnings.
Range: ch001-ch035

This is a warning-only audit. It does not prove content is wrong and does not modify output.

## Summary

- findings: 9

## Findings By Kind

- dialogue_or_quote_embedded_in_long_paragraph: 3
- inline_italic_in_long_paragraph: 1
- many_beats_in_one_paragraph: 5

## Findings By Chapter

- ch003: 1
- ch005: 1
- ch025: 1
- ch031: 5
- ch035: 1

## Detail

| chapter | paragraph | kind | length | excerpt |
| --- | ---: | --- | ---: | --- |
| ch003 | 9 | many_beats_in_one_paragraph | 306 | —รับทราบ บทสนทนานี้คืออะไรกัน? ทำไมพวกเขาถึงฟังดูเหมือนคุ้นเคยกับสถานการณ์นี้อยู่แล้ว? พวกเขาเป็นใคร? ทำไมถึงมาอยู่ที่นี่? และที่สำคัญกว่านั้น ทำไมผมถึงมาอยู... |
| ch005 | 13 | many_beats_in_one_paragraph | 327 | มันต้องหยุดได้แล้ว...'* มือสั่นขณะบังคับตัวเองให้มองตรงไปข้างหน้า ริมฝีปากวาทยากรที่ถูกเย็บปิดด้วยลวดดำขลับ แสยะยิ้มกว้างอย่างน่าขยะแขยง เขากำลังสนุกกับมัน แ... |
| ch025 | 25 | many_beats_in_one_paragraph | 398 | ร่างกายของผมสั่นเทา ถูกเกาะกุมด้วยความกลัวที่ดิบเถื่อนจนรู้สึกเหมือนผิวหนังตึงเป๊ะ ทุกครั้งที่ประตูถูกกระแทก กระเพาะของผมก็บิดมวน พลิกคว่ำพลิกหงายเหมือนมันอย... |
| ch031 | 3 | many_beats_in_one_paragraph | 315 | ฉันกะพริบตาช้าๆ ขยับเข้าไปใกล้ภาพวาดนั้น พื้นหลังยังคงเหมือนเดิม เส้นทางคดเคี้ยวเหมือนเดิม แมกไม้เขียวขจีรอบด้าน ท้องฟ้าสีครามสุดลูกหูลูกตา... ทุกอย่างเหมือน... |
| ch031 | 27 | inline_italic_in_long_paragraph | 429 | ตอนนี้ฉันพักการตัดสินใจไว้ก่อน ส่วนหนึ่งในใจอยากจะปฏิเสธภารกิจ แต่ด้วยการที่มีผู้อำนวยเพลงไล่กวดตามหลังมาติดๆ และรางวัลล่อใจที่รออยู่ ฉันรู้ว่ามันคุ้มค่าที่จ... |
| ch031 | 43 | dialogue_or_quote_embedded_in_long_paragraph | 280 | "...เหตุผลเดียวที่ฉันยอมพิจารณาจะช่วยนายก็เพราะเห็นแก่นายหรอกนะ ไม่อย่างนั้นไม่มีทางที่ฉันจะโปรโมตเกมคุณภาพต่ำที่เพื่อนของนายกำลังพัฒนาอยู่แน่ๆ อันที่จริง ถ้... |
| ch031 | 54 | dialogue_or_quote_embedded_in_long_paragraph | 427 | "...ช่วงนี้เทรนด์สตรีมแนวลึกลับระทึกขวัญกำลังมาแรง ถ้าเพื่อนของนายอยากขายเกม ฉันสามารถแนะนำเขากับครีเอเตอร์ชื่อดังที่ฉันรู้จักให้ได้ ด้วยวิธีนั้น เขาจะสามารถ... |
| ch031 | 54 | many_beats_in_one_paragraph | 427 | "...ช่วงนี้เทรนด์สตรีมแนวลึกลับระทึกขวัญกำลังมาแรง ถ้าเพื่อนของนายอยากขายเกม ฉันสามารถแนะนำเขากับครีเอเตอร์ชื่อดังที่ฉันรู้จักให้ได้ ด้วยวิธีนั้น เขาจะสามารถ... |
| ch035 | 21 | dialogue_or_quote_embedded_in_long_paragraph | 277 | "สนใจหนูหน่อยสิ ข้างนอกมันร้อน หนูไม่ชอบความร้อนเลย หนูอยากอยู่ข้างในแล้วก็เล่นสนุก เหมือนตอนนี้ไง~" เสียงนั้นยังคงกระซิบที่ข้างหู แผ่วเบาลงในทุกวินาที แม้คว... |

## Interpretation

- `inline_italic_in_long_paragraph`: a thought/sound marker may need its own beat.
- `dialogue_or_quote_embedded_in_long_paragraph`: direct speech or quoted sound may be merged into narration.
- `many_beats_in_one_paragraph`: paragraph may be readable but still too rhythmically dense for `good format.md`.
- `system_panel_not_standalone`: game/system panel is not isolated as its own block.

Use these findings to choose AI-format sample chapters. Do not apply mechanical splitting blindly.
