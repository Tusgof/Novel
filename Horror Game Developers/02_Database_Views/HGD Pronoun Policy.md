# HGD Pronoun Policy

Status: active
Last updated: 2026-06-16

## Purpose

Keep Horror Game Developer Thai output consistent across chapters. This note is the Obsidian-side source of truth for pronoun handling and should be reflected in prompts, style profiles, and output guardrails.

## Core Rule

Seth Thorne narration, internal monologue, and self-referential dialogue use `ผม`.

Avoid switching Seth to `ฉัน` unless a future explicit style decision changes his voice.

## Relationship Register

- Seth self-reference: `ผม`, `ของผม`, `ตัวผม`
- Seth addressing Kyle in casual peer dialogue: usually `นาย`
- Kyle addressing Seth in casual peer dialogue: usually `นาย`
- System/UI addressing Seth or the player: `คุณ`
- Female characters may use `ฉัน` when the speaker is clearly female.
- Children may use age-appropriate forms such as `หนู` when supported by context.

## QA Rule

Flag a chapter/block when Seth's point-of-view drifts between `ผม` and `ฉัน`, or when Kyle/Seth peer dialogue flips between `นาย`, `คุณ`, and `เธอ` without a source-context reason.

## Prevention

- Refinement prompt must include this policy.
- QA prompt must check this policy.
- Published output guardrails must detect known high-risk Seth chapters that still use `ฉัน` after repair.
