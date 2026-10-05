---
name: novel-verify
description: Verify Novel workspace work on its real surfaces — translated chapter output, the Sentinel quality gate, and the MoonRead reader — and navigate the workspace's features through its Feature Map. Use before claiming any translation, repair, glossary, setup, or MoonRead publication work is done, or when you need to know how a Novel feature is reached and driven.
---

# Novel verification

Tests passing is not "verified" here. A chapter is verified when its final output exists, passes the output guardrails and Sentinel for the touched scope, and — when it is meant for readers — renders through MoonRead's `publish:verify`.

## First, find the feature

Open [`references/features/README.md`](references/features/README.md). It lists every feature, how the owner asks for it, the command that drives it, and its gotchas. Read only the feature file you need.

## Always

1. Pick the novel explicitly: every pipeline command takes `--config "<Novel Folder>/.system/config.yaml"`.
2. Run `preflight` first. Fix anything under **Blocking** before provider calls.
3. Use `--dry-run` where a command offers it before the first real run.
4. Verify on the surface the work lands on (see each feature's **Verify**), then report each claim as measured, inferred, or guessed.

## Stop and report instead of continuing

A manual prompt, a QA hard-fail, a provider failure, a Sentinel blocker or major finding, or scope drift. Never force-accept QA or Sentinel results (see `NOVEL_OPERATOR_GUIDE.md`).

## Maintaining this skill

When a command, flag, path, or gotcha changes, update the matching feature file in the same change. `python tools/yuehua.py doctor` from the Yuehua Kit fails the map when it names a path that no longer exists.
