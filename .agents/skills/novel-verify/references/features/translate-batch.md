# Translate a batch

**What.** The Lean production pipeline for one novel: project approved glossary terms into a source copy → literal translation per block → whole-chapter refinement in the novel's voice → QA against the original → local formatting → guardrails and Sentinel on staging → promotion into `05_Output`. New terms are harvested as `proposed`, never auto-approved.

**How the owner asks.** "ช่วยแปล [เรื่อง] [ช่วงตอน] …" — see `NOVEL_OPERATOR_GUIDE.md` §1.

**Drive it.**
```
python -m novel_pipeline.cli --config "<Novel>/.system/config.yaml" preflight
python -m novel_pipeline.cli --config "<Novel>/.system/config.yaml" lean-run --chapters ch211-ch215 --run-id <id> --dry-run
python -m novel_pipeline.cli --config "<Novel>/.system/config.yaml" lean-run --chapters ch211-ch215 --run-id <id>
python -m novel_pipeline.cli --config "<Novel>/.system/config.yaml" status --run-id <id>
```
Add `--resume` to `lean-run` to reuse valid checkpoints after an interruption.

**Verify.** The chapter files exist under the novel's `05_Output/`, the run's Sentinel result for the batch scope has no blocker or major findings ([quality-gates.md](quality-gates.md)), and a spot-check reads the first, last, and one middle chapter against source. Then publish ([moonread-publish.md](moonread-publish.md)) if the batch is for readers.

**Gotchas.**
- Keep batches small (5 chapters): longer runs raise timeout, QA hard-fail, and glossary-drift risk.
- A valid QA `FAIL` is adjudicated by the configured fallback; a deterministic rule failure blocks immediately. Neither is a reason to force-accept.
- Provider routing and fallbacks come from each novel's `<Novel>/.system/providers.yaml`; do not edit routing to get a run through.
- `preflight` blocks when the novel's local data folders (`01_Glossary`, `03_Raw`, `04_Work`, `05_Output`, `06_Logs`) are missing — they are local and not in Git.
