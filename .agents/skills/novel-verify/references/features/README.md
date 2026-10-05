# Novel Feature Map

One line per feature: what it is and where its details live. Commands assume the repository root as the working directory; the pipeline entry point is `python -m novel_pipeline.cli` (installed as `novel-pipeline`, defined in `novel_pipeline/cli.py`). Registered novels are listed in `00_Config/novel_registry.json`.

| Feature | What it does | Details |
|:--|:--|:--|
| Translate a batch | Lean production run for a bounded chapter range (5 chapters by default) | [translate-batch.md](translate-batch.md) |
| Repair a chapter | Find the cause of a defect in one chapter, fix only what is needed, prevent recurrence | [repair-chapter.md](repair-chapter.md) |
| Glossary | Propose, review, and approve terms; approved terms feed the literal pass | [glossary.md](glossary.md) |
| Quality gates | Output guardrails and Sentinel on the touched scope | [quality-gates.md](quality-gates.md) |
| Publish to MoonRead | Regenerate reader content from verified output and verify the reader build | [moonread-publish.md](moonread-publish.md) |
| Set up a new novel | Scaffold, fetch raw source, pilot the voice | [new-novel-setup.md](new-novel-setup.md) |
| Preflight, status, recovery | Readiness checks, run status, resuming interrupted runs, reports | [preflight-status-recovery.md](preflight-status-recovery.md) |

Owner-facing phrasing for each request (Thai) is in `NOVEL_OPERATOR_GUIDE.md`; system structure is in `ARCHITECTURE.md`.
