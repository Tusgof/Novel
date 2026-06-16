# QA Provider Cost/Quality Benchmark - qa_provider_benchmark_20260609_134420

Generated: 2026-06-09T14:23:26

## Scope

- Non-production QA-only comparison.
- Production routing was not changed.
- Compared `deepseek/deepseek-v4-pro`, `deepseek/deepseek-v4-flash`, and Qwen CLI current QA route.
- Cases: 30 total: 10 known-pass, 10 historical-recovery-derived fail cases, 10 adversarial fail cases.

## Summary

| Candidate | Provider | Model | Calls | Avg score | False negatives | Severe false negatives | False positives | Parse failures | Provider failures | Avg latency | Est. cost | Est. cost / 100 blocks |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `openrouter_v4_pro` | openrouter | `deepseek/deepseek-v4-pro` | 30 | 66.00 | 1 | 1 | 2 | 13 | 0 | 10.990s | 0.03095155 | 0.103172 |
| `openrouter_v4_flash` | openrouter | `deepseek/deepseek-v4-flash` | 30 | 80.17 | 4 | 4 | 1 | 4 | 0 | 5.836s | 0.00647915 | 0.021597 |
| `qwen_cli` | qwen | `deepseek-reasoner` | 30 | 88.00 | 0 | 0 | 2 | 3 | 3 | 61.326s | n/a | n/a |

## Recommendation

No candidate cleared the severe-false-negative gate; keep QA routing unchanged and rerun with repaired fixtures/providers.

## Per-Case Results

