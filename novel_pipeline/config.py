from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import yaml

from novel_pipeline.providers.base import build_provider_spec, default_provider_specs
from novel_pipeline.types import (
    AppConfig,
    BatchDefaults,
    ChunkingPolicy,
    ProviderSpec,
    ResearchProfile,
    SourceConfig,
    StageRouting,
    StyleProfile,
    WorkspacePaths,
)


class ConfigError(RuntimeError):
    pass


def load_yaml_mapping(path: Path | str, *, required: bool = False) -> dict[str, Any]:
    target = Path(path)
    if not target.exists():
        if required:
            raise ConfigError(f"Config file not found: {target}")
        return {}
    raw = target.read_text(encoding="utf-8")
    if not raw.strip():
        return {}
    payload = yaml.safe_load(raw)
    if payload is None:
        return {}
    if not isinstance(payload, Mapping):
        raise ConfigError(f"Expected mapping in YAML file: {target}")
    return {str(key): value for key, value in payload.items()}


def _workspace_root_from_config_path(config_path: Path) -> Path:
    parent = config_path.parent
    if parent.name == ".system":
        return parent.parent.resolve()
    return parent.resolve()


def _resolve_relative(root: Path, value: Any) -> Path:
    candidate = Path(str(value))
    if not candidate.is_absolute():
        candidate = (root / candidate).resolve()
    return candidate


def _parse_stage_routing(data: Mapping[str, Any]) -> dict[str, StageRouting]:
    routing_section = data.get("routing")
    if routing_section is None:
        routing_section = {
            key: value
            for key, value in data.items()
            if key not in {"providers", "default"}
        }
    if not isinstance(routing_section, Mapping):
        raise ConfigError("providers.yaml routing section must be a mapping.")
    routing: dict[str, StageRouting] = {}
    for stage, value in routing_section.items():
        routing[str(stage)] = StageRouting.from_mapping(str(stage), value)
    return routing


def _parse_provider_specs(data: Mapping[str, Any], *, base_dir: Path) -> dict[str, ProviderSpec]:
    providers_section = data.get("providers")
    if providers_section is None:
        return default_provider_specs()
    if not isinstance(providers_section, Mapping):
        raise ConfigError("providers.yaml providers section must be a mapping.")
    defaults = default_provider_specs()
    specs: dict[str, ProviderSpec] = {}
    for provider_name, value in providers_section.items():
        provider_key = str(provider_name)
        if isinstance(value, Mapping):
            merged = dict(defaults.get(provider_key, ProviderSpec(name=provider_key, executable=(provider_key,))).to_dict())
            merged.update({str(key): item for key, item in value.items()})
            specs[provider_key] = ProviderSpec.from_mapping(provider_key, merged, base_dir=base_dir)
        else:
            specs[provider_key] = build_provider_spec(provider_key, base_dir=base_dir)
    for provider_key, spec in defaults.items():
        specs.setdefault(provider_key, spec)
    return specs


def _parse_style_profiles(data: Mapping[str, Any]) -> dict[str, StyleProfile]:
    profiles: dict[str, StyleProfile] = {}
    for key, value in data.items():
        if isinstance(value, Mapping):
            profiles[str(key)] = StyleProfile.from_mapping(str(key), value)
    return profiles


def _parse_research_profile(path: Path) -> ResearchProfile | None:
    if not path.exists():
        return None
    payload = load_yaml_mapping(path)
    try:
        return ResearchProfile.from_mapping(payload)
    except ValueError as exc:
        raise ConfigError(f"Invalid research profile: {exc}") from exc


