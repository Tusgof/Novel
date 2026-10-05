# Repair a chapter

**What.** Diagnose a reported defect in one chapter (a wrong term, a pronoun, leaked English or Chinese, truncation), fix only what is needed, and add a guardrail or test when the defect can recur.

**How the owner asks.** "ช่วยตรวจและซ่อม [เรื่อง] ตอน [เลข] ปัญหาคือ …" — see `NOVEL_OPERATOR_GUIDE.md` §2.

**Drive it.**
```
python -m novel_pipeline.cli --config "<Novel>/.system/config.yaml" inspect-block --run-id <id> --block-id ch203-block-004
python -m novel_pipeline.cli --config "<Novel>/.system/config.yaml" rerun-block --run-id <id> --block-id ch203-block-004 --from-stage refine
python -m novel_pipeline.cli --config "<Novel>/.system/config.yaml" report glossary-audit --help
```
`inspect-block` never modifies artifacts; start there.

**Verify.** Classify the cause first: one chapter only, a wrong glossary entry, prompt or routing, a guardrail gap, or stale MoonRead content. After the fix, rerun the quality gates on that chapter ([quality-gates.md](quality-gates.md)), search the same batch for the same pattern, and regenerate MoonRead if the chapter is published.

**Gotchas.**
- Fixing the output text alone leaves the cause in place when it was a glossary or prompt problem; fix the source of the defect.
- A recurring defect class deserves a guardrail in `scripts/check_output_quality_guardrails.py` or a test, not only a manual edit.
