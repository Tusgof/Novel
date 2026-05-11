# System Cleanup Audit - 2026-05-11

## Scope

Read-only audit of the current Deep Sea Embers repo after `V6.0` closure.

This audit does not delete, move, or rewrite runtime artifacts. It only classifies cleanup candidates before destructive work.

## Baseline

- git status: clean before the audit edits
- current accepted product baseline already exists
- no active translation batch
- current cleanup review started after `V6.0E` closure

## Findings

### 1. Canonical docs are clear, but naming is inconsistent

Current canonical root docs:

- `PROJECT_BRAIN.md`
- `IMPLEMENT_PLAN.md`
- `OPERATOR_MANUAL.md`

Issue:

- the actual file is `IMPLEMENT_PLAN.md`
- many references in docs and historical paths still use `Implement_PLAN.md`

Classification:

- action: normalize/rename references
- priority: high
- reason: low-risk cleanup with direct clarity benefit

### 2. `07_Reports/` mixes active baselines with historical/experimental artifacts

Examples of active/high-value reports:

- `preflight_report.md`
- `recovery_drill.md`
- `product_review_batch-ch019-ch023-v1.md`
- `checkpoint_batch-ch019-ch023-v1.md`
- `glossary_*_batch-ch019-ch023-v1.md`
- `spot_check_batch_ch019_ch023_v1.md`

Examples of likely historical/archive candidates:

- `elephant_worker_benchmark_20250418_123456.md`
- `refinement_benchmark_*.md`
- `refinement_comparative_qa_gpt_20260417.md`
- `doc_memory_backup_20260419_151601/`
- older glossary/classification reports for already-closed earlier experiments where equivalent canonical evidence already exists

Classification:

- action: split active vs archive
- priority: high
- reason: current report root is usable but noisy; operational files and old benchmark/history files are mixed together

### 3. `scripts/` contains product-adjacent helpers plus stale benchmark/test helpers

Examples:

- likely still relevant:
  - `run_qa_judgment.py`
- likely review-for-archive/remove:
  - `elephant_only_smoke_benchmark.py`
  - `elephant_worker_benchmark.py`
  - `refinement_benchmark.py`
  - `refinement_benchmark_fix.py`
  - `refinement_benchmark_gpt.py`
  - `generate_benchmark_report.py`
  - `test_provider_command.py`
  - `test_qwen_cli.py`
  - `test_simple.py`

Classification:

- action: classify each script as keep vs archive vs retire
- priority: high
- reason: these scripts look like one-off benchmark/debug helpers from closed decisions, not normal product operation

### 4. Disposable local cache exists and should stay disposable

Observed:

- `__pycache__/` exists at repo root

Git policy:

- already ignored by `.gitignore`

Classification:

- action: remove local cache during cleanup execution
- priority: medium
- reason: not a repo design issue, just filesystem clutter

### 5. Templates and playbooks look mostly clean

Likely keep:

- `00_Templates/Batch-Rollout-Checklist.md`
- `00_Templates/Worker-Bounded-Batch-Prompt.md`
- `00_Templates/Recovery-Drill-Checklist.md`
- `00_Templates/Novel-Profile.yaml`
- `00_Templates/Research-Profile.yaml`
- `NOVEL_SETUP_PLAYBOOK.md`
- `FETCH_ADAPTER_PLAYBOOK.md`
- `RESEARCH_PROFILE_PLAYBOOK.md`

Potential review later:

- very small generic templates such as `Chapter-Template.md` and `Run-Template.md` may or may not still be used, but they are low-risk and low-clutter compared with reports/scripts

Classification:

- action: keep for now
- priority: low

## Recommended Cleanup Order

1. Normalize canonical doc naming references (`IMPLEMENT_PLAN.md` casing)
2. Separate `07_Reports/` into active vs archive surface
3. Review `scripts/` and archive/retire closed benchmark/debug helpers
4. Remove disposable local caches (`__pycache__/`)
5. Re-run compile/tests/preflight/product-review

## Guardrails For Cleanup

- do not touch `03_Raw/`, `04_Work/`, `05_Output/`, or `06_Logs/`
- do not rewrite ledger history
- do not delete current accepted baseline reports without an archive destination
- do not break canonical doc links while fixing naming consistency
- do not remove scripts that are still referenced by current operator/product workflows without verification

## Proposed Next Slice

Update after execution:

- `V6.1B` completed on 2026-05-11 by normalizing active references and git path casing to `IMPLEMENT_PLAN.md`
- next cleanup slice is now `V6.1C`

`V6.1C` - archive and repo-surface cleanup.

Reason:

- report/history and helper-script surface is the next largest practical clutter source after naming normalization