| Candidate | Case | Group | Expected | Predicted | Score | Latency | Cost | First line |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |
| `openrouter_v4_pro` | `pass__ch001-block-001` | known_pass | pass | pass | 100 | 2.468s | 0.00089436 | PASS: Translation is complete, no omissions or additions, meaning is accurate, names and terms are consistent, no Chinese leakage, tone matches the source. |
| `openrouter_v4_pro` | `pass__ch002-block-003` | known_pass | pass | unknown | 35 | 12.826s | 0.0012332250000000001 | None |
| `openrouter_v4_pro` | `pass__ch006-block-004` | known_pass | pass | unknown | 35 | 10.624s | 0.00126063 | None |
| `openrouter_v4_pro` | `pass__ch011-block-002` | known_pass | pass | unknown | 35 | 11.976s | 0.00083781 | None |
| `openrouter_v4_pro` | `pass__ch016-block-005` | known_pass | pass | fail | 45 | 5.323s | 0.0007999649999999999 | FAIL: Missing translation of the Chinese interjection "妈耶！" — the Thai text uses "แม่เจ้า!" which is a different expression and does not match the source's tone or meaning. |
| `openrouter_v4_pro` | `pass__ch021-block-004` | known_pass | pass | pass | 100 | 2.250s | 0.000927855 | PASS: Translation is complete, accurate, and consistent with source; no omissions, additions, meaning drift, name/glossary errors, Chinese leakage, or tone issues. |
| `openrouter_v4_pro` | `pass__ch027-block-003` | known_pass | pass | pass | 100 | 13.333s | 0.001254975 | PASS: All source content faithfully translated with no omissions, additions, meaning drift, Chinese leakage, or issue in name consistency or tone; only note is using "เรือผู้ไร้บ้า |
| `openrouter_v4_pro` | `pass__ch033-block-005` | known_pass | pass | fail | 45 | 1.906s | 0.00059073 | FAIL: Chinese leakage in Thai body text: "摆" remains untranslated in "พ่นฟองอากาศออกมา摆ขยับหาง". |
| `openrouter_v4_pro` | `pass__ch040-block-002` | known_pass | pass | pass | 100 | 5.951s | 0.0009165450000000001 | PASS: Translation is complete and accurate, with no omissions, additions, meaning drift, or Chinese leakage; names and glossary terms are consistent, tone matches the source, and n |
| `openrouter_v4_pro` | `pass__ch050-block-006` | known_pass | pass | pass | 100 | 6.164s | 0.00020097 | PASS: Accurate translation with no omissions, additions, or meaning drift; name and tone preserved. |
| `openrouter_v4_pro` | `historical__ch014-block-005__omission` | historical_recovery_derived | fail | fail | 100 | 4.788s | 0.00102051 | FAIL: missing final interjection "(妈耶！)" from source |
| `openrouter_v4_pro` | `historical__ch026-block-004__glossary` | historical_recovery_derived | fail | fail | 100 | 12.830s | 0.00134154 | FAIL: Chinese source says “船…船…船…” (boat) but Thai literal renders as “กัปตัน” (captain) — the character name is also misspelled as “ดันแคง” instead of “ดันแคน” per the refined ver |
| `openrouter_v4_pro` | `historical__ch029-block-005__chinese` | historical_recovery_derived | fail | unknown | 35 | 11.130s | 0.00134067 | None |
| `openrouter_v4_pro` | `historical__ch037-block-002__omission` | historical_recovery_derived | fail | fail | 100 | 13.922s | 0.0010339949999999998 | FAIL: missing the opening dialogue and description from the previously silent believer. |
| `openrouter_v4_pro` | `historical__ch044-block-001__addition` | historical_recovery_derived | fail | fail | 100 | 1.860s | 0.000834765 | FAIL: Added introductory phrase "ในปริสสันของปรานด์" not present in source; unsupported addition. |
| `openrouter_v4_pro` | `historical__ch013-block-001__glossary` | historical_recovery_derived | fail | unknown | 35 | 13.831s | 0.00119451 | None |
| `openrouter_v4_pro` | `historical__ch043-block-006__chinese` | historical_recovery_derived | fail | pass | 35 | 53.528s | 0.001393305 | PASS: Translation is faithful, no omissions or additions, proper glossary terms (e.g., 深海教会 → คริสตจักรแห่งทะเลลึก), no Chinese leakage, and tone matches source. |
| `openrouter_v4_pro` | `historical__ch017-block-003__addition` | historical_recovery_derived | fail | fail | 100 | 12.796s | 0.001133175 | FAIL: addition of "ในปริสสันของปรานด์" not present in source. |
| `openrouter_v4_pro` | `historical__ch019-block-005__omission` | historical_recovery_derived | fail | unknown | 35 | 15.690s | 0.001261935 | None |
| `openrouter_v4_pro` | `historical__ch041-block-002__meaning` | historical_recovery_derived | fail | unknown | 35 | 9.698s | 0.0009248100000000001 | None |
| `openrouter_v4_pro` | `adversarial__ch003-block-002__omission` | adversarial | fail | unknown | 35 | 12.901s | 0.00123975 | None |
| `openrouter_v4_pro` | `adversarial__ch005-block-004__addition` | adversarial | fail | unknown | 35 | 11.494s | 0.00123714 | None |
| `openrouter_v4_pro` | `adversarial__ch009-block-003__glossary` | adversarial | fail | unknown | 35 | 14.631s | 0.00125628 | None |
| `openrouter_v4_pro` | `adversarial__ch012-block-003__chinese` | adversarial | fail | unknown | 35 | 10.529s | 0.0011975549999999999 | None |
| `openrouter_v4_pro` | `adversarial__ch018-block-004__omission` | adversarial | fail | fail | 100 | 6.858s | 0.000864345 | FAIL: The Thai translation omits the entire incantation paragraph ("伪日终将坠落，真实的太阳神将自血与火中复活！万物生机归于太阳，万物秩序归于太阳！"), which is present in the Chinese source and required for completeness |
| `openrouter_v4_pro` | `adversarial__ch023-block-002__addition` | adversarial | fail | fail | 100 | 12.429s | 0.0008178 | FAIL: Added sentence "เขารู้สึกดีใจอย่างสุดซึ้งทั้งที่ไม่มีเหตุผลใดรองรับ" not present in source. |
| `openrouter_v4_pro` | `adversarial__ch028-block-004__glossary` | adversarial | fail | unknown | 35 | 13.576s | 0.00132588 | None |
| `openrouter_v4_pro` | `adversarial__ch032-block-006__omission` | adversarial | fail | fail | 100 | 5.835s | 0.00050895 | FAIL: translation truncated, missing the rest of the sentence after "นาม" |
| `openrouter_v4_pro` | `adversarial__ch038-block-005__perspective` | adversarial | fail | fail | 100 | 12.495s | 0.00107532 | FAIL: Unsupported addition of "เขาคิดว่า" at the start introduces a perspective shift not present in the source. |
| `openrouter_v4_pro` | `adversarial__ch045-block-003__meaning` | adversarial | fail | unknown | 35 | 6.070s | 0.001032255 | None |
| `openrouter_v4_flash` | `pass__ch001-block-001` | known_pass | pass | pass | 100 | 1.298s | 0.000201515 | PASS: The translation is complete, accurate, and maintains the original meaning, tone, and structure without omissions, additions, or errors. |
| `openrouter_v4_flash` | `pass__ch002-block-003` | known_pass | pass | pass | 100 | 2.759s | 0.00018844109999999997 | PASS: The translation is complete, accurate, and natural, with no omissions, additions, meaning drift, or Chinese leakage. Names and glossary terms are consistent, and the tone mat |
| `openrouter_v4_flash` | `pass__ch006-block-004` | known_pass | pass | unknown | 35 | 13.412s | 0.00028487339999999997 | None |
| `openrouter_v4_flash` | `pass__ch011-block-002` | known_pass | pass | pass | 100 | 18.570s | 0.0004074535 | PASS: Complete and accurate translation, no omissions or errors. |
| `openrouter_v4_flash` | `pass__ch016-block-005` | known_pass | pass | fail | 45 | 2.012s | 0.0001782179 | FAIL: Name inconsistency: "ดันแค้น" (refined) vs "ดันแคน" (source/literal). |
| `openrouter_v4_flash` | `pass__ch021-block-004` | known_pass | pass | pass | 100 | 4.706s | 0.00026747429999999996 | PASS: The translation is complete, accurate, and consistent in terminology, tone, and meaning with the Chinese source, with no omissions, additions, or errors. |
| `openrouter_v4_flash` | `pass__ch027-block-003` | known_pass | pass | pass | 100 | 2.894s | 0.0001803805 | PASS: The translation is complete and accurate, with no omissions, additions, meaning drift, Chinese leakage, or tone inconsistencies. Glossary and names are consistent, and all de |
| `openrouter_v4_flash` | `pass__ch033-block-005` | known_pass | pass | pass | 100 | 10.215s | 0.000132705 | PASS: The translation is accurate, complete, and natural in Thai, with no omissions, additions, meaning drift, or Chinese leakage. |
| `openrouter_v4_flash` | `pass__ch040-block-002` | known_pass | pass | pass | 100 | 2.378s | 0.0001996473 | PASS |
| `openrouter_v4_flash` | `pass__ch050-block-006` | known_pass | pass | pass | 100 | 1.097s | 2.39852e-05 | PASS: The translation is accurate, complete, and maintains the original meaning without omissions, additions, or errors. |
| `openrouter_v4_flash` | `historical__ch014-block-005__omission` | historical_recovery_derived | fail | fail | 100 | 2.149s | 0.00016357119999999998 | FAIL: Missing the line "(แม่เจ้า!)" at the end of the Chinese source, which is omitted in the Thai output. |
| `openrouter_v4_flash` | `historical__ch026-block-004__glossary` | historical_recovery_derived | fail | fail | 100 | 6.786s | 0.0002866428 | FAIL: 人名翻译不一致：第一次出现为“ดันแคง”，第二次为“ดันแคน”，应统一为“ดันแคน”。 |
| `openrouter_v4_flash` | `historical__ch029-block-005__chinese` | historical_recovery_derived | fail | fail | 100 | 7.541s | 0.000279172 | FAIL: Untranslated Chinese "亚空间" appears in the Thai body text. |
| `openrouter_v4_flash` | `historical__ch037-block-002__omission` | historical_recovery_derived | fail | fail | 100 | 2.763s | 0.0001894241 | FAIL: Missing the opening dialogue line from the Chinese source: “我认识他……他在下城区开着一家快关门的古董店，店里全都是假货那种，”旁边一个始终没怎么开口的教徒说话了，“他本来就有病，身体从来就没好过，大概是在下水道里待的时间过久，之前又受了惊吓，才导致病情恶化了吧。” This entir |
| `openrouter_v4_flash` | `historical__ch044-block-001__addition` | historical_recovery_derived | fail | unknown | 35 | 8.944s | 0.0002818261 | None |
| `openrouter_v4_flash` | `historical__ch013-block-001__glossary` | historical_recovery_derived | fail | pass | 35 | 8.873s | 0.00027543660000000004 | PASS: The translation is complete, accurate, maintains tone, and fixes minor Thai style issues without omissions or additions. |
| `openrouter_v4_flash` | `historical__ch043-block-006__chinese` | historical_recovery_derived | fail | fail | 80 | 8.630s | 0.0001445993 | FAIL: 末尾存在未翻译的中文“亚空间”。 |
| `openrouter_v4_flash` | `historical__ch017-block-003__addition` | historical_recovery_derived | fail | fail | 100 | 2.447s | 0.00022894069999999998 | FAIL: Refined translation adds "ในปริสสันของปรานด์" at the beginning, which is not present in the Chinese source, constituting an unsupported addition. |
| `openrouter_v4_flash` | `historical__ch019-block-005__omission` | historical_recovery_derived | fail | fail | 100 | 4.824s | 0.00022697469999999998 | FAIL: Unsupported addition in Thai refined: "ข้อความนี้ไม่มีในต้นฉบับ" is not present in Chinese source. |
| `openrouter_v4_flash` | `historical__ch041-block-002__meaning` | historical_recovery_derived | fail | fail | 100 | 4.368s | 0.00012169540000000001 | FAIL: The Thai refinement omits a significant portion of the original text, including details about Dunkan's past assumptions, his search for memory fragments, the reasons for his  |
| `openrouter_v4_flash` | `adversarial__ch003-block-002__omission` | adversarial | fail | unknown | 35 | 5.955s | 0.000280155 | None |
| `openrouter_v4_flash` | `adversarial__ch005-block-004__addition` | adversarial | fail | fail | 100 | 7.963s | 0.0002583324 | FAIL: Unsupported addition at the beginning: "หนังสือพิมพ์ยืนยันว่าเรื่องทั้งหมดเป็นข่าวปลอม" is not in the source. |
| `openrouter_v4_flash` | `adversarial__ch009-block-003__glossary` | adversarial | fail | pass | 35 | 2.767s | 0.0001987626 | PASS: The translation is accurate, complete, and maintains the original tone and meaning. Glossary terms like "กัปตันดันแคง" (Captain Duncan) and "เรือผู้ไร้บ้าน" (Ship of the Lost |
| `openrouter_v4_flash` | `adversarial__ch012-block-003__chinese` | adversarial | fail | unknown | 35 | 7.919s | 0.0002708165 | None |
| `openrouter_v4_flash` | `adversarial__ch018-block-004__omission` | adversarial | fail | fail | 100 | 3.583s | 0.0002082977 | FAIL: 泰文精修版遗漏了中文原文中的关键预言段落（“伪日终将坠落...”），属于严重缺失。 |
| `openrouter_v4_flash` | `adversarial__ch023-block-002__addition` | adversarial | fail | fail | 100 | 16.344s | 0.0003672488 | FAIL: 泰语版本末尾添加了中文原文没有的句子"他感到深深的喜悦，尽管没有任何理由支持"，属于不支持的添加。 |
| `openrouter_v4_flash` | `adversarial__ch028-block-004__glossary` | adversarial | fail | pass | 35 | 2.657s | 0.0002144906 | PASS: The translation is complete, accurate, and maintains the original meaning, tone, and detail without omissions, additions, or Chinese leakage. Glossary terms like "หัวแพะ" (go |
| `openrouter_v4_flash` | `adversarial__ch032-block-006__omission` | adversarial | fail | fail | 100 | 3.968s | 7.78536e-05 | FAIL: The refined translation cuts off mid-sentence, omitting the rest of the question about the goat head's claim. |
| `openrouter_v4_flash` | `adversarial__ch038-block-005__perspective` | adversarial | fail | pass | 35 | 4.521s | 0.0001979762 | PASS: The translation matches the source in content, perspective, and tone, with no omissions, additions, or meaning drift. |
| `openrouter_v4_flash` | `adversarial__ch045-block-003__meaning` | adversarial | fail | fail | 100 | 2.746s | 0.0001422401 | FAIL: The Thai translation adds an unsupported summary sentence "สรุปแล้วเหตุการณ์ทั้งหมดไม่ได้สำคัญนัก" that is not present in the Chinese source, constituting an addition error. |
| `qwen_cli` | `pass__ch001-block-001` | known_pass | pass | pass | 100 | 41.601s | n/a | PASS: The Thai translation is complete and accurate — no omissions, additions, meaning drift, or Chinese leakage. All names (周铭 → โจวหมิง), glossary terms (浇铸 → หล่อ), and tone (de |
| `qwen_cli` | `pass__ch002-block-003` | known_pass | pass | pass | 100 | 21.698s | n/a | PASS: All content preserved, no omissions/additions, names consistent (โจวหมิง/ดันแคน แอบโนมาร์), no Chinese leakage, tone matches source (internal monologue → goat head banter → i |
| `qwen_cli` | `pass__ch006-block-004` | known_pass | pass | pass | 90 | 26.322s | n/a | PASS: The Thai translation is complete and accurate — no omissions, additions, meaning drift, glossary/name errors, Chinese leakage, or tone issues. The refined version only adjust |
| `qwen_cli` | `pass__ch011-block-002` | known_pass | pass | pass | 100 | 26.228s | n/a | PASS: All content is faithfully translated with no omissions, additions, or meaning drift. Glossary terms (ดันแคน, ตุ๊กตา, กัปตันผี) are consistent, no Chinese leakage, and the ton |
| `qwen_cli` | `pass__ch016-block-005` | known_pass | pass | fail | 45 | 38.830s | n/a | FAIL: ชื่อตัวละครไม่สอดคล้อง — THAI_LITERAL ใช้ "ดันแคน" แต่ THAI_REFINED_TO_JUDGE ใช้ "ดันแค้น" ในย่อหน้าที่ 3 (บรรทัด "แรงดึงมหาศาลก็โถมเข้าใส่...") ซึ่งเป็นการสะกดที่ผิดเพี้ยนไป |
| `qwen_cli` | `pass__ch021-block-004` | known_pass | pass | pass | 100 | 19.618s | n/a | PASS: No omissions, additions, meaning drift, glossary/name inconsistency, Chinese leakage, or tone issues detected. The refined version reads naturally in Thai and faithfully conv |
| `qwen_cli` | `pass__ch027-block-003` | known_pass | pass | pass | 100 | 50.842s | n/a | PASS: No omissions, additions, meaning drift, glossary/name inconsistency, Chinese leakage, or tone issues detected. The refined version improves fluency (e.g. "ความเงียบ" vs "ความ |
| `qwen_cli` | `pass__ch033-block-005` | known_pass | pass | fail | 45 | 70.678s | n/a | FAIL: Untranslated Chinese character "摆" remains in the Thai body text of paragraph 3 (line: "พวกมันพ่นฟองอากาศออกมา摆ขยับหาง"). |
| `qwen_cli` | `pass__ch040-block-002` | known_pass | pass | pass | 100 | 34.513s | n/a | PASS: The translation is complete and accurate — no omissions, additions, meaning drift, or Chinese leakage. Glossary terms (วันนา, กอมอนา, อวกาศย่อย, ผู้ฟื้นคืน, คริสตจักรแห่งท้อง |
| `qwen_cli` | `pass__ch050-block-006` | known_pass | pass | pass | 100 | 58.197s | n/a | PASS: Complete and accurate translation with no omissions, additions, or errors. |
| `qwen_cli` | `historical__ch014-block-005__omission` | historical_recovery_derived | fail | fail | 100 | 63.312s | n/a | FAIL: Missing the final paragraph — Duncan's explanation about Alice's secrets, the "cursed doll" title, and the "Harmless on the Lost Home only" caveat are entirely omitted from t |
| `qwen_cli` | `historical__ch026-block-004__glossary` | historical_recovery_derived | fail | fail | 100 | 67.445s | n/a | FAIL: Name inconsistency — "ดันแคน" in THAI_LITERAL vs "ดันแคง" in THAI_REFINED_TO_JUDGE (Duncan's name uses different final consonant). Also "กะ... กะ... กัปตัน..." in literal was |
| `qwen_cli` | `historical__ch029-block-005__chinese` | historical_recovery_derived | fail | fail | 100 | 63.586s | n/a | FAIL: Chinese leakage — "亚空间" appears untranslated in the Thai body text at the end. |
| `qwen_cli` | `historical__ch037-block-002__omission` | historical_recovery_derived | fail | fail | 100 | 51.339s | n/a | FAIL: Missing the opening dialogue block — the Chinese source begins with a speaking line from a believer ("我认识他……他在下城区开着一家快关门的古董店...") which is entirely absent from THAI_LITERAL a |
| `qwen_cli` | `historical__ch044-block-001__addition` | historical_recovery_derived | fail | fail | 100 | 71.909s | n/a | FAIL: THAI_REFINED_TO_JUDGE opens with "ในปริสสันของปรานด์" which is an unsupported addition — no equivalent exists in the CHINESE_SOURCE. The source begins directly with "一份普兰德消息报 |
| `qwen_cli` | `historical__ch013-block-001__glossary` | historical_recovery_derived | fail | fail | 100 | 72.759s | n/a | FAIL: Missing sentence — the THAI_REFINED_TO_JUDGE omits the entire paragraph starting with "ดันแคนมองไปที่..." (Duncan's meaningful glance and Alice's calm response) that appears  |
| `qwen_cli` | `historical__ch043-block-006__chinese` | historical_recovery_derived | fail | fail | 100 | 42.660s | n/a | FAIL: **亚空间** (Chinese leakage) appears untranslated in the Thai body text at the end. |
| `qwen_cli` | `historical__ch017-block-003__addition` | historical_recovery_derived | fail | fail | 100 | 44.614s | n/a | FAIL: The refined version adds "ในปริสสันของปรานด์" (In the prison of Prand) at the very beginning, which is an unsupported addition not present in the Chinese source or the litera |
| `qwen_cli` | `historical__ch019-block-005__omission` | historical_recovery_derived | fail | fail | 100 | 80.157s | n/a | FAIL: The THAI_REFINED_TO_JUDGE appends the extra line "ข้อความนี้ไม่มีในต้นฉบับ" which is an unsupported addition not present in the CHINESE_SOURCE. |
| `qwen_cli` | `historical__ch041-block-002__meaning` | historical_recovery_derived | fail | fail | 100 | 103.569s | n/a | FAIL: THAI_REFINED_TO_JUDGE omits the entire second half of the source (from "巨大的违和感充斥着邓肯的内心" onward — ~5 sentences covering Duncan's memory search, the two hypotheses, and the lig |
| `qwen_cli` | `adversarial__ch003-block-002__omission` | adversarial | fail | fail | 100 | 49.699s | n/a | FAIL: The THAI_REFINED_TO_JUDGE omits the final paragraph of the Chinese source — the passage about Duncan wondering whether this world has no normal weather and whether the overca |
| `qwen_cli` | `adversarial__ch005-block-004__addition` | adversarial | fail | fail | 100 | 79.854s | n/a | FAIL: THAI_REFINED_TO_JUDGE opens with an unsupported addition ("หนังสือพิมพ์ยืนยันว่าเรื่องทั้งหมดเป็นข่าวปลอม") that has no basis in the CHINESE_SOURCE. |
| `qwen_cli` | `adversarial__ch009-block-003__glossary` | adversarial | fail | fail | 100 | 124.406s | n/a | FAIL: Name inconsistency — "ดันแคน" in THAI_LITERAL vs "ดันแคง" in THAI_REFINED_TO_JUDGE for the same character "邓肯". The glossary-standard rendering should be consistent across bo |
| `qwen_cli` | `adversarial__ch012-block-003__chinese` | adversarial | fail | fail | 100 | 66.945s | n/a | FAIL: Thai body text contains untranslated Chinese "灵界边缘" at the end, which is a Chinese leakage. |
| `qwen_cli` | `adversarial__ch018-block-004__omission` | adversarial | fail | fail | 100 | 37.283s | n/a | FAIL: The refined version omits the entire cult chant line — "ดวงตะวันจอมปลอมจักต้องร่วงหล่น สุริยเทพที่แท้จริงจักฟื้นคืนชีพจากโลหิตและเปลวเพลิง! พลังชีวิตของสรรพสิ่งขึ้นตรงต่อดวงต |
| `qwen_cli` | `adversarial__ch023-block-002__addition` | adversarial | fail | fail | 100 | 69.190s | n/a | FAIL: The refined version adds a final sentence "เขารู้สึกดีใจอย่างสุดซึ้งทั้งที่ไม่มีเหตุผลใดรองรับ" ("He felt deeply joyful for no reason at all") that does not exist in the Chin |
| `qwen_cli` | `adversarial__ch028-block-004__glossary` | adversarial | fail | unknown | 20 | 52.418s | n/a |  |
| `qwen_cli` | `adversarial__ch032-block-006__omission` | adversarial | fail | unknown | 20 | 79.333s | n/a |  |
| `qwen_cli` | `adversarial__ch038-block-005__perspective` | adversarial | fail | unknown | 20 | 134.201s | n/a |  |
| `qwen_cli` | `adversarial__ch045-block-003__meaning` | adversarial | fail | fail | 100 | 96.561s | n/a | FAIL: The refined version replaces the entire dialogue (Nina's reply, Duncan's question, their argument, and Duncan's correction) with a single summary sentence "สรุปแล้วเหตุการณ์ท |

## Fixture Notes

- Historical-recovery-derived cases use blocks that had historical failed or hard-fail records, then inject one controlled failure when the original bad artifact was not preserved.
- Adversarial cases use current clean artifacts and inject one controlled QA defect.
- The report should be used for QA routing decisions only; it does not evaluate literal translation, refinement, glossary scan, or formatting.

## Safety

- No API key or bearer token is written to artifacts or this report.
- No production ledger, glossary notes, source files, chapter work artifacts, final outputs, or provider config are modified by the benchmark.
