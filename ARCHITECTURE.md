# Architecture: Novel Translation System

Last updated: 2026-07-02

This document explains stable system structure. It is not the roadmap, current status, or incident log.

## System Purpose

The system translates web novels into Thai through an auditable pipeline:

- fetch and validate source chapters
- scan/approve glossary terms
- translate, refine, QA, format, and assemble bounded batches
- run deterministic quality gates and Sentinel
- publish verified output into MoonRead
- support multiple novels without relying on Codex memory

It does not rewrite ledger history, treat generated reader files as source of truth, silently publish incomplete chapters, or change provider routing without explicit approval.

Main roles:

- user: chooses priorities, glossary decisions, and production approval
- Codex architect: plans, reviews, verifies, and updates durable rules
- bounded worker: implements a narrow assigned scope
- dashboard/operator: runs bounded workflows and inspects blockers

HERDR coding-agent workers are transport-scoped implementation actors. They are separate from dashboard employee aliases and from translation provider stages; neither aliases nor provider routing grants a HERDR worker authority.

## Source Of Truth Map

Workspace control docs:

- `AGENTS.md`: work policy and agent behavior
- `PROJECT_BRAIN.md`: current verified state, active risks, guardrails, next safe action
- `IMPLEMENT_PLAN.md`: roadmap, milestones, acceptance gates
- `ARCHITECTURE.md`: structure, boundaries, flows, ownership
- `HERDR_WORKER_PROTOCOL.md`: bounded transport and verification rules for coding-agent workers
- `DOC_RECOVERY.md`: canonical doc hashes and recovery steps

Shared/system config:

- `00_Config/novel_registry.json`: registered novels, reader scope, title policy, shared quality metadata
- `00_Config/language_playbooks/*.md`: reusable language rules when implemented
- `Deep Sea Embers/.system/config.yaml`: current pipeline execution settings
- `Deep Sea Embers/.system/providers.yaml`: provider routing and fallback chains

Novel/runtime state:

- `03_Raw/`: fetched source cache
- `04_Work/`: block, batch, glossary, QA, and formatting artifacts
- `05_Output/`: final translated Markdown product
- `06_Logs/run_ledger.jsonl`: append-only execution history
- `07_Reports/`: audits, checkpoints, handoffs, evidence

Reader state:

- `MoonRead/`: workspace-level reader app
- `MoonRead/content/generated/`: generated reader copy; disposable/regenerable
- `Deep Sea Embers/reader-web/`: compatibility stub only

## Layer Model

Layer 0: multi-novel shared policy

- registry, shared guardrails, generic Sentinel rules, MoonRead import rules

Layer 1: language playbook

- source-language risks such as title handling, pronouns, names, UI terms, sound effects, and glossary patterns

Layer 2: novel profile and vault

- per-novel glossary, pronoun policy, title policy, source-site quirks, known false positives

Layer 3: run and batch state

- run IDs, block artifacts, ledger records, recovery reports, checkpoint reports

Layer 4: reader surface

- MoonRead generated content, reader UI, publish verification, smoke tests

Rule placement:

- Fix a recurring defect at the lowest layer that catches it safely.
- Promote a rule upward only after evidence proves it is general and low false-positive risk.
- Keep story-specific voice and terminology in the novel layer.

## Main Workflow

```text
setup/fetch
  -> source validation and chapter numbering check
  -> block splitting
  -> glossary scan
  -> glossary approval
  -> literal translation
  -> refinement
  -> QA
  -> AI formatting
  -> deterministic output validation
  -> Sentinel
  -> final assembly
  -> report generation
  -> MoonRead generation
  -> scoped publish verification
```

Workflow rules:

- Bound runs by explicit chapter/block range.
- Stop on manual QA prompt, provider failure, command length failure, validation failure, Sentinel blocker/major finding, or scope expansion.
- Repair from the earliest broken stage.
- Historical failed ledger records remain; use latest-state inspection for current truth.
- Post-V6.34 production mode is bounded sequential batches with scan/glossary gates, blocking Sentinel, deterministic output guardrails, and major-run spot-checks. Broad unattended parallel translate/refine/QA remains experimental until a dedicated milestone proves ledger safety and provider isolation.

