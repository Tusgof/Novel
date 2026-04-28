from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import Any

import yaml

from novel_pipeline.files import atomic_write_text
from novel_pipeline.types import AppConfig, NovelProfile, ResearchProfile, utc_now_iso


def slugify_novel_id(value: str) -> str:
    compact = "".join(ch.lower() if ch.isalnum() else "-" for ch in value.strip())
    while "--" in compact:
        compact = compact.replace("--", "-")
    return compact.strip("-")


def _normalize_style_profile_key(value: str) -> str:
    compact = value.strip().lower().replace("-", "_").replace("/", "_")
    compact = re.sub(r"[^a-z0-9_]+", "_", compact)
    compact = re.sub(r"_+", "_", compact)
    return compact.strip("_")


def _resolve_style_profile_key(
    *,
    template_config: AppConfig,
    genre: str,
    explicit_style_profile: str,
) -> str:
    explicit = explicit_style_profile.strip()
    if explicit:
        return explicit

    genre_key = _normalize_style_profile_key(genre)
    if not genre_key:
        return template_config.default_style_profile

    genre_aliases = {
        "dark_fantasy": "dark_fantasy",
        "deep_sea_embers": "deep_sea_embers",
        "horror": "horror",
        "modern_urban": "modern_urban",
        "romance_drama": "romance_drama",
        "sci_fi": "sci_fi",
        "science_fiction": "sci_fi",
        "xianxia": "xianxia_wuxia",
        "xianxia_wuxia": "xianxia_wuxia",
        "wuxia": "xianxia_wuxia",
    }
    resolved = genre_aliases.get(genre_key, genre_key)
    if resolved in template_config.style_profiles:
        return resolved
    if genre_key in template_config.style_profiles:
        return genre_key
    return template_config.default_style_profile


def build_novel_profile(
    *,
    novel_id: str,
    title: str,
    aliases: list[str] | tuple[str, ...] | None = None,
    source_language: str,
    target_language: str,
    genre: str,
    style_profile: str,
    source_adapter: str,
    source_toc_url: str,
    created_from_workspace: Path,
) -> NovelProfile:
    cleaned_aliases = tuple(alias.strip() for alias in (aliases or []) if alias.strip())
    return NovelProfile(
        novel_id=novel_id,
        title=title.strip(),
        aliases=cleaned_aliases,
        source_language=source_language.strip(),
        target_language=target_language.strip(),
        genre=genre.strip(),
        style_profile=style_profile.strip(),
        source_adapter=source_adapter.strip(),
        source_toc_url=source_toc_url.strip(),
        metadata={
            "schema_version": 1,
            "created_at": utc_now_iso(),
            "created_from_workspace": str(created_from_workspace),
            "research_profile_status": "pending",
        },
    )


def build_research_profile(
    *,
    title: str,
    source_url: str,
    aliases: list[str] | tuple[str, ...] | None = None,
) -> ResearchProfile:
    return ResearchProfile(
        title=title.strip(),
        source_url=source_url.strip(),
        aliases=tuple(alias.strip() for alias in (aliases or []) if alias.strip()),
        status="pending",
    )


def render_novel_profile_yaml(profile: NovelProfile) -> str:
    payload: dict[str, Any] = {
        "schema_version": int(profile.metadata.get("schema_version", 1)),
        "novel_id": profile.novel_id,
        "title": profile.title,
        "aliases": list(profile.aliases),
        "languages": {
            "source": profile.source_language,
            "target": profile.target_language,
        },
        "genre": profile.genre,
        "style_profile": profile.style_profile,
        "source": {
            "adapter": profile.source_adapter,
            "toc_url": profile.source_toc_url,
        },
        "research": {
            "status": str(profile.metadata.get("research_profile_status", "pending")),
            "profile_path": "RESEARCH_PROFILE.yaml",
            "title": profile.title,
            "source_url": profile.source_toc_url,
        },
        "setup": {
            "created_at": str(profile.metadata.get("created_at", "")),
            "created_from_workspace": str(profile.metadata.get("created_from_workspace", "")),
        },
        "notes": profile.notes,
    }
    return yaml.safe_dump(payload, allow_unicode=True, sort_keys=False)


def render_research_profile_yaml(profile: ResearchProfile) -> str:
    payload: dict[str, Any] = {
        "schema_version": 1,
        "title": profile.title,
        "aliases": list(profile.aliases),
        "source_url": profile.source_url,
        "status": profile.status,
        "synopsis": profile.synopsis,
        "tags": list(profile.tags),
        "style_notes": profile.style_notes,
        "reader_expectations": profile.reader_expectations,
        "review_summary": profile.review_summary,
        "terminology": list(profile.terminology),
        "reference_links": list(profile.reference_links),
        "notes": profile.notes,
    }
    return yaml.safe_dump(payload, allow_unicode=True, sort_keys=False)


def _copy_tree(src: Path, dest: Path) -> None:
    if not src.exists():
        return
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(src, dest)


