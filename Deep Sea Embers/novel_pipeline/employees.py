from __future__ import annotations

from typing import Any

from novel_pipeline.types import AppConfig


EMPLOYEE_ROSTER: tuple[dict[str, Any], ...] = (
    {
        "code": "000",
        "name": "Ferryman",
        "archetype": "คนพาข้ามฝั่ง / ผู้นำทางเข้าท่า",
        "role": "setup, fetch, new project entry",
        "maps_to": ("init-novel", "fetch/source adapter", "project setup", "preflight"),
        "stages": ("project_setup", "fetch", "fetched"),
        "actions": ("init-novel", "project-setup", "run-batch:glossary-scan", "preflight"),
    },
    {
        "code": "001",
        "name": "Libra",
        "archetype": "บรรณารักษ์หญิง",
        "role": "glossary librarian",
        "maps_to": ("term extraction", "term suggestion", "glossary queue", "approve/reject"),
        "stages": ("term_extraction", "term_suggestion", "glossary_scanned", "glossary_approved"),
        "actions": ("glossary-decision",),
    },
    {
        "code": "002",
        "name": "Quill",
        "archetype": "นักจดถ้อยคำ",
        "role": "literal translator",
        "maps_to": ("literal_translation",),
        "stages": ("literal_translation", "translating"),
        "actions": (),
    },
    {
        "code": "003",
        "name": "Vesper",
        "archetype": "บรรณาธิการยามค่ำ",
        "role": "refinement editor",
        "maps_to": ("refinement",),
        "stages": ("refinement", "refining"),
        "actions": (),
    },
    {
        "code": "004",
        "name": "Corvus",
        "archetype": "ผู้ตรวจคำสาบาน",
        "role": "QA judge",
        "maps_to": ("qa_judge",),
        "stages": ("qa_judge", "qa"),
        "actions": (),
    },
    {
        "code": "005",
        "name": "Loom",
        "archetype": "ช่างเรียงรูปเล่ม",
        "role": "formatting/layout worker",
        "maps_to": ("formatting",),
        "stages": ("formatting",),
        "actions": (),
    },
    {
        "code": "006",
        "name": "Archivist",
        "archetype": "ผู้เฝ้าหอจดหมายเหตุ",
        "role": "reports/output keeper",
        "maps_to": ("reports", "final output", "cleanliness/product review"),
        "stages": ("completed",),
        "actions": ("report",),
    },
    {
        "code": "007",
        "name": "Warden",
        "archetype": "ผู้คุมประตูฉุกเฉิน",
        "role": "recovery worker",
        "maps_to": ("inspect-block", "rerun-block", "failed block recovery"),
        "stages": ("rerun-block",),
        "actions": ("inspect-block", "rerun-block"),
    },
)


def employee_for_stage(stage: str) -> dict[str, Any] | None:
    normalized = stage.strip()
    for employee in EMPLOYEE_ROSTER:
        if normalized in employee["stages"] or normalized in employee["actions"]:
            return employee
    return None


def _route_label(config: AppConfig, stage: str) -> str:
    try:
        routing = config.stage_routing_for(stage)
    except KeyError:
        return "local"
    primary = f"{routing.provider}/{routing.model or config.providers[routing.provider].default_model or 'default'}"
    fallbacks = [
        f"{item.get('provider', '')}/{item.get('model', '') or 'default'}"
        for item in routing.fallbacks
        if item.get("provider")
    ]
    if fallbacks:
        return primary + " -> " + " -> ".join(fallbacks)
    return primary


def employee_provider_label(config: AppConfig, employee: dict[str, Any]) -> str:
    route_stages = [stage for stage in employee["stages"] if stage in config.stage_routing]
    if not route_stages:
        return "local"
    return " | ".join(_route_label(config, stage) for stage in route_stages)


__all__ = ["EMPLOYEE_ROSTER", "employee_for_stage", "employee_provider_label"]
