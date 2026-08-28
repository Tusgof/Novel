# Immortality System Translation Policy

## Identity

- Working title: Immortality System
- Chinese title: 系统赋我长生，我熬死了所有人
- Traditional source title: 系統賦我長生，我熬死了所有人
- Author: 一只榴莲3号
- Source language: Chinese
- Target language: Thai
- Style profile: xianxia_wuxia

## Voice And Register

- Use elevated but readable Thai suitable for cultivation fantasy.
- Preserve the protagonist's patient, observant perspective and long historical scale.
- Keep cultivation concepts distinct from ordinary fantasy terms.
- Avoid modern slang unless it is present in the source.

## Terminology

- Record named characters, sects, clans, locations, realms, techniques, artifacts,
  titles, and recurring system terms in `01_Glossary/`.
- Use one approved Thai term consistently once it is accepted.
- Keep transliteration for proper names and translation for descriptive concepts.
- Do not create notes for ordinary one-off words or full sentences.

## Source And Provenance

- Dek-D is the identification/reference page only.
- Fanqie is the confirmed original/publication reference.
- Novel543 is the selected fetch source because its TOC exposes a contiguous 2,570
  chapter range and its paginated chapter extraction was verified.
- Novel543 is an aggregator/mirror; provenance is not independently verified.

## Setup Gate

1. Fetch and validate the intended raw source scope in `03_Raw/`.
2. Run source sequence, title, duplicate, empty-body, and extraction checks.
3. Run Libra - Pilot Gate from raw source: 20 random chapters with a recorded seed,
   split into 10 in-sample and 10 out-of-sample chapters.
4. Keep pilot artifacts isolated from production output and MoonRead.
5. Start production only after the pilot has a measured recommendation.
