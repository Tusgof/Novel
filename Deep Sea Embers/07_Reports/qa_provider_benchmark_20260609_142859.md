# QA Provider Cost/Quality Benchmark - qa_provider_benchmark_20260609_142859

Generated: 2026-06-10T00:48:42

## Scope

- Non-production QA-only comparison.
- Production routing was not changed.
- Compared candidates: `openrouter_v4_pro`, `openrouter_v4_flash`, `openrouter_v4_flash_reasoning`, `qwen_cli`.
- Cases: 30 total: 10 known-pass, 10 historical-recovery-derived fail cases, 10 adversarial fail cases.

## Summary

| Candidate | Provider | Model | Request options | Calls | Avg score | False negatives | Severe false negatives | False positives | Parse failures | Provider failures | Avg latency | Est. cost | Est. cost / 100 blocks |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `openrouter_v4_pro` | openrouter | `deepseek/deepseek-v4-pro` | `{}` | 30 | 57.83 | 2 | 2 | 0 | 17 | 2 | 20.254s | 0.03668051 | 0.122268 |
| `openrouter_v4_flash` | openrouter | `deepseek/deepseek-v4-flash` | `{}` | 30 | 75.17 | 5 | 5 | 1 | 5 | 0 | 10.242s | 0.00783422 | 0.026114 |
| `openrouter_v4_flash_reasoning` | openrouter | `deepseek/deepseek-v4-flash` | `{"reasoning":{"enabled":true,"exclude":true}}` | 30 | 66.17 | 0 | 0 | 0 | 15 | 0 | 9.527s | 0.00802472 | 0.026749 |
| `qwen_cli` | qwen | `deepseek-reasoner` | `{}` | 30 | 95.83 | 0 | 0 | 2 | 0 | 1 | 41.776s | n/a | n/a |

## Recommendation

Do not promote deepseek/deepseek-v4-flash with reasoning enabled to QA primary yet. It produced zero severe false negatives in this fixture set, but its structured-output reliability is not acceptable (15 parse failures); keep production QA routing unchanged for now.

## Per-Case Results

