# Design Guide: Novel Operator Dashboard

Purpose: keep the local dashboard practical, readable, and safe for daily translation control. This file is the source of truth for dashboard UI/UX decisions.

## Product Principle

The dashboard exists to help one operator answer four questions quickly:

- What run am I working on?
- Is anything blocked?
- What is the next safe action?
- Which worker/stage is responsible for the current task?

Do not turn the dashboard into documentation, a marketing page, or a decorative card wall.

## Visual Direction

- Use a clear, friendly, restrained style inspired by Wise-style product dashboards.
- Green is reserved for ready, success, completed, and positive states.
- Blue is reserved for primary actions and links.
- Yellow is reserved for warnings and bounded-only caution.
- Red is reserved for blocked, failed, destructive, or urgent states.
- Use neutral surfaces, readable contrast, and subtle borders.
- Avoid decorative gradients, floating orbs, hero sections, and visual noise.

## Layout Rules

- First viewport must show current run, blocker, next safe action, and the active task surface.
- Group controls by task, not by internal implementation detail.
- Keep one primary action visible for the current task when possible.
- Put technical detail, command previews, audit fields, and raw diagnostics behind details or secondary panels.
- Use consistent 4px/8px spacing increments.
- Related label/input/action elements stay close together; unrelated sections get larger gaps.
- Cards are allowed for repeated items such as employee cards, report links, glossary candidates, and chapter summaries.
- Do not put cards inside cards unless the inner object is a genuinely repeated item.

## Typography

- Use one sans-serif family.
- Dashboard headings should stay compact; avoid oversized marketing typography.
- Keep body text short and scannable.
- Prefer labels and state chips over explanatory paragraphs.
- Do not rely on long instructions to make controls understandable.

## Component States

Every interactive element must show clear state:

- buttons: default, hover, active/pressed, disabled, loading when needed
- inputs: default, focused, error
- navigation: inactive and active
- status chips: ready, warning, blocked, unknown
- long actions: current employee, action/stage, provider/model, elapsed time, waiting/retry/fallback state, and last safe log line

## Employee Cards

Employee cards are display aliases only. They must never hide audit data.

Each employee card should show:

- code and character name
- short role description
- real mapped stage/action
- provider/model route when applicable
- readiness
- latest activity or no-activity state
- chibi asset when available

The chibi art supports recognition and warmth, but the operational text remains the source of truth.

## Safety And Auditability

- Read-only dashboard load must not call live providers.
- Provider smoke tests must be explicit user-triggered actions.
- State-changing actions must show exact scope before execution.
- Internal stage/provider/model names remain available for audit.
- Dashboard labels can be friendly, but reports and ledgers must stay exact.

## Copy Rules

- Remove helper text when the label already explains the control.
- Use one short sentence only when a mistake is likely without it.
- Prefer "Continue", "Review glossary", "Recover block", and "Generate report" over raw command names in primary UI.
- Keep raw command names in previews/details where auditability matters.

## Asset Rules

- Project-bound dashboard images live under `assets/dashboard/`.
- Generated art must not be required for pipeline execution.
- If an image is missing, the dashboard must still render with text state.
- Avoid text inside generated character art; UI text is rendered by HTML.