## Component Map

Pipeline CLI (`Deep Sea Embers/novel_pipeline/`):

- owns fetch, scan, translate, refine, QA, formatting, assembly, status, reports, dashboard entrypoints
- must not publish reader changes without generated-reader validation

- Provider routing: `providers.yaml` maps stages to provider/model/fallback chains; output is untrusted until parsed and validated.
- Glossary system: owns approved terms, aliases, rejected variants, and per-novel terminology policy.
- Sentinel: post-output gate over final Markdown and MoonRead generated content; run scoped by touched range for publication work.
- MoonRead: owns reader UI and generated reader content; must not mutate source, glossary, ledger, work artifacts, or final outputs.
- Reports: preserve evidence and handoff context; do not override files, tests, or current status.

## Actor / Employee Map

Employee names are dashboard/docs aliases. Ledger and config stage names remain authoritative.

| Actor | Role | Maps To |
| --- | --- | --- |
| Ferryman | setup, fetch, project entry | project setup, source adapter, preflight |
| Libra | glossary librarian | term extraction, suggestion, approval, coverage |
| Quill | literal translator | literal translation |
| Vesper | refinement editor | refinement |
| Corvus | QA judge | QA |
| Loom | format/layout worker | formatting |
| Sentinel | quality gate | post-output deterministic checks |
| Archivist | reports/output keeper | reports, final output evidence |
| Warden | recovery worker | inspect-block, rerun-block, failed block recovery |

## Provider Routing Map

Current intended production routing:

- setup/fetch: Codex / GPT-5.4 via Ferryman
- glossary scan: OpenRouter `google/gemini-3.7-flash`
- glossary option suggestion: OpenRouter `deepseek/deepseek-v4-flash-0731`
- literal translation: OpenRouter `google/gemini-3.7-flash`
- refinement: OpenRouter `deepseek/deepseek-v4-flash-0731`
- QA primary: OpenRouter `deepseek/deepseek-v4-flash-0731` with reasoning enabled
- QA fallback: OpenRouter `google/gemini-3.7-flash`; DeepSeek V4 Pro is disabled
- formatting primary: OpenRouter `deepseek/deepseek-v4-flash-0731`
- formatting fallback/cleanup: local deterministic formatter
- OpenRouter API key env var: `NOVEL_OPENROUTER_API`

Rules:

- Do not use Elephant or Nemotron for state-changing work.
- Do not use OpenRouter `deepseek/deepseek-v4-pro` in normal HGD QA routing unless a future benchmark re-approves it.
- Provider smoke tests and production route changes require explicit user approval.

## Guardrail Stack

Quality protection is layered:

1. provider output validation
2. QA stage
3. deterministic output guardrail
4. Libra glossary coverage
5. Sentinel report/gate
6. MoonRead generator validation
7. scoped MoonRead `publish:verify`
8. major-run spot-check checklist

Use scoped checks for touched ranges. Full unscoped scans can hit historical backlog and should be intentional.

## Failure And Recovery Model

- Provider failure: stop or follow configured fallback; never commit provider error/meta output.
- Command length failure: rerun with safe transport/config.
- QA hard-fail: inspect source/literal/refined/QA artifacts, rerun from earliest broken stage, and force-accept only with explicit approval.
- Formatting validation failure: rerun formatting from latest refined artifact.
- Sentinel blocker/major: stop publication, repair the full affected pattern, rerun scoped verification.
- Source numbering mismatch: stop fetch/translation, run source sequence checks, fix mapping first.
- MoonRead failure: inspect generator rejection, lint, build, and smoke output; fix final output for content issues and reader code for UI issues.

Recurring failures need cause/prevention recorded in the right document.

## New Novel Setup Flow