def load_app_config(config_path: Path | str = Path(".system/config.yaml")) -> AppConfig:
    target = Path(config_path).expanduser().resolve()
    if not target.exists():
        raise ConfigError(f"Main config file not found: {target}")

    workspace_root = _workspace_root_from_config_path(target)
    workspace = WorkspacePaths.from_root(workspace_root)

    config_doc = load_yaml_mapping(target, required=True)
    system_root = target.parent
    providers_doc = load_yaml_mapping(system_root / "providers.yaml")
    styles_doc = load_yaml_mapping(system_root / "style_profiles.yaml")
    research_profile = _parse_research_profile(workspace_root / "RESEARCH_PROFILE.yaml")

    novel_id = str(config_doc.get("novel_id", workspace_root.name)).strip() or workspace_root.name
    vault_root = _resolve_relative(workspace_root, config_doc.get("vault_root", "."))
    source_language = str(config_doc.get("source_language", "zh")).strip() or "zh"
    default_style_profile = str(config_doc.get("default_style_profile", "default")).strip() or "default"

    batch_payload = config_doc.get("batch")
    if not isinstance(batch_payload, Mapping):
        batch_payload = config_doc
    batch = BatchDefaults.from_mapping(batch_payload)
    chunking = ChunkingPolicy.from_mapping(config_doc.get("chunking") if isinstance(config_doc.get("chunking"), Mapping) else None)

    source_section = config_doc.get("source")
    if isinstance(source_section, Mapping):
        source_cfg = SourceConfig(
            adapter=str(source_section.get("adapter", "")),
            toc_url=str(source_section.get("toc_url", "")),
            base_url=str(source_section.get("base_url", "")),
            delay_seconds=float(source_section.get("delay_seconds", 1.0)),
            encoding=str(source_section.get("encoding", "")),
            extra={str(k): v for k, v in source_section.items()
                   if k not in ("adapter", "toc_url", "base_url", "delay_seconds", "encoding")},
        )
    else:
        source_cfg = SourceConfig()

    style_profiles = _parse_style_profiles(styles_doc)
    if not style_profiles:
        style_profiles = {
            "default": StyleProfile(key="default", name="default", description="Neutral polished Thai prose.")
        }

    providers = _parse_provider_specs(providers_doc, base_dir=system_root)
    stage_routing = _parse_stage_routing(providers_doc)

    _validate_config(
        config_path=target,
        workspace=workspace,
        novel_id=novel_id,
        source_language=source_language,
        default_style_profile=default_style_profile,
        providers=providers,
        stage_routing=stage_routing,
        style_profiles=style_profiles,
    )

    return AppConfig(
        config_path=target,
        workspace=workspace,
        novel_id=novel_id,
        vault_root=vault_root,
        source_language=source_language,
        default_style_profile=default_style_profile,
        batch=batch,
        chunking=chunking,
        research_profile=research_profile,
        source=source_cfg,
        providers=providers,
        stage_routing=stage_routing,
        style_profiles=style_profiles,
        raw_config=config_doc,
    )


def _validate_config(
    *,
    config_path: Path,
    workspace: WorkspacePaths,
    novel_id: str,
    source_language: str,
    default_style_profile: str,
    providers: Mapping[str, ProviderSpec],
    stage_routing: Mapping[str, StageRouting],
    style_profiles: Mapping[str, StyleProfile],
) -> None:
    if not config_path.exists():
        raise ConfigError(f"Config path does not exist: {config_path}")
    if not novel_id:
        raise ConfigError("novel_id cannot be empty.")
    if not source_language:
        raise ConfigError("source_language cannot be empty.")
    if default_style_profile and default_style_profile not in style_profiles:
        raise ConfigError(f"Default style profile '{default_style_profile}' is missing from style_profiles.yaml.")
    for stage, routing in stage_routing.items():
        if not routing.provider:
            raise ConfigError(f"Stage '{stage}' does not define a provider.")
        if routing.provider not in providers:
            raise ConfigError(f"Stage '{stage}' references unknown provider '{routing.provider}'.")
        if routing.fallback_provider and routing.fallback_provider not in providers:
            raise ConfigError(f"Stage '{stage}' references unknown fallback provider '{routing.fallback_provider}'.")
        for fallback in routing.fallbacks:
            fallback_provider = fallback.get("provider", "")
            if fallback_provider and fallback_provider not in providers:
                raise ConfigError(f"Stage '{stage}' references unknown fallback provider '{fallback_provider}'.")
    if not workspace.root.exists():
        raise ConfigError(f"Workspace root does not exist: {workspace.root}")


load_workspace_config = load_app_config


__all__ = [
    "ConfigError",
    "load_app_config",
    "load_workspace_config",
    "load_yaml_mapping",
]
