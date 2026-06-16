# V6.13 Glossary Queue Cleanup Execution Proposal - 2026-06-16

Purpose: define the exact low-risk cleanup path for the 46 visible untracked glossary notes, without modifying the notes yet.

No provider calls were made. No glossary notes, ledger records, source files, output files, MoonRead files, provider config, or runtime artifacts were modified.

## Current Queue

Visible untracked glossary queue:

- 46 glossary notes under `01_Glossary/`
- all 46 are `status: approved`
- all 46 have required fields
- no duplicate `original_term` inside the queue
- no duplicate `thai_term` inside the queue
- no `original_term` overlap with tracked glossary
- one `thai_term` overlap with tracked glossary:
  - untracked `01_Glossary/真实的太阳神.md`
  - tracked `01_Glossary/实太阳神.md`
  - both render as `สุริยเทพที่แท้จริง`

Evidence:

- `07_Reports/v6_13_glossary_queue_review_20260616.md`
- `07_Reports/v6_13_glossary_alias_overlap_proposal_20260616.md`

## Recommended Decision

Use the existing alias mechanism.

Recommended cleanup:

1. Keep tracked `01_Glossary/实太阳神.md` as the canonical glossary note.
2. Add `真实的太阳神` to its `aliases` list.
3. Do not commit untracked `01_Glossary/真实的太阳神.md` as a second standalone note.
4. Commit the other 45 untracked approved glossary notes.
5. Remove only `01_Glossary/真实的太阳神.md` from the visible queue after the canonical alias is committed.

This keeps the glossary single-source for the title concept while preserving the accepted Thai term.

## Exact File Actions If Approved

Approved action set:

| action | path | detail |
| --- | --- | --- |
| edit tracked note | `01_Glossary/实太阳神.md` | add alias `真实的太阳神` |
| stage untracked notes | 45 glossary notes excluding `真实的太阳神.md` | commit as approved glossary expansion |
| remove untracked duplicate note | `01_Glossary/真实的太阳神.md` | delete only after alias is added and staged |
| do not touch | `06_Logs/`, `04_Work/`, `05_Output/`, `.system/`, `novel_pipeline/` | no runtime or artifact changes |

Expected canonical note frontmatter after edit:

```yaml
original_term: 实太阳神
thai_term: สุริยเทพที่แท้จริง
category: title
status: approved
aliases:
  - 真实的太阳神
```

## Validation If Approved

Before commit:

```powershell
cd "D:\Fogust\Workspace\Novel\Deep Sea Embers"
$env:PYTHONIOENCODING='utf-8'
python -m compileall novel_pipeline test_translation.py
python test_translation.py
python scripts\check_output_quality_guardrails.py
novel-pipeline --config ".system/config.yaml" report glossary-conflicts --output "07_Reports/glossary_conflicts_after_v6_13_cleanup.md"
git diff --check
git status --short
```

Required result:

- tests pass
- final-output guardrails pass
- glossary conflict report has no unintended duplicate/overlap issue
- staged diff contains only:
  - `01_Glossary/实太阳神.md`
  - 45 approved glossary notes
  - optional cleanup validation report
  - deletion of untracked `01_Glossary/真实的太阳神.md`

## Commit Shape If Approved

One dedicated glossary-only commit:

```text
Resolve glossary alias queue
```

Do not combine with:

- runtime changes
- provider routing changes
- translation runs
- MoonRead generation
- V6.18 benchmark implementation
- report archive cleanup

## Risks And Mitigation

| risk | mitigation |
| --- | --- |
| duplicate Thai term remains as two source notes | use alias on canonical note and remove duplicate standalone note |
| accidentally committing unrelated untracked reports | stage only `01_Glossary/*.md` selected files and inspect `git diff --cached --name-only` |
| losing the variant term | alias preserves `真实的太阳神` in glossary index |
| broad artifact mutation | do not run pipeline translation or provider calls |

## Stop Rule

This report is not approval to modify glossary notes. It is an execution proposal only. Wait for explicit approval before editing, deleting, staging, or committing the glossary queue.
