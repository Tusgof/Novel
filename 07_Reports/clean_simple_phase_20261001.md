# Clean & Simple Phase Report

Date: 2026-10-01

## Scope

This pass removed the unused local dashboard and employee-alias layer. It did not change provider routing, translation output, ledger history, glossary policy, Sentinel rules, or MoonRead content.

## Removed

- `Deep Sea Embers/novel_pipeline/operator_ui.py`
- `Deep Sea Embers/novel_pipeline/employees.py`
- `Deep Sea Embers/assets/dashboard/employee-chibi-spritesheet.png`
- `Deep Sea Embers/DESIGN.md`
- `Deep Sea Embers/OPERATOR_MANUAL.md`
- CLI `operator` command and its obsolete tests
- Dashboard/employee-alias references from active architecture, control docs, and worker templates

## Retained

- Direct bounded pipeline CLI: fetch, scan, approve, translate, refine, QA, format, resume, recovery, status, and reports
- `preflight`, `project_setup`, ledger/artifacts, deterministic guardrails, Sentinel, and MoonRead integration
- Libra as a glossary/pilot method name; only the dashboard employee-alias layer was removed
- Historical dashboard reports under novel `07_Reports/` as evidence; they are not runtime dependencies

## Root Cause

The project had accumulated a local control surface that duplicated the direct CLI and represented pipeline stages as fictional employee identities. It increased maintenance and test surface without being part of the current operating workflow.

## Prevention

- `cli.py` now exposes only direct pipeline commands; a removed dashboard cannot be reintroduced accidentally through an active entrypoint.
- Product/recovery reports validate only canonical root docs and active pipeline files.
- Architecture and templates name real stages and worker protocol roles instead of employee aliases.
- Future UI work requires a separate explicit milestone; it is not part of the translation pipeline by default.

## Verification

- `python -m compileall novel_pipeline`: passed
- `python test_translation.py`: passed; all tests passed
- `novel-pipeline --config ".system/config.yaml" --help`: passed; no `operator` command listed
- `novel-pipeline --config ".system/config.yaml" preflight`: exit `0`, status `degraded` only for dirty worktree warning
- `novel-pipeline --config ".system/config.yaml" report recovery-drill`: exit `0`, `accepted`
- `novel-pipeline --config ".system/config.yaml" report product-review --run-id batch-ch019-ch023-v1`: output acceptance checks passed; overall `degraded` only for dirty worktree warning
- `git diff --check`: passed
- Active-code/reference scan: no remaining dashboard implementation, employee roster, or operator CLI references

## Next Step

Review the simplified boundaries in the root `ARCHITECTURE.md`, then perform the architecture convergence pass as a separate change. No translation or MoonRead publication was run in this cleanup.