1. Create/open the novel vault.
2. Add a registry entry.
3. Choose the source language playbook.
4. Research the novel and save a compact profile.
5. Configure or adapt fetch logic.
6. Fetch a bounded source sample.
7. Validate source numbering and metadata.
8. Run glossary scan.
9. Approve/reject glossary terms.
10. Generate a bounded run plan.
11. Run **Libra - Pilot Gate**, the mandatory 20-chapter randomized setup experiment:
   - fetch the intended source scope into `03_Raw/` before sampling; sampling is invalid until the raw source pool exists.
   - if the source site is partially unavailable, record the verified fetchable scope first and sample only from that fetched scope.
   - sample from fetched `03_Raw/` source chapters, not only chapters that were already translated or already problematic.
   - use a recorded fixed seed so the raw-source pool and selected chapters are reproducible.
   - 10 in-sample chapters to tune pipeline behavior.
   - 10 out-of-sample chapters to prove the fixes generalize.
   - classify every fix as multi-novel, language-level, novel-level, or run-local.
   - do not scale production batches until the experiment passes its measured gates.
12. Run the first production bounded translation batch only after the experiment recommends a safe execution mode.
13. Verify output, Sentinel, reports, and MoonRead before scaling further.

## Cross-Novel Experiment Gate

Use this gate when testing whether a pipeline improvement generalizes across active novels.

- Sampling source is always `03_Raw/`, never `05_Output/`, MoonRead generated content, or only previously translated chapters.
- Audit the fetched raw-source pool before sampling. If the upstream novel has more chapters than the local raw pool, either fetch/validate the broader scope first or explicitly record the verified local scope as the experiment boundary.
- Use stratified random sampling across the verified raw range so the sample covers early, middle, late, and unseen chapters.
- Keep in-sample and out-of-sample sets separate. Tune only on in-sample; use out-of-sample as the generalization proof.
- Run treatment waves from isolated experiment vaults unless the milestone is explicitly a production run. Production `05_Output`, MoonRead generated content, and the production ledger must not be overwritten by exploratory evidence.
- Isolated experiment vaults that run Sentinel must include a local `00_Config/novel_registry.json`; runtime Sentinel must scan the experiment vault's `03_Raw` and `05_Output`, not production output or MoonRead.
- Start each treatment wave with a scan-only/glossary approval gate before translation. Translation without experiment-local glossary approval is an invalid treatment run.
- For glossary experiments, classify scan candidates before approval into approve-new, alias-to-existing, reject/noise, and ask-human/source-aware. Alias-to-existing should not create duplicate glossary notes.
- Record seed, source pool, selected chapters, commands, metrics, failures, fixes, and decisions in `01_Research_Log/` using `RESEARCH_LOG_FORMAT.md`.
- Classify every fix by layer before implementation:
  - Layer 0 multi-novel shared rule
  - Layer 1 language playbook
  - Layer 2 novel profile/vault
  - Layer 3 run-local recovery
  - Layer 4 MoonRead reader surface
- Do not publish experiment output unless a separate production publication gate approves it.

## Boundaries And Non-Goals

- `PROJECT_BRAIN.md` is current memory, not architecture.
- `IMPLEMENT_PLAN.md` is roadmap, not architecture.
- `AGENTS.md` is behavior policy, not runtime design.
- `MoonRead/content/generated/` is generated output, not source of truth.
- `06_Logs/run_ledger.jsonl` is append-only.
- `05_Output/` is final product text; treat it as product surface.
- Novel folders must not own durable cross-novel policy.
- Worker models must not rewrite canonical docs without Codex review.
- Docs-only architecture work must not call providers or run production workflows.

## Maintenance Rule

Update this file only for stable structure and ownership rules.

- Current state belongs in `PROJECT_BRAIN.md`.
- Future work belongs in `IMPLEMENT_PLAN.md`.
- Agent behavior belongs in `AGENTS.md`.
- Evidence and long incident detail belong in `07_Reports/`.