def _rewrite_providers_payload(
    providers_payload: dict[str, Any],
    *,
    source_workspace_root: Path,
    target_workspace_root: Path,
) -> dict[str, Any]:
    rewritten = yaml.safe_load(yaml.safe_dump(providers_payload, allow_unicode=True, sort_keys=False)) or {}
    providers = rewritten.get("providers")
    if not isinstance(providers, dict):
        return rewritten
    codex = providers.get("codex")
    if not isinstance(codex, dict):
        return rewritten
    extra_args = codex.get("extra_args")
    if not isinstance(extra_args, list):
        return rewritten
    source_root_str = str(source_workspace_root)
    target_root_str = str(target_workspace_root)
    codex["extra_args"] = [
        target_root_str if str(item) == source_root_str else item
        for item in extra_args
    ]
    return rewritten


def initialize_novel_project(
    *,
    template_config: AppConfig,
    project_root: Path,
    title: str,
    source_url: str,
    novel_id: str | None = None,
    aliases: list[str] | tuple[str, ...] | None = None,
    source_language: str = "zh",
    target_language: str = "th",
    genre: str = "",
    adapter: str = "",
    style_profile: str = "",
) -> dict[str, Path]:
    if not title.strip():
        raise ValueError("title cannot be empty.")
    if not source_url.strip():
        raise ValueError("source_url cannot be empty.")

    target_root = Path(project_root).expanduser().resolve()
    if target_root.exists():
        if any(target_root.iterdir()):
            raise ValueError(f"project_root must be empty: {target_root}")
    else:
        target_root.mkdir(parents=True, exist_ok=True)

    resolved_novel_id = (novel_id or slugify_novel_id(title)).strip()
    if not resolved_novel_id:
        raise ValueError("novel_id cannot be empty after normalization.")

    source_workspace = template_config.workspace.root
    resolved_style_profile = _resolve_style_profile_key(
        template_config=template_config,
        genre=genre,
        explicit_style_profile=style_profile,
    )
    source_system = source_workspace / ".system"
    target_system = target_root / ".system"
    target_system.mkdir(parents=True, exist_ok=True)

    providers_payload = yaml.safe_load((source_system / "providers.yaml").read_text(encoding="utf-8")) or {}
    rewritten_providers = _rewrite_providers_payload(
        providers_payload,
        source_workspace_root=source_workspace,
        target_workspace_root=target_root,
    )
    atomic_write_text(
        target_system / "providers.yaml",
        yaml.safe_dump(rewritten_providers, allow_unicode=True, sort_keys=False),
    )
    atomic_write_text(
        target_system / "style_profiles.yaml",
        (source_system / "style_profiles.yaml").read_text(encoding="utf-8"),
    )

    config_payload: dict[str, Any] = {
        "novel_id": resolved_novel_id,
        "vault_root": ".",
        "source_language": source_language.strip() or template_config.source_language,
        "default_batch_size": template_config.batch.default_batch_size,
        "chapter_unit": template_config.batch.chapter_unit,
        "default_style_profile": resolved_style_profile,
        "chunking": {
            "chinese_character_limit": template_config.chunking.chinese_character_limit,
            "non_chinese_word_limit": template_config.chunking.non_chinese_word_limit,
        },
        "source": {
            "adapter": adapter.strip() or template_config.source.adapter,
            "toc_url": source_url.strip(),
            "delay_seconds": template_config.source.delay_seconds,
            "encoding": template_config.source.encoding,
        },
    }
    atomic_write_text(
        target_system / "config.yaml",
        yaml.safe_dump(config_payload, allow_unicode=True, sort_keys=False),
    )

    _copy_tree(source_workspace / "prompts", target_root / "prompts")
    _copy_tree(source_workspace / "00_Templates", target_root / "00_Templates")

    for relative_dir in (
        "01_Glossary",
        "02_Database_Views",
        "03_Raw",
        "04_Work",
        "05_Output",
        "06_Logs",
        "07_Reports",
        "skills",
    ):
        (target_root / relative_dir).mkdir(parents=True, exist_ok=True)

    profile = build_novel_profile(
        novel_id=resolved_novel_id,
        title=title,
        aliases=aliases,
        source_language=source_language.strip() or template_config.source_language,
        target_language=target_language.strip() or "th",
        genre=genre,
        style_profile=resolved_style_profile,
        source_adapter=adapter.strip() or template_config.source.adapter,
        source_toc_url=source_url,
        created_from_workspace=source_workspace,
    )
    atomic_write_text(target_root / "NOVEL_PROFILE.yaml", render_novel_profile_yaml(profile))

    research_profile = build_research_profile(
        title=title,
        source_url=source_url,
        aliases=aliases,
    )
    atomic_write_text(target_root / "RESEARCH_PROFILE.yaml", render_research_profile_yaml(research_profile))

    return {
        "project_root": target_root,
        "config_path": target_system / "config.yaml",
        "profile_path": target_root / "NOVEL_PROFILE.yaml",
        "research_profile_path": target_root / "RESEARCH_PROFILE.yaml",
    }


__all__ = [
    "build_novel_profile",
    "build_research_profile",
    "initialize_novel_project",
    "render_novel_profile_yaml",
    "render_research_profile_yaml",
    "slugify_novel_id",
]
