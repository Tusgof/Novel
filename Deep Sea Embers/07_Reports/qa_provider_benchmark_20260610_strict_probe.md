# QA Provider Cost/Quality Benchmark - qa_provider_benchmark_20260610_strict_probe

Generated: 2026-06-10T01:05:40

## Scope

- Non-production QA-only comparison.
- Production routing was not changed.
- Compared candidates: `openrouter_v4_flash_reasoning_strict`.
- Cases: 15 total: 10 known-pass, 10 historical-recovery-derived fail cases, 10 adversarial fail cases.

## Summary

| Candidate | Provider | Model | Request options | Calls | Avg score | False negatives | Severe false negatives | False positives | Parse failures | Provider failures | Avg latency | Est. cost | Est. cost / 100 blocks |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `openrouter_v4_flash_reasoning_strict` | openrouter | `deepseek/deepseek-v4-flash` | `{"max_tokens":1500,"reasoning":{"enabled":true,"exclude":true}}` | 15 | 66.67 | 2 | 2 | 2 | 4 | 0 | 31.657s | 0.00515377 | 0.034358 |

## Recommendation

Insufficient OpenRouter data; keep current QA routing until the benchmark can be rerun.

## Per-Case Results

| Candidate | Case | Group | Expected | Predicted | Score | Latency | Cost | First line |
| --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |
| `openrouter_v4_flash_reasoning_strict` | `pass__ch008-block-003` | known_pass | pass | pass | 100 | 8.685s | 0.00026541 | PASS: The translation is complete and accurate, with no omissions, additions, meaning drift, or glossary inconsistencies. |
| `openrouter_v4_flash_reasoning_strict` | `pass__ch011-block-002` | known_pass | pass | pass | 100 | 28.742s | 0.00017143520000000002 | PASS: All content present, meaning preserved, no omissions/additions, names and glossary consistent, no Chinese leakage, tone appropriate. |
| `openrouter_v4_flash_reasoning_strict` | `pass__ch021-block-001` | known_pass | pass | fail | 45 | 35.053s | 0.00029086970000000005 | FAIL: "面具神官" (masked priest) mistranslated as "นักบวชแห่งเทพหน้ากาก" (priest of the mask god), adding unsupported religious affiliation. |
| `openrouter_v4_flash_reasoning_strict` | `pass__ch034-block-002` | known_pass | pass | pass | 100 | 5.928s | 0.0003487684 | PASS: The translation is complete, accurate, and natural, with no omissions, additions, meaning drift, Chinese leakage, or tone inconsistencies. |
| `openrouter_v4_flash_reasoning_strict` | `pass__ch042-block-002` | known_pass | pass | fail | 45 | 32.029s | 0.00027366719999999997 | FAIL: Unsupported addition: "กว่าที่คิด" ("than thought") in first sentence not present in Chinese source. |
| `openrouter_v4_flash_reasoning_strict` | `historical__ch029-block-005__chinese` | historical_recovery_derived | fail | pass | 35 | 8.533s | 0.0003782584 | PASS: All content from the Chinese source is fully and accurately translated into Thai, with no omissions, additions, or meaning drift; glossary terms are consistent, and no Chines |
| `openrouter_v4_flash_reasoning_strict` | `historical__ch037-block-002__omission` | historical_recovery_derived | fail | unknown | 35 | 121.291s | 0.00047134849999999997 | None |
| `openrouter_v4_flash_reasoning_strict` | `historical__ch044-block-001__addition` | historical_recovery_derived | fail | unknown | 35 | 13.504s | 0.0004827513 | None |
| `openrouter_v4_flash_reasoning_strict` | `historical__ch013-block-001__glossary` | historical_recovery_derived | fail | unknown | 35 | 65.200s | 0.00047066039999999994 | None |
| `openrouter_v4_flash_reasoning_strict` | `historical__ch017-block-003__addition` | historical_recovery_derived | fail | fail | 100 | 22.036s | 0.0002855615 | FAIL: Unsupported addition "ในปริสสันของปรานด์" at the start, not present in Chinese source. |
| `openrouter_v4_flash_reasoning_strict` | `historical__ch019-block-005__omission` | historical_recovery_derived | fail | fail | 100 | 12.025s | 0.0002692437 | FAIL: Unsupported addition at the end: "ข้อความนี้ไม่มีในต้นฉบับ" is not in the source. |
| `openrouter_v4_flash_reasoning_strict` | `adversarial__ch003-block-002__omission` | adversarial | fail | fail | 100 | 5.016s | 0.000328322 | FAIL: Missing the final sentences about the sky having been like this since he arrived and his suspicion about eternal overcast. |
| `openrouter_v4_flash_reasoning_strict` | `adversarial__ch009-block-003__glossary` | adversarial | fail | fail | 100 | 24.086s | 0.00032458659999999996 | FAIL: ชื่อตัวละคร “ดันแคน” เปลี่ยนเป็น “ดันแคง” ไม่สอดคล้องกับต้นฉบับ |
| `openrouter_v4_flash_reasoning_strict` | `adversarial__ch012-block-003__chinese` | adversarial | fail | unknown | 35 | 38.560s | 0.00047154509999999995 | None |
| `openrouter_v4_flash_reasoning_strict` | `adversarial__ch028-block-004__glossary` | adversarial | fail | pass | 35 | 54.171s | 0.0003213427 | PASS: The translation is complete, accurate, consistent with glossary terms, and maintains natural Thai tone without omissions or additions. |

## Fixture Notes

- Historical-recovery-derived cases use blocks that had historical failed or hard-fail records, then inject one controlled failure when the original bad artifact was not preserved.
- Adversarial cases use current clean artifacts and inject one controlled QA defect.
- The report should be used for QA routing decisions only; it does not evaluate literal translation, refinement, glossary scan, or formatting.

## Safety

- No API key or bearer token is written to artifacts or this report.
- No production ledger, glossary notes, source files, chapter work artifacts, final outputs, or provider config are modified by the benchmark.
