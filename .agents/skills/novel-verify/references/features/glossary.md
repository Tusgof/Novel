# Glossary

**What.** Each novel keeps its glossary in its local `01_Glossary/`. Terms are scanned from chapters, proposed with evidence, reviewed, and approved; only approved terms are projected into the literal pass.

**How the owner asks.** Usually as part of translation or repair; directly as "ตรวจ glossary …" or an audit request (`NOVEL_OPERATOR_GUIDE.md` §5).

**Drive it.**
```
python -m novel_pipeline.cli --config "<Novel>/.system/config.yaml" scan-terms --help
python -m novel_pipeline.cli --config "<Novel>/.system/config.yaml" approve-terms --chapter-id ch211
python -m novel_pipeline.cli --config "<Novel>/.system/config.yaml" report glossary-conflicts --help
python -m novel_pipeline.cli --config "<Novel>/.system/config.yaml" report glossary-guard --help
```

**Verify.** `report glossary-conflicts` shows no unresolved conflict for the terms you touched; `report glossary-guard` passes for the affected chapters.

**Gotchas.**
- Agents propose; the owner approves. Never promote `proposed` terms to approved on your own.
- Novels never share glossaries: each `--config` selects its own novel's context, and the resolver refuses a sibling novel's files.
