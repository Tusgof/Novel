# Architecture: Novel Translation Workspace

Last updated: 2026-10-03

This document defines stable ownership and runtime boundaries. Current status belongs in `PROJECT_BRAIN.md`; planned work belongs in `IMPLEMENT_PLAN.md`.

## 1. Product Boundary

The workspace translates source web novels into Thai and publishes only verified Markdown to MoonRead. It supports multiple novels, languages, source adapters, novel-specific voice profiles, auditable bounded runs, recovery, and quality gates.

The selected novel is always explicit. The runtime must never infer DSE from the current directory, a missing config argument, or a provider helper path.

## 2. Two-Level Architecture

### Project layer: `Novel/` (Layer 0)

This is the multi-novel system and owns behavior that must be safe for every novel:

| Area | Canonical location | Responsibility |
| --- | --- | --- |
| Shared runtime | `novel_pipeline/` | CLI, Lean stages, config loading, ledger/artifact helpers, provider execution |
| Shared helpers | `scripts/` | OpenRouter shim, deterministic guardrails, Sentinel, source/reader checks |
| Registry and shared policy | `00_Config/` | novel registry, cross-novel quality thresholds, reader policy |
| Reader | `MoonRead/` | generated reader content, UI, publish verification, lint/build/smoke |
| Durable project memory | root `PROJECT_BRAIN.md`, `IMPLEMENT_PLAN.md`, `ARCHITECTURE.md`, `AGENTS.md` | intent, roadmap, structure, behavior policy |
| Evidence | root `01_Research_Log/`, `07_Reports/` | experiments, audits, checkpoints, incident evidence |

Project-layer code may read a selected novel context, but it must not contain default paths to a specific novel. Shared code must use `AppConfig.workspace` and the selected config's registry identity.

### Migration status (verified 2026-10-03)

- The root `novel_pipeline/` package is the only canonical runtime package.
- All five registered novel configs select `pipeline_engine: lean`.
- `Deep Sea Embers/novel_pipeline/__init__.py` is only a compatibility shim; it redirects submodule resolution to the root package. It is not a second engine.
- The 36 old DSE-local runtime modules were removed; their migrated root counterparts retain historical recovery support. Git preserves the old source history.
- `novel_pipeline/pipeline.py` remains as a compatibility/recovery module for historical tests and artifacts. Lean production dispatch does not call its legacy end-to-end runner, and the CLI rejects legacy stage commands for Lean configs.
- This migration was verified without provider calls. A new provider-backed production batch is still a separate bounded operation, not evidence silently inferred from the migration tests.

### Novel layer: `<Novel>/` (Layer 1 and Layer 2)

Each novel is an isolated Obsidian vault and runtime context:

| Area | Canonical location | Responsibility |
| --- | --- | --- |
| Runtime selection | `<Novel>/.system/config.yaml` | novel ID, source language, source adapter, `pipeline_engine`, batch/chunk policy |
| Provider policy | `<Novel>/.system/providers.yaml` | stage routes and fallbacks; helper paths must resolve to this novel or root shared scripts |
| Novel voice | `<Novel>/.system/lean_voice.md`, `style_profiles.yaml`, `RESEARCH_PROFILE.yaml` | compact refine guidance, genre, tone, source-specific context |
| Terms and policy | `<Novel>/01_Glossary/`, `02_Database_Views/` | approved terms, aliases, rejected variants, Obsidian notes and novel-specific policies |
| Source | `<Novel>/03_Raw/` | fetched source and manifest; source of truth for translation input |
| Run state | `<Novel>/04_Work/`, `<Novel>/06_Logs/` | bounded checkpoints, artifacts, append-only ledger, recovery state |
| Product | `<Novel>/05_Output/` | final Thai Markdown only; never used as source input |
| Evidence | `<Novel>/07_Reports/` | novel-specific reports and checkpoints |

Novel-layer rules may tune voice, terminology, source parsing, and known false positives. They may not silently change shared quality gates, provider safety, or reader publication policy.

## 3. Context Contract

Every command that can read or write novel data must receive an explicit `--config <Novel>/.system/config.yaml`. The loader derives the novel root from that config path and constructs every runtime path from it.

Provider helper resolution follows this order only:

1. `<Novel>/scripts/<helper>` if the novel owns a helper;
2. `<Workspace>/scripts/<helper>` for shared helpers;
3. fail closed if the helper does not exist.

Sibling novel paths are rejected. Provider `--cd` must equal the selected novel root. The root CLI has no DSE default config.

Production checkpoint and trace paths stay under the selected novel's
`04_Work/_lean_runs/`; experiment paths stay under its `04_Work/`. Run IDs are
single safe directory names, and resume cannot change the original chapter scope.
New-novel scaffolding selects Lean and creates its own voice profile, not a copy
of the template novel's character policy.

The old copies under novel folders are compatibility files only; they are not canonical entrypoints. New work uses the root package and root shared scripts. Provider helper resolution rejects absolute or relative paths that escape the selected novel or root `scripts/` boundary.

## 4. Production Lean Pipeline

All registered novel configs currently declare `pipeline_engine: lean`. `novel-pipeline run` dispatches to the chapter-aware Lean engine for those configs; the explicit `lean-run` command is available for diagnostics.

```text
explicit novel config
  -> verify raw source and novel context
  -> project approved, chapter-relevant glossary terms into a source copy
  -> literal translation in transport-safe blocks
  -> assemble the chapter
  -> refine once with the novel's compact style profile
  -> chapter-level QA against original source + refined text (literal retained for rule checks)
  -> local Markdown spacing normalization (no AI content rewrite)
  -> deterministic output validation
  -> stage candidate Markdown under 04_Work/_lean_runs/<run-id>/_staged_output
  -> blocking Sentinel on the staged candidate only
  -> atomically promote verified Markdown into 05_Output
```

The original source remains the semantic source of truth. Harvested terms are proposals until reviewed; they are never silently promoted to the production glossary. Checkpoints and provider traces live under `<Novel>/04_Work/_lean_runs/<run-id>/`, not in product output.

Production runs remain bounded by explicit chapter range and run ID. A provider failure, validation failure, QA hard-fail, manual action, Sentinel blocker or major finding, or unexpected scope expansion stops the run.

Shared Lean prompts live in root `prompts/lean/`; only the refinement voice is
novel-specific. Production Sentinel always includes deterministic guardrails,
regardless of an inherited experiment skip flag.

No product file is written before the chapter set passes the production gate. A failed gate leaves the existing `05_Output` unchanged. The run report records staged paths, promotion results, and the Sentinel report.

Promotion is atomic per file, not a multi-file transaction. If a disk error occurs
after some files are promoted, the run is blocked and reports those exact paths.
Literal, refinement, QA and harvest honor their configured provider routes and
fallbacks; routing changes require separate authorization.

## 5. Guardrail Ownership

1. provider response validation: shared runtime
2. chapter QA: shared runtime plus novel style profile
3. deterministic output checks: root `scripts/check_output_quality_guardrails.py`
4. glossary coverage and conflict checks: shared runtime plus novel glossary
5. Sentinel: root `scripts/sentinel_quality_report.py`
6. MoonRead generation and reader checks: `MoonRead/`
7. human/Inspector spot-check: project acceptance gate

Fix recurring defects at the lowest layer that safely catches them. Promote a novel rule to project layer only after evidence shows it is cross-novel and has low false-positive risk.

## 6. Ownership

- Codex owns project architecture, layer promotion, provider-routing changes, run scope, acceptance, documentation, commit, and publication decisions.
- Luna Max may execute explicitly bounded translation work through the HERDR protocol. It cannot change project policy, routing, quality thresholds, or canonical docs without a separate authorized work order.
- Novel configuration owns data and voice for that novel, not the shared runtime.
- MoonRead consumes verified generated content and never mutates translation source, glossary, ledger, or work artifacts.

## 7. Non-Negotiable Boundaries

- `03_Raw` is source input; `05_Output` is product output.
- `06_Logs/run_ledger.jsonl` is append-only.
- Experiment artifacts never overwrite production artifacts.
- No provider key or transcript containing credentials is committed.
- No command may silently fall back to DSE or another sibling novel.
- A command must not mutate novel identity with `--novel`; the selected `.system/config.yaml` is authoritative.
- No experiment or production run is complete without deterministic checks, blocking Sentinel, and the major-run spot-check policy where applicable.