| Candidate | Case | Group | Expected | Predicted | Score | Latency | Cost | First line |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |
| `openrouter_v4_pro` | `pass__ch001-block-001` | known_pass | pass | unknown | 35 | 17.039s | 0.00130152 | None |
| `openrouter_v4_pro` | `pass__ch003-block-003` | known_pass | pass | unknown | 35 | 9.524s | 0.00133545 | None |
| `openrouter_v4_pro` | `pass__ch005-block-001` | known_pass | pass | unknown | 35 | 23.548s | 0.00129195 | None |
| `openrouter_v4_pro` | `pass__ch008-block-003` | known_pass | pass | pass | 100 | 147.775s | 0.0037671 | PASS: Translation is faithful, all sentences present, no meaning drift, glossary consistent, no Chinese leakage. |
| `openrouter_v4_pro` | `pass__ch011-block-002` | known_pass | pass | pass | 100 | 16.469s | 0.00042891 | PASS: All sentences are present, no unsupported additions, names and terms are consistent, no Chinese leakage, tone matches the eerie narrative. |
| `openrouter_v4_pro` | `pass__ch016-block-001` | known_pass | pass | unknown | 35 | 16.895s | 0.0012984749999999999 | None |
| `openrouter_v4_pro` | `pass__ch021-block-001` | known_pass | pass | unknown | 20 | 17.097s | 0.0 |  |
| `openrouter_v4_pro` | `pass__ch023-block-004` | known_pass | pass | unknown | 35 | 15.513s | 0.0012884700000000001 | None |
| `openrouter_v4_pro` | `pass__ch034-block-002` | known_pass | pass | pass | 100 | 11.830s | 0.0008821799999999999 | PASS: Translation is accurate, no omissions, no additions, no Chinese leakage, names consistent, tone matches source. |
| `openrouter_v4_pro` | `pass__ch042-block-002` | known_pass | pass | pass | 100 | 88.093s | 0.0033669 | PASS: Accurate translation with no critical issues; minor wording choice does not cause meaning drift. |
| `openrouter_v4_pro` | `historical__ch014-block-005__omission` | historical_recovery_derived | fail | unknown | 35 | 12.280s | 0.00113448 | None |
| `openrouter_v4_pro` | `historical__ch026-block-004__glossary` | historical_recovery_derived | fail | fail | 100 | 3.685s | 0.0009134999999999999 | FAIL: Name inconsistency: Chinese source uses “邓肯” which should be transliterated as “เติ้งเคิ่น” or “ตุนเคิ่น” per glossary, but THAI_REFINED_TO_JUDGE uses “ดันแคง” (and THAI_LITE |
| `openrouter_v4_pro` | `historical__ch029-block-005__chinese` | historical_recovery_derived | fail | unknown | 35 | 9.393s | 0.00134067 | None |
| `openrouter_v4_pro` | `historical__ch037-block-002__omission` | historical_recovery_derived | fail | unknown | 35 | 7.469s | 0.0011966849999999998 | None |
| `openrouter_v4_pro` | `historical__ch044-block-001__addition` | historical_recovery_derived | fail | pass | 35 | 14.334s | 0.0012532350000000001 | PASS |
| `openrouter_v4_pro` | `historical__ch013-block-001__glossary` | historical_recovery_derived | fail | unknown | 35 | 27.563s | 0.00119364 | None |
| `openrouter_v4_pro` | `historical__ch043-block-006__chinese` | historical_recovery_derived | fail | pass | 35 | 21.890s | 0.001502055 | PASS: All content accurately translated, no omissions, additions, or errors. |
| `openrouter_v4_pro` | `historical__ch017-block-003__addition` | historical_recovery_derived | fail | fail | 100 | 8.120s | 0.0010940249999999998 | FAIL: Addition of "ในปริสสันของปรานด์" not in source |
| `openrouter_v4_pro` | `historical__ch019-block-005__omission` | historical_recovery_derived | fail | unknown | 35 | 15.538s | 0.001262805 | None |
| `openrouter_v4_pro` | `historical__ch041-block-002__meaning` | historical_recovery_derived | fail | fail | 100 | 14.537s | 0.00130587 | FAIL: Missing entire paragraphs from the source; only first few sentences translated, then an unsupported summary sentence added. |
| `openrouter_v4_pro` | `adversarial__ch003-block-002__omission` | adversarial | fail | unknown | 35 | 12.110s | 0.00123975 | None |
| `openrouter_v4_pro` | `adversarial__ch005-block-004__addition` | adversarial | fail | unknown | 35 | 14.916s | 0.00123714 | None |
| `openrouter_v4_pro` | `adversarial__ch009-block-003__glossary` | adversarial | fail | fail | 100 | 13.414s | 0.00128151 | FAIL: Name "ดันแคน" inconsistent with Thai refined "ดันแคง" (glossary mismatch). |
| `openrouter_v4_pro` | `adversarial__ch012-block-003__chinese` | adversarial | fail | fail | 100 | 3.066s | 0.000783435 | FAIL: Final line “灵界边缘” is untranslated Chinese lingering at the end of the Thai output. |
| `openrouter_v4_pro` | `adversarial__ch018-block-004__omission` | adversarial | fail | unknown | 35 | 14.795s | 0.001251495 | None |
| `openrouter_v4_pro` | `adversarial__ch023-block-002__addition` | adversarial | fail | fail | 100 | 1.925s | 0.0008178 | FAIL: Added sentence "เขารู้สึกดีใจอย่างสุดซึ้งทั้งที่ไม่มีเหตุผลใดรองรับ" not present in source. |
| `openrouter_v4_pro` | `adversarial__ch028-block-004__glossary` | adversarial | fail | unknown | 35 | 12.171s | 0.00132588 | None |
| `openrouter_v4_pro` | `adversarial__ch032-block-006__omission` | adversarial | fail | fail | 100 | 9.741s | 0.0005533199999999999 | FAIL: translation truncated, missing the latter half of the sentence (the alternative about the |
| `openrouter_v4_pro` | `adversarial__ch038-block-005__perspective` | adversarial | fail | unknown | 20 | 19.114s | 0.0 |  |
| `openrouter_v4_pro` | `adversarial__ch045-block-003__meaning` | adversarial | fail | unknown | 35 | 7.781s | 0.001032255 | None |
| `openrouter_v4_flash` | `pass__ch001-block-001` | known_pass | pass | unknown | 35 | 11.469s | 0.0002941136 | None |
| `openrouter_v4_flash` | `pass__ch003-block-003` | known_pass | pass | pass | 100 | 4.020s | 0.00021016539999999998 | PASS: Translation is accurate, complete, and consistent with Chinese source. No omissions, additions, meaning drift, glossary errors, Chinese leakage, or tone issues. |
| `openrouter_v4_flash` | `pass__ch005-block-001` | known_pass | pass | pass | 100 | 35.294s | 0.0006080838 | PASS: Translation is accurate, complete, and consistent; no omissions, additions, meaning drift, name inconsistency, Chinese leakage, or tone issues. |
| `openrouter_v4_flash` | `pass__ch008-block-003` | known_pass | pass | pass | 100 | 6.175s | 0.00021055859999999997 | PASS: Translation is faithful, complete, and consistent; no omissions, additions, or meaning drift. |
| `openrouter_v4_flash` | `pass__ch011-block-002` | known_pass | pass | pass | 100 | 16.552s | 9.6334e-05 | PASS: The translation is complete, accurate, and natural, with no omissions, additions, meaning drift, or Chinese leakage. |
| `openrouter_v4_flash` | `pass__ch016-block-001` | known_pass | pass | pass | 100 | 1.653s | 0.0002002371 | PASS: The translation is complete, accurate, and natural, with no omissions, additions, meaning drift, or Chinese leakage. |
| `openrouter_v4_flash` | `pass__ch021-block-001` | known_pass | pass | unknown | 35 | 6.159s | 0.0002723893 | None |
| `openrouter_v4_flash` | `pass__ch023-block-004` | known_pass | pass | unknown | 35 | 9.709s | 0.0002911646 | None |
| `openrouter_v4_flash` | `pass__ch034-block-002` | known_pass | pass | pass | 100 | 3.002s | 0.0002119348 | PASS: Translation is complete, accurate, and maintains the original meaning, tone, and details without omissions, additions, or errors. |
| `openrouter_v4_flash` | `pass__ch042-block-002` | known_pass | pass | fail | 45 | 35.090s | 0.0005898 | FAIL: Unsupported addition of "กว่าที่คิด" in the first sentence (not in source). |
| `openrouter_v4_flash` | `historical__ch014-block-005__omission` | historical_recovery_derived | fail | fail | 100 | 10.628s | 0.000163178 | FAIL: Missing the final line "(妈耶！)" which is present in the Chinese source but omitted in the Thai translation. |
| `openrouter_v4_flash` | `historical__ch026-block-004__glossary` | historical_recovery_derived | fail | pass | 35 | 4.608s | 0.0002109518 | PASS: The translation is accurate, consistent with the source, and uses appropriate Thai. Notable corrections from the literal version include fixing the stuttering speech from “กะ |
| `openrouter_v4_flash` | `historical__ch029-block-005__chinese` | historical_recovery_derived | fail | fail | 100 | 3.191s | 0.0002089858 | FAIL: Glossary term "亚空间" is left untranslated as Chinese in the Thai body text. |
| `openrouter_v4_flash` | `historical__ch037-block-002__omission` | historical_recovery_derived | fail | fail | 100 | 6.551s | 0.0001856887 | FAIL: The first sentence of the Chinese source ("我认识他……他在下城区开着一家快关门的古董店，店里全都是假货那种") is missing from the Thai literal translation, which starts directly with "เมื่อได้ฟังคำอธิบายจาก |
| `openrouter_v4_flash` | `historical__ch044-block-001__addition` | historical_recovery_derived | fail | fail | 100 | 38.074s | 0.0007447208 | FAIL: Unsupported addition in first sentence: "ในปริสสันของปรานด์" does not appear in the Chinese source. |
| `openrouter_v4_flash` | `historical__ch013-block-001__glossary` | historical_recovery_derived | fail | fail | 100 | 23.143s | 0.0005577542 | FAIL: ชื่อตัวละคร "ดันแคง" ในย่อหน้าแรกไม่สอดคล้องกับ "ดันแคน" ในย่อหน้าถัดไป |
| `openrouter_v4_flash` | `historical__ch043-block-006__chinese` | historical_recovery_derived | fail | fail | 80 | 5.422s | 9.21071e-05 | FAIL: 精炼翻译末尾出现未翻译的中文“亚空间”，属于中文泄漏。 |
| `openrouter_v4_flash` | `historical__ch017-block-003__addition` | historical_recovery_derived | fail | fail | 100 | 2.999s | 0.0001815601 | FAIL: Addition of "ในปริสสันของปรานด์" not present in Chinese source. |
| `openrouter_v4_flash` | `historical__ch019-block-005__omission` | historical_recovery_derived | fail | fail | 100 | 1.864s | 0.0001957153 | FAIL: The Thai translation contains an extra sentence "ข้อความนี้ไม่มีในต้นฉบับ" (This text is not in the original) that is not present in the Chinese source, constituting an unsup |
| `openrouter_v4_flash` | `historical__ch041-block-002__meaning` | historical_recovery_derived | fail | fail | 100 | 1.686s | 0.0001187464 | FAIL: The Thai translation omits the entire second paragraph of the Chinese source, which details the character's reasoning about technology, memory, and knowledge gaps, resulting  |
| `openrouter_v4_flash` | `adversarial__ch003-block-002__omission` | adversarial | fail | pass | 35 | 1.229s | 0.000188736 | PASS: The translation is complete and accurate, with no omissions, additions, or meaning drift. All names and terms are consistent, and the tone matches the original. |
| `openrouter_v4_flash` | `adversarial__ch005-block-004__addition` | adversarial | fail | fail | 100 | 10.045s | 0.0002461432 | FAIL: Unsupported addition at the beginning: "หนังสือพิมพ์ยืนยันว่าเรื่องทั้งหมดเป็นข่าวปลอม" is not present in the Chinese source. |
| `openrouter_v4_flash` | `adversarial__ch009-block-003__glossary` | adversarial | fail | pass | 35 | 4.595s | 0.0001973864 | PASS: The translation is accurate, complete, and maintains the original meaning, tone, and details. Glossary terms like "กัปตันดันแคง" and "เรือผู้ไร้บ้าน" are consistent, and ther |
| `openrouter_v4_flash` | `adversarial__ch012-block-003__chinese` | adversarial | fail | pass | 35 | 1.169s | 0.0001797907 | PASS: The translation is accurate, complete, and maintains the original tone and meaning. No omissions, additions, meaning drift, glossary inconsistency, Chinese leakage, or tone i |
| `openrouter_v4_flash` | `adversarial__ch018-block-004__omission` | adversarial | fail | fail | 100 | 11.345s | 0.0002816295 | FAIL: 漏译了关键涂鸦文字内容 "伪日终将坠落..." 整段，导致重要信息缺失。 |
| `openrouter_v4_flash` | `adversarial__ch023-block-002__addition` | adversarial | fail | fail | 80 | 13.073s | 0.00027700939999999996 | FAIL: 翻译在最后增加了原文没有的“他感到非常高兴， |
| `openrouter_v4_flash` | `adversarial__ch028-block-004__glossary` | adversarial | fail | pass | 35 | 3.500s | 0.0002072164 | PASS: The translation is complete, accurate, and maintains the original meaning, tone, and detail without omissions, additions, or Chinese leakage. |
| `openrouter_v4_flash` | `adversarial__ch032-block-006__omission` | adversarial | fail | fail | 100 | 7.252s | 8.78802e-05 | FAIL: The refined translation is incomplete, omitting the second half of the sentence and the name "周铭". |
| `openrouter_v4_flash` | `adversarial__ch038-block-005__perspective` | adversarial | fail | unknown | 35 | 5.832s | 0.000290968 | None |
| `openrouter_v4_flash` | `adversarial__ch045-block-003__meaning` | adversarial | fail | unknown | 35 | 21.919s | 0.0002332659 | None |
| `openrouter_v4_flash_reasoning` | `pass__ch001-block-001` | known_pass | pass | pass | 100 | 25.415s | 0.0006802360000000001 | PASS: Translation is complete, accurate, and consistent with the source; no omissions, additions, meaning drift, or Chinese leakage. |
| `openrouter_v4_flash_reasoning` | `pass__ch003-block-003` | known_pass | pass | pass | 100 | 4.494s | 0.0002382792 | PASS: The translation is complete and accurate, with no omissions, additions, meaning drift, or Chinese leakage. Names and glossary terms are consistent, and the tone matches the o |
| `openrouter_v4_flash_reasoning` | `pass__ch005-block-001` | known_pass | pass | pass | 100 | 20.236s | 0.0002736672 | PASS: The translation is faithful, complete, and consistent; all names and glossary terms are correctly rendered, no omissions, additions, or Chinese leakage detected. |
| `openrouter_v4_flash_reasoning` | `pass__ch008-block-003` | known_pass | pass | unknown | 35 | 10.355s | 0.00027111139999999996 | None |
| `openrouter_v4_flash_reasoning` | `pass__ch011-block-002` | known_pass | pass | unknown | 35 | 6.481s | 0.0001893258 | None |
| `openrouter_v4_flash_reasoning` | `pass__ch016-block-001` | known_pass | pass | pass | 100 | 3.549s | 0.0002128195 | PASS: The translation matches the source in content, tone, and detail with no omissions, additions, or errors. |
| `openrouter_v4_flash_reasoning` | `pass__ch021-block-001` | known_pass | pass | unknown | 35 | 7.753s | 0.0002723893 | None |
| `openrouter_v4_flash_reasoning` | `pass__ch023-block-004` | known_pass | pass | pass | 100 | 3.646s | 0.00022530359999999998 | PASS: The Thai translation accurately conveys all content from the Chinese source without omissions, additions, meaning drift, or Chinese leakage, and maintains consistent names an |
| `openrouter_v4_flash_reasoning` | `pass__ch034-block-002` | known_pass | pass | unknown | 35 | 7.791s | 0.0002927374 | None |
| `openrouter_v4_flash_reasoning` | `pass__ch042-block-002` | known_pass | pass | unknown | 35 | 6.080s | 0.0002718978 | None |
| `openrouter_v4_flash_reasoning` | `historical__ch014-block-005__omission` | historical_recovery_derived | fail | fail | 100 | 2.667s | 0.00018696659999999999 | FAIL: Missing the exclamation "(妈耶！)" at the end of the paragraph. |
| `openrouter_v4_flash_reasoning` | `historical__ch026-block-004__glossary` | historical_recovery_derived | fail | fail | 100 | 31.928s | 0.0004893374 | FAIL: Name 'ดันแคง' in refined does not match common transliteration 'ดันแคน' for character '邓肯' (Duncan), causing glossary inconsistency. |
| `openrouter_v4_flash_reasoning` | `historical__ch029-block-005__chinese` | historical_recovery_derived | fail | unknown | 35 | 6.156s | 0.0003029606 | None |
| `openrouter_v4_flash_reasoning` | `historical__ch037-block-002__omission` | historical_recovery_derived | fail | unknown | 35 | 20.271s | 0.0002704233 | None |
| `openrouter_v4_flash_reasoning` | `historical__ch044-block-001__addition` | historical_recovery_derived | fail | unknown | 35 | 6.730s | 0.0002818261 | None |
| `openrouter_v4_flash_reasoning` | `historical__ch013-block-001__glossary` | historical_recovery_derived | fail | unknown | 35 | 8.110s | 0.0002697352 | None |
| `openrouter_v4_flash_reasoning` | `historical__ch043-block-006__chinese` | historical_recovery_derived | fail | fail | 80 | 4.530s | 0.0001149127 | FAIL: 泰文精炼版末尾出现未翻译的中文“亚空间”，属于中文泄漏。 |
| `openrouter_v4_flash_reasoning` | `historical__ch017-block-003__addition` | historical_recovery_derived | fail | unknown | 35 | 16.131s | 0.0002755349 | None |
| `openrouter_v4_flash_reasoning` | `historical__ch019-block-005__omission` | historical_recovery_derived | fail | unknown | 35 | 5.145s | 0.00028516829999999997 | None |
| `openrouter_v4_flash_reasoning` | `historical__ch041-block-002__meaning` | historical_recovery_derived | fail | fail | 100 | 5.380s | 0.000207413 | FAIL: 遗漏了大部分内容（记忆碎片、城市规划、扭亮电灯等细节），并添加了原文不存在的总结句“สรุปแล้วเหตุการณ์ทั้งหมดไม่ได้สำคัญนัก”，改变了原意。 |
| `openrouter_v4_flash_reasoning` | `adversarial__ch003-block-002__omission` | adversarial | fail | unknown | 35 | 25.019s | 0.000280155 | None |
| `openrouter_v4_flash_reasoning` | `adversarial__ch005-block-004__addition` | adversarial | fail | fail | 100 | 7.436s | 0.0002652134 | FAIL: Added unsupported sentence "หนังสือพิมพ์ยืนยันว่าเรื่องทั้งหมดเป็นข่าวปลอม" at the beginning, not present in Chinese source. |
| `openrouter_v4_flash_reasoning` | `adversarial__ch009-block-003__glossary` | adversarial | fail | unknown | 35 | 5.310s | 0.0002838904 | None |
| `openrouter_v4_flash_reasoning` | `adversarial__ch012-block-003__chinese` | adversarial | fail | unknown | 35 | 7.736s | 0.0002706199 | None |
| `openrouter_v4_flash_reasoning` | `adversarial__ch018-block-004__omission` | adversarial | fail | fail | 100 | 2.641s | 0.0002169481 | FAIL: Missing the quoted text "伪日终将坠落，真实的太阳神将自血与火中复活！万物生机归于太阳，万物秩序归于太阳！" in the Thai refined version. |
| `openrouter_v4_flash_reasoning` | `adversarial__ch023-block-002__addition` | adversarial | fail | fail | 100 | 11.714s | 0.0002698335 | FAIL: The Thai translation contains an unsupported addition: the final sentence "เขารู้สึกดีใจอย่างสุดซึ้งทั้งที่ไม่มีเหตุผลใดรองรับ" (He felt deeply happy without any reason) is n |
| `openrouter_v4_flash_reasoning` | `adversarial__ch028-block-004__glossary` | adversarial | fail | unknown | 35 | 5.527s | 0.000299815 | None |
| `openrouter_v4_flash_reasoning` | `adversarial__ch032-block-006__omission` | adversarial | fail | fail | 80 | 4.650s | 8.27686e-05 | FAIL: 句子不完整，遗漏了关键信息和后半部分内容。 |
| `openrouter_v4_flash_reasoning` | `adversarial__ch038-block-005__perspective` | adversarial | fail | fail | 100 | 9.270s | 0.000281138 | FAIL: adds "เขาคิดว่า" which introduces a perspective not present in source, causing meaning drift. |
| `openrouter_v4_flash_reasoning` | `adversarial__ch045-block-003__meaning` | adversarial | fail | fail | 100 | 3.655s | 0.0001622933 | FAIL: Unsupported addition of "สรุปแล้วเหตุการณ์ทั้งหมดไม่ได้สำคัญนัก" which is not present in the Chinese source. |
| `qwen_cli` | `pass__ch001-block-001` | known_pass | pass | pass | 100 | 42.138s | n/a | PASS: The Thai translation is complete, accurate, and idiomatic — no omissions, additions, meaning drift, glossary/name errors, Chinese leakage, or tone issues. All paragraphs, dia |
| `qwen_cli` | `pass__ch003-block-003` | known_pass | pass | pass | 100 | 106.986s | n/a | PASS: All content preserved, no omissions or additions, glossary terms consistent ("ดันแคน", "เรือผู้ไร้บ้าน", "พังงาเรือ"), no Chinese leakage, tone matches source, and meaning dr |
| `qwen_cli` | `pass__ch005-block-001` | known_pass | pass | pass | 85 | 234.136s | n/a | PASS: All content faithfully translated with no omissions, additions, or meaning drift. Names (กอมอนา, บาต็อก, ลอว์เรนซ์, โอ๊กขาว) are consistent. No Chinese leakage. Tone matches  |
| `qwen_cli` | `pass__ch008-block-003` | known_pass | pass | fail | 45 | 54.115s | n/a | FAIL: Missing sentence: "这当然不是因为“这人偶很漂亮”这样简单的理由" — the refined version drops the phrase "这当然不是因为" (this is certainly not because), which weakens the emphatic negation present in th |
| `qwen_cli` | `pass__ch011-block-002` | known_pass | pass | pass | 100 | 23.850s | n/a | PASS: All content is faithfully translated with no omissions, additions, or meaning drift. Glossary terms (ดันแคน, ตุ๊กตา, กัปตันผี) are consistent, no Chinese leakage, and the ton |
| `qwen_cli` | `pass__ch016-block-001` | known_pass | pass | pass | 100 | 32.116s | n/a | PASS: Complete and faithful translation — no omissions, additions, meaning drift, or Chinese leakage. All names (ดันแคน, เรือผู้ไร้บ้าน, หัวแพะ) and glossary terms (พังงา, ต้นเรือ, |
| `qwen_cli` | `pass__ch021-block-001` | known_pass | pass | pass | 100 | 29.773s | n/a | PASS: No omissions, additions, meaning drift, glossary/name inconsistency, Chinese leakage, or tone issues detected. The only change from literal to refined is "นักบวชสวมหน้ากาก" → |
| `qwen_cli` | `pass__ch023-block-004` | known_pass | pass | pass | 100 | 31.742s | n/a | PASS: No omissions, additions, meaning drift, glossary/name inconsistency, Chinese leakage, or tone issues. The refined version improves fluency (e.g., "ภายใต้กฎเหล่านี้", "ผู้กำหน |
| `qwen_cli` | `pass__ch034-block-002` | known_pass | pass | fail | 45 | 41.507s | n/a | FAIL: Missing sentence — "钓鱼佬的热情在胸膛中熊熊燃烧" (the passion of the angler burned fiercely in his chest) is omitted from the first paragraph of the Thai refined version. The literal has  |
| `qwen_cli` | `pass__ch042-block-002` | known_pass | pass | pass | 100 | 35.816s | n/a | PASS: No omissions, additions, or meaning drift. Glossary/name consistency maintained (ดันแคน). No Chinese leakage. Tone and register consistent. The only change from literal is mi |
| `qwen_cli` | `historical__ch014-block-005__omission` | historical_recovery_derived | fail | fail | 100 | 33.850s | n/a | FAIL: Missing the final paragraph — Duncan's explanation about Alice's secrets, "สิ่งผิดปกติ 099", and the "ไร้บ้าน" line are entirely omitted from the refined version. |
| `qwen_cli` | `historical__ch026-block-004__glossary` | historical_recovery_derived | fail | fail | 100 | 29.578s | n/a | FAIL: Name inconsistency — "ดันแคน" in THAI_REFINED_TO_JUDGE vs "ดันแคนต์" (Duncan) in glossary/established convention; also "เรือ... เรือ... เรือ..." corrects the literal's "กะ... |
| `qwen_cli` | `historical__ch029-block-005__chinese` | historical_recovery_derived | fail | fail | 100 | 17.408s | n/a | FAIL: Chinese leakage — "亚空间" appears untranslated in the Thai body text at the end of the THAI_REFINED_TO_JUDGE output. |
| `qwen_cli` | `historical__ch037-block-002__omission` | historical_recovery_derived | fail | fail | 100 | 30.900s | n/a | FAIL: Missing the opening dialogue block — the Chinese source begins with a speaking line from a nearby cultist ("我认识他……他在下城区开着一家快关门的古董店...") which is entirely absent from THAI_REF |
| `qwen_cli` | `historical__ch044-block-001__addition` | historical_recovery_derived | fail | fail | 100 | 30.758s | n/a | FAIL: THAI_REFINED_TO_JUDGE opens with "ในปริสสันของปรานด์" which is an unsupported addition — no equivalent exists in the CHINESE_SOURCE. The source begins directly with "一份普兰德消息报 |
| `qwen_cli` | `historical__ch013-block-001__glossary` | historical_recovery_derived | fail | fail | 100 | 37.375s | n/a | FAIL: Missing sentence — "这不禁让他对某些更加遥远的事物产生了好奇" (This made him curious about even more distant things) is absent from the literal translation, creating a gap in the causal chain be |
| `qwen_cli` | `historical__ch043-block-006__chinese` | historical_recovery_derived | fail | fail | 100 | 27.298s | n/a | FAIL: **亚空间** (Chinese leakage) appears untranslated in the Thai body text at the end. |
| `qwen_cli` | `historical__ch017-block-003__addition` | historical_recovery_derived | fail | fail | 100 | 37.489s | n/a | FAIL: The refined version adds "ในปริสสันของปรานด์" (In the prison of Prand) at the very beginning, which is an unsupported addition not present in the Chinese source or the litera |
| `qwen_cli` | `historical__ch019-block-005__omission` | historical_recovery_derived | fail | fail | 100 | 18.718s | n/a | FAIL: The THAI_REFINED_TO_JUDGE appends an extra sentence "ข้อความนี้ไม่มีในต้นฉบับ" that does not exist in the Chinese source, constituting an unsupported addition. |
| `qwen_cli` | `historical__ch041-block-002__meaning` | historical_recovery_derived | fail | fail | 100 | 37.104s | n/a | FAIL: THAI_REFINED_TO_JUDGE omits the entire second half of the passage (from "巨大的违和感充斥着邓肯的内心" onward — ~5 paragraphs covering Duncan's memory search, the two hypotheses, and the l |
| `qwen_cli` | `adversarial__ch003-block-002__omission` | adversarial | fail | fail | 100 | 37.843s | n/a | FAIL: The THAI_REFINED_TO_JUDGE omits the final paragraph of the Chinese source — the passage about Duncan wondering whether this world has no normal weather and whether the overca |
| `qwen_cli` | `adversarial__ch005-block-004__addition` | adversarial | fail | fail | 100 | 38.284s | n/a | FAIL: THAI_REFINED_TO_JUDGE prepends an unsupported sentence "หนังสือพิมพ์ยืนยันว่าเรื่องทั้งหมดเป็นข่าวปลอม" (The newspaper confirms the whole story is fake news) that has no corr |
| `qwen_cli` | `adversarial__ch009-block-003__glossary` | adversarial | fail | fail | 100 | 26.429s | n/a | FAIL: Name inconsistency — "ดันแคน" in THAI_LITERAL vs "ดันแคง" in THAI_REFINED_TO_JUDGE for "邓肯". The refined version uses a different transliteration (แคง vs แคน) without justifi |
| `qwen_cli` | `adversarial__ch012-block-003__chinese` | adversarial | fail | fail | 100 | 28.479s | n/a | FAIL: Thai body text contains untranslated Chinese "灵界边缘" appended at the end. |
| `qwen_cli` | `adversarial__ch018-block-004__omission` | adversarial | fail | fail | 100 | 35.129s | n/a | FAIL: Missing the entire cultist chant paragraph — "伪日终将坠落，真实的太阳神将自血与火中复活！万物生机归于太阳，万物秩序归于太阳！" is omitted from the Thai output. |
| `qwen_cli` | `adversarial__ch023-block-002__addition` | adversarial | fail | fail | 100 | 30.098s | n/a | FAIL: The refined version adds a final sentence "เขารู้สึกดีใจอย่างสุดซึ้งทั้งที่ไม่มีเหตุผลใดรองรับ" ("He felt deeply delighted for no reason at all") that does not exist in the C |
| `qwen_cli` | `adversarial__ch028-block-004__glossary` | adversarial | fail | fail | 100 | 34.633s | n/a | FAIL: Missing the sentence "นครรัฐปรานด์ยามดึกสงัดก็สิ้นสุดความวุ่นวายตลอดทั้งวัน" — the refined version drops "ยามดึกสงัดก็สิ้นสุดความวุ่นวายตลอดทั้งวัน" and replaces it with "ในย |
| `qwen_cli` | `adversarial__ch032-block-006__omission` | adversarial | fail | fail | 100 | 17.230s | n/a | FAIL: The Thai translation is truncated mid-sentence — the entire second half of the question (the alternative about coming from a deeper layer) is missing. |
| `qwen_cli` | `adversarial__ch038-block-005__perspective` | adversarial | fail | fail | 100 | 40.962s | n/a | FAIL: The refined version prepends "เขาคิดว่า" (He thought that) to the first paragraph, which is an unsupported addition — the Chinese source has no such framing. This introduces  |
| `qwen_cli` | `adversarial__ch045-block-003__meaning` | adversarial | fail | fail | 100 | 31.546s | n/a | FAIL: The refined version replaces the entire dialogue (Nina's schedule, Duncan's question, their argument, and the correction about who was entrusted to whom) with a single summar |

## Fixture Notes

- Historical-recovery-derived cases use blocks that had historical failed or hard-fail records, then inject one controlled failure when the original bad artifact was not preserved.
- Adversarial cases use current clean artifacts and inject one controlled QA defect.
- The report should be used for QA routing decisions only; it does not evaluate literal translation, refinement, glossary scan, or formatting.

## Safety

- No API key or bearer token is written to artifacts or this report.
- No production ledger, glossary notes, source files, chapter work artifacts, final outputs, or provider config are modified by the benchmark.
