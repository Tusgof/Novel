# Novel Setup Playbook

Use this playbook when creating a new novel project. The goal is to create a runnable project folder without code edits and without guessing.

## Required Inputs From The User

Do not start setup until these are provided:

- primary novel title
- alternate titles if they exist
- primary source TOC or index URL used for fetch
- source language
- target language
- initial genre label

Minimum required fields:

- `title`
- `source_url`

If either is missing, setup is incomplete.

## Output Of This Playbook

A new project folder with:

- `.system/config.yaml`
- `.system/providers.yaml`
- `.system/style_profiles.yaml`
- `NOVEL_PROFILE.yaml`
- `RESEARCH_PROFILE.yaml`
- copied `prompts/`
- copied `00_Templates/`
- empty isolated state folders:
  - `01_Glossary/`
  - `02_Database_Views/`
  - `03_Raw/`
  - `04_Work/`
  - `05_Output/`
  - `06_Logs/`
  - `07_Reports/`
  - `skills/`

## Step 1: Confirm The Novel Identity

Record:

- primary title
- aliases
- intended `novel_id`
- source language
- target language
- genre

Rules:

- `novel_id` should be stable and filesystem-safe
- aliases should contain Chinese/English/alternate names when known
- do not rely on one chapter name as the novel identity

## Step 2: Confirm The Fetch Source

Before scaffolding, inspect the source site:

- TOC/index page exists
- chapter links are visible in HTML or predictable
- no obvious anti-bot block on first load
- encoding looks recoverable
- chapter body appears extractable from static HTML

If any of these fail, stop and decide whether:

- an existing adapter still works with custom cleanup
- a new adapter is required
- the source is unsuitable

## Step 3: Scaffold The Project

Run from the current working pipeline workspace:

```powershell
cd "D:\Fogust\Workspace\Novel\Deep Sea Embers"
$env:PYTHONIOENCODING='utf-8'
novel-pipeline --config ".system/config.yaml" init-novel `
  --project-root "D:\Fogust\Workspace\Novel\<New Project Folder>" `
  --title "<Primary Title>" `
  --source-url "<TOC URL>" `
  --novel-id "<novel-id>" `
  --alias "<Alt Title 1>" `
  --alias "<Alt Title 2>" `
  --source-language zh `
  --target-language th `
  --genre "<genre>" `
  --adapter "<adapter>" `
  --style-profile "<style_profile>"
```

Expected result:

- project folder exists
- `NOVEL_PROFILE.yaml` exists
- config path points to the new project
- provider/style files were copied
- prompts/templates were copied

## Step 4: Inspect The New Profile

Open and confirm:

- `NOVEL_PROFILE.yaml`
- `RESEARCH_PROFILE.yaml`
- `.system/config.yaml`

Required checks:

- `novel_id` is correct
- `title` is correct
- aliases are present if known
- `source.adapter` is correct
- `source.toc_url` is correct
- `style_profile` matches the intended genre baseline

## Step 5: Validate The Config Loads

Run:

```powershell
python -c "from novel_pipeline.config import load_app_config; cfg = load_app_config(r'D:\Fogust\Workspace\Novel\<New Project Folder>\.system\config.yaml'); print(cfg.novel_id); print(cfg.workspace.root)"
```

The config must load without code edits.

## Step 6: Validate Source Feasibility

Use the new config path:

```powershell
novel-pipeline --config "D:\Fogust\Workspace\Novel\<New Project Folder>\.system\config.yaml" fetch --adapter "<adapter>"
```

Expected:

- manifest builds or prints sample chapter list
- no mojibake obvious in titles
- chapter IDs are assigned

If this fails, stop and move to the fetch adapter playbook.

## Step 7: Fetch One Sample Chapter

Pick one chapter and run:

```powershell
novel-pipeline --config "D:\Fogust\Workspace\Novel\<New Project Folder>\.system\config.yaml" fetch --adapter "<adapter>" --chapter-id ch001
```

Then inspect:

- `03_Raw/ch001/source.json`

Required checks:

- source text is the real chapter body
- no title/body swap
- no obvious nav/ad dump
- encoding is correct
- body language matches the declared source language

## Step 8: Decide Whether The Project Is Ready

Ready for glossary scan only when all of these are true:

- config loads cleanly
- manifest builds
- sample chapter fetches
- source text is readable and clean enough to split
- `RESEARCH_PROFILE.yaml` exists and is ready for the first manual research pass
- operator follows `RESEARCH_PROFILE_PLAYBOOK.md` before relying on one chapter as style evidence

If not, do not start translation. Fix the adapter or source assumptions first.

## Stop Conditions

Stop setup immediately if:

- title or source URL is missing
- config does not load
- fetch source appears dynamic or blocked
- manifest is wrong or incomplete
- chapter body extraction is noisy or empty
- encoding is not recoverable

## Acceptance

Setup is accepted only when:

- the new project exists as an isolated folder
- the project config loads with the existing pipeline code
- a sample manifest can be built
- a sample chapter can be fetched and inspected
- no code edits were needed for the new novel itself
