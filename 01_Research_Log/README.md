# Research Log Index

สารบัญนี้เรียงลำดับบันทึกการวิจัย V6.34 จากจุดเริ่มต้นถึงรายการล่าสุด เพื่อให้อ่านตามลำดับเหตุการณ์ได้ง่าย

หมายเหตุ:

- ไฟล์ log ตัวจริงยังใช้ชื่อแบบ `YYYY-MM-DD_novel_pipeline_...md` ตาม `RESEARCH_LOG_FORMAT.md`
- เลข `001`, `002`, ... ในไฟล์นี้คือ "ลำดับอ่าน" ไม่ใช่ชื่อไฟล์
- รายการที่เป็น failure/stop ยังเก็บไว้ เพราะเป็นหลักฐานการทดลอง ไม่ใช่งานพังที่ควรลบ
- ไฟล์ชุดเก่า `libra_blind_pilot_*` ถูกลบแล้ว เพราะเป็นเส้นทางก่อนปรับ scope ให้ถูกต้องตาม V6.34 ปัจจุบัน

## ลำดับอ่าน V6.34

| ลำดับ | อ่านเมื่อ | ไฟล์ | อ่านเพื่อเข้าใจอะไร |
|---:|---|---|---|
| 001 | เริ่มแผน | `2026-06-30_novel_pipeline_v6_34_charter.md` | กรอบทดลอง V6.34, คำถามหลัก, metric, stop rule, no-production rule |
| 002 | เตรียม sample | `2026-06-30_novel_pipeline_v6_34_source_pool_sampling.md` | ตรวจ raw source pool และล็อก sample ข้าม DSE/HGD/IRS |
| 003 | Baseline gate | `2026-06-30_novel_pipeline_v6_34_m3_scan_glossary_gate.md` | scan/glossary gate สำหรับ baseline |
| 004 | Baseline stop | `2026-06-30_novel_pipeline_v6_34_m3_hgd_baseline_stop.md` | baseline หยุดที่ HGD `ch037` เพราะ glossary/title coverage |
| 005 | วิเคราะห์ baseline | `2026-06-30_novel_pipeline_v6_34_m4_initial_analysis.md` | วิเคราะห์ `ch037` ว่าปัญหาเป็น title sidecar/glossary inconsistency |
| 006 | เลือก treatment | `2026-07-01_novel_pipeline_v6_34_m4_treatment_selection.md` | เลือก treatment เรื่อง title/H1 glossary validation |
| 007 | HGD treatment stop | `2026-07-01_novel_pipeline_v6_34_m5_hgd_treatment_early_stop.md` | HGD treatment หยุดที่ `ch024` จาก approved glossary English leakage |
| 008 | HGD checkpoint | `2026-07-01_novel_pipeline_v6_34_m5_hgd_treatment_checkpoint.md` | HGD treatment ผ่านจุด baseline stop เดิม (`ch024`, `ch037`) |
| 009 | HGD BOM repair | `2026-07-01_novel_pipeline_v6_34_m5_hgd_ch132_bom_glossary_repair.md` | แก้ BOM/glossary parsing ที่กระทบ HGD `ch132` |
| 010 | HGD treatment complete | `2026-07-01_novel_pipeline_v6_34_m5_hgd_treatment_completion.md` | HGD in-sample treatment 10 ตอนจบและ Sentinel ผ่าน |
| 011 | HGD comparison | `2026-07-01_novel_pipeline_v6_34_m5_hgd_baseline_vs_treatment_comparison.md` | เทียบ HGD baseline vs treatment ว่าดีขึ้นตรงไหนและยังไม่ลื่นตรงไหน |
| 012 | DSE source mismatch | `2026-07-01_novel_pipeline_v6_34_m5_dse_source_mismatch_stop.md` | DSE treatment vault ผิด source parity จึงหยุดก่อนวัดผล |
| 013 | DSE treatment v2 | `2026-07-01_novel_pipeline_v6_34_m5_dse_treatment_v2_completion.md` | DSE treatment rebuild ถูกต้องและจบครบ in-sample |
| 014 | IRS ch020 stop | `2026-07-01_novel_pipeline_v6_34_m5_irs_treatment_ch020_stop.md` | IRS หยุดที่ `ch020` จาก glossary-note leakage หลัง source มี bare `Footnotes:` |
| 015 | IRS footnote prevention | `2026-07-01_novel_pipeline_v6_34_m5_irs_footnote_marker_prevention.md` | เพิ่ม prevention สำหรับ bare `Footnotes:` ใน non-CJK source |
| 016 | IRS treatment complete | `2026-07-01_novel_pipeline_v6_34_m5_irs_treatment_completion.md` | IRS in-sample treatment จบ มี minor `Complete Memory` เหลือเป็น evidence |
| 017 | Cross-novel comparison | `2026-07-01_novel_pipeline_v6_34_m5_cross_novel_treatment_comparison.md` | สรุป HGD/DSE/IRS treatment ก่อนเข้า OOS |
| 018 | Pre-OOS hardening | `2026-07-01_novel_pipeline_v6_34_m5_pre_oos_cjk_parenthetical_hardening.md` | hardening CJK/Hanja parenthetical ก่อน OOS |
| 019 | OOS scan/glossary | `2026-07-01_novel_pipeline_v6_34_m6_oos_scan_glossary_gate.md` | เปิด OOS ด้วย scan/glossary gate ข้าม 3 เรื่อง |
| 020 | HGD OOS ch131 stop | `2026-07-01_novel_pipeline_v6_34_m6_oos_hgd_ch131_stop.md` | OOS หยุดที่ HGD `ch131` จาก glossary conflict |
| 021 | ch131 analysis | `2026-07-01_novel_pipeline_v6_34_m6_oos_ch131_analysis.md` | วิเคราะห์ `Containment Department` vs `Containment Sector` |
| 022 | ch131 treatment | `2026-07-01_novel_pipeline_v6_34_m6_ch131_treatment.md` | เพิ่ม source-surface collision detection และแก้ HGD alias conflict |
| 023 | HGD OOS ch184 stop | `2026-07-01_novel_pipeline_v6_34_m6_oos_hgd_ch184_stop.md` | OOS หยุดที่ `ch184` จาก false glossary `Enter` และ semantic drift |
| 024 | ch184 analysis | `2026-07-01_novel_pipeline_v6_34_m6_oos_ch184_analysis.md` | วิเคราะห์ `Enter` matched inside `Entering` และเลือก boundary-aware matching |
| 025 | ch184 treatment | `2026-07-01_novel_pipeline_v6_34_m6_ch184_treatment.md` | เพิ่ม boundary-aware glossary subset matching และ rerun `ch184` |
| 026 | HGD OOS ch192 stop | `2026-07-01_novel_pipeline_v6_34_m6_oos_hgd_ch192_stop.md` | OOS หยุดที่ `ch192` จาก peer dialogue `คุณ`/`นาย` drift |
| 027 | ch192 treatment | `2026-07-01_novel_pipeline_v6_34_m6_ch192_pronoun_treatment.md` | เพิ่ม HGD-only peer-address repair หลัง literal-safe omission recovery |
| 028 | HGD OOS completion | `2026-07-01_novel_pipeline_v6_34_m6_hgd_oos_completion.md` | HGD OOS จบครบ 10 ตอน, Sentinel `0/0/0/0`, แต่ยังมี smoothness risk |
| 029 | DSE OOS source parity stop | `2026-07-01_novel_pipeline_v6_34_m6_dse_oos_source_parity_stop.md` | DSE OOS หยุดเพราะ experiment vault ใช้ raw source stale/off-by-one ทั้ง 10 sampled chapters |
| 030 | DSE ch029 source-script treatment | `2026-07-01_novel_pipeline_v6_34_m6_dse_ch029_source_script_treatment.md` | เพิ่ม cleanup แคบ ๆ สำหรับ Chinese annotation ที่หลุดใน Thai output แล้ว rerun `ch029-block-005` ผ่าน QA |
| 031 | DSE OOS completion | `2026-07-01_novel_pipeline_v6_34_m6_dse_oos_completion.md` | DSE OOS v2 จบครบ 10 ตอน, guardrails ผ่าน, source parity 0, และเพิ่ม duplicate-title prevention |
| 032 | IRS OOS completion | `2026-07-01_novel_pipeline_v6_34_m6_irs_oos_completion.md` | IRS OOS จบครบ 10 ตอน, source parity 0, Sentinel `0/0/0/0`, แต่ยังมี provider smoothness risk |
| 033 | Cross-novel OOS comparison | `2026-07-01_novel_pipeline_v6_34_m6_cross_novel_oos_comparison.md` | เทียบ HGD/DSE/IRS OOS และสรุปว่า production ต่อได้แบบ bounded sequential แต่ยังไม่ควร long unattended |

## ไฟล์ที่ลบออก

ไฟล์ต่อไปนี้ถูกลบเพราะเป็นบันทึกจากเส้นทางเก่าก่อนแผน V6.34 ปัจจุบันถูกล็อกให้เป็น cross-novel/raw-source experiment:

- `2026-06-30_novel_pipeline_libra_blind_pilot_baseline_v6_34b.md`
- `2026-06-30_novel_pipeline_libra_blind_pilot_source_pool.md`
- `2026-06-30_novel_pipeline_libra_blind_pilot_v6_34c_irs_glossary_approval.md`
- `2026-06-30_novel_pipeline_libra_blind_pilot_v6_34c_irs_glossary_classification.md`
- `2026-06-30_novel_pipeline_libra_blind_pilot_v6_34c_irs_scan.md`
