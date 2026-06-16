# V6.15 Dashboard Usability Follow-Up - 2026-06-16

Scope: improve the local operator dashboard so state-changing controls do not appear usable before their required scope is complete.

## Change Summary

- Added a visible disabled state for dashboard buttons.
- `Start Batch`, `Continue`, and `Run Rerun-Block` now stay disabled until their required scope is complete.
- Action previews now show the missing scope fields instead of a vague incomplete message.
- The dashboard initializes action-preview state immediately on page load, before the read-only bootstrap snapshot finishes.
- Button labels change from locked labels to action labels:
  - `Fill Run ID + Range` -> `Start Scan` or `Start Translation`
  - `Fill Run ID + Boundary` -> `Continue To Boundary`
  - `Fill Run ID + Block` -> `Run Rerun-Block`

## Browser Verification

Temporary server:

```powershell
novel-pipeline --config ".system/config.yaml" operator --host 127.0.0.1 --port 8766
```

Checks:

- Initial page load:
  - `#batchBtn.disabled`: `true`
  - `#resumeBtn.disabled`: `true`
  - `#rerunBtn.disabled`: `true`
  - batch button label: `Fill Run ID + Range`
  - preview text included `Action locked until scope is complete.`
- After entering chapter range `ch051-ch052`:
  - `#batchBtn.disabled`: `false`
  - batch button label: `Start Scan`
  - preview command included `run --range ch051-ch052 --run-id deep-sea-embers-retranslate-ch001-ch050-v2 --stop-after glossary-scan`
- Browser console errors: none

## Validation

```powershell
python -m compileall novel_pipeline scripts test_translation.py
$env:PYTHONIOENCODING='utf-8'; python test_translation.py
```

Both passed.

## Safety

- No provider calls were made.
- No pipeline run/resume/rerun-block was executed.
- No ledger, glossary, source, work artifacts, or final outputs were modified.
- Dashboard server was started only for local browser verification and then stopped.

## Remaining V6.15 Work

This first entry closed the initial usability fix only. Later updates below close the practical V6.15 follow-up scope.

- clearer report grouping and active/historical report decisions
- better glossary queue empty-state and next-action guidance
- stronger visual hierarchy for current blocker vs next safe command
- broader browser smoke flow covering glossary review and recovery controls

## Polish Update: Blocker And Glossary Empty State

Additional scoped dashboard polish was applied after the first fix:

- Current blocker panel now shows a `Do this next:` row with a safe navigation-only button.
- Failed/manual-action blockers route the user to `Recover Block`.
- Degraded/no-blocker states route the user to `Continue Translation`.
- Glossary queue empty-state now distinguishes:
  - no effective scan terms
  - glossary review complete
  - unexpectedly empty queue that should be refreshed
- The glossary empty-state includes a navigation-only next-step button instead of leaving the user to infer what to do.

Browser smoke on `127.0.0.1:8766`:

- Loaded run: `deep-sea-embers-retranslate-ch001-ch050-v2`
- `Do this next:` rendered after bootstrap.
- Blocker next-step button count: `1`
- Clicking the blocker next-step kept focus on `Continue Translation`.
- `Start Batch`, `Continue`, and `Run Rerun-Block` stayed disabled without required scope.
- `No action executed yet.` remained unchanged after clicking the navigation-only next-step.
- Browser console errors: none.

Validation:

```powershell
python -m compileall novel_pipeline scripts test_translation.py
$env:PYTHONIOENCODING='utf-8'; python test_translation.py
$env:PYTHONIOENCODING='utf-8'; python scripts\check_output_quality_guardrails.py
git diff --check
```

All passed.

## Browser Smoke: Glossary And Recovery Surfaces

Additional read-only browser smoke covered the remaining V6.15 glossary/recovery surfaces without provider calls or state-changing actions.

Checks on `127.0.0.1:8766`:

- page loaded as `Novel Operator`
- focus navigation buttons were present for `Review Glossary` and `Recover Block`
- glossary workbench carried `data-focus-group="glossary,all"`
- recovery and block-inspection panels carried `data-focus-group="recovery,all"`
- glossary panel loaded progress for the active run
- provider-assisted suggestion warning remained visible: `Provider-assisted suggestions require an explicit click.`
- custom Thai term input is present in the glossary suggestion UI source
- recovery panel showed no current failures for the loaded run
- `Run Rerun-Block` remained disabled without run/block scope
- `actionResult` stayed `No action executed yet.`
- `reportResult` stayed `No report generated yet.`
- Browser console errors: none.

Conclusion: V6.15 dashboard usability follow-up is closed for the current practical scope. Future dashboard changes should be opened as a new milestone or a specific bug, not as lingering V6.15 work.

## Polish Update: Report Controls Grouping

The report controls were regrouped by operator question instead of a flat row of report-kind buttons:

- `Is the system ready?`: preflight, product review
- `Is this run complete?`: checkpoint, cleanliness
- `What failed?`: provider usage, recovery drill
- `Is glossary safe?`: glossary guard, decisions, conflicts, audit

No report backend or report kind changed. Existing `data-report` actions are preserved.

Browser smoke on `127.0.0.1:8766`:

- report group headings rendered: `Is the system ready?`, `Is this run complete?`, `What failed?`, `Is glossary safe?`
- report action count: `10`
- report actions present: `preflight`, `product-review`, `checkpoint`, `cleanliness`, `provider-usage`, `recovery-drill`, `glossary-guard`, `glossary-decisions`, `glossary-conflicts`, `glossary-audit`
- `reportResult` stayed `No report generated yet.`
- Browser console errors: none.

Validation:

```powershell
python -m compileall novel_pipeline scripts test_translation.py
$env:PYTHONIOENCODING='utf-8'; python test_translation.py
$env:PYTHONIOENCODING='utf-8'; python scripts\check_output_quality_guardrails.py
git diff --check
```

All passed.
