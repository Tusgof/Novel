from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def as_string_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, tuple):
        return tuple(str(item) for item in value)
    if isinstance(value, list):
        return tuple(str(item) for item in value)
    if isinstance(value, set):
        return tuple(str(item) for item in sorted(value, key=str))
    if isinstance(value, str):
        return (value,)
    return (str(value),)


def as_string_or_empty(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def json_safe(value: Any) -> Any:
    if is_dataclass(value):
        return json_safe(asdict(value))
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat()
    if isinstance(value, Mapping):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [json_safe(item) for item in value]
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    if isinstance(value, set):
        return [json_safe(item) for item in sorted(value, key=str)]
    return value


class JsonSerializable:
    def to_dict(self) -> dict[str, Any]:
        return json_safe(asdict(self))


@dataclass(slots=True)
class WorkspacePaths(JsonSerializable):
    root: Path
    config_dir: Path
    templates_dir: Path
    glossary_dir: Path
    database_views_dir: Path
    raw_dir: Path
    work_dir: Path
    output_dir: Path
    logs_dir: Path
    prompts_dir: Path
    skills_dir: Path
    system: Path
    prompts: Path
    templates: Path
    glossary: Path
    database_views: Path
    raw: Path
    work: Path
    output: Path
    logs: Path

    @classmethod
    def from_root(cls, root: Path | str) -> WorkspacePaths:
        root_path = Path(root).expanduser().resolve()
        config_dir = root_path / ".system"
        templates_dir = root_path / "00_Templates"
        glossary_dir = root_path / "01_Glossary"
        database_views_dir = root_path / "02_Database_Views"
        raw_dir = root_path / "03_Raw"
        work_dir = root_path / "04_Work"
        output_dir = root_path / "05_Output"
        logs_dir = root_path / "06_Logs"
        prompts_dir = root_path / "prompts"
        skills_dir = root_path / "skills"
        return cls(
            root=root_path,
            config_dir=config_dir,
            templates_dir=templates_dir,
            glossary_dir=glossary_dir,
            database_views_dir=database_views_dir,
            raw_dir=raw_dir,
            work_dir=work_dir,
            output_dir=output_dir,
            logs_dir=logs_dir,
            prompts_dir=prompts_dir,
            skills_dir=skills_dir,
            system=config_dir,
            prompts=prompts_dir,
            templates=templates_dir,
            glossary=glossary_dir,
            database_views=database_views_dir,
            raw=raw_dir,
            work=work_dir,
            output=output_dir,
            logs=logs_dir,
        )


@dataclass(slots=True)
class ChunkingPolicy(JsonSerializable):
    chinese_character_limit: int = 2500
    non_chinese_word_limit: int = 5000

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any] | None) -> ChunkingPolicy:
        payload = dict(data or {})
        return cls(
            chinese_character_limit=int(
                payload.get("chinese_character_limit", payload.get("chinese_characters", 2500))
            ),
            non_chinese_word_limit=int(
                payload.get("non_chinese_word_limit", payload.get("latin_word_limit", 5000))
            ),
        )


@dataclass(slots=True)
class BatchDefaults(JsonSerializable):
    default_batch_size: int = 10
    chapter_unit: str = "chapters"

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any] | None) -> BatchDefaults:
        payload = dict(data or {})
        return cls(
            default_batch_size=int(payload.get("default_batch_size", 10)),
            chapter_unit=str(payload.get("chapter_unit", "chapters")),
        )


@dataclass(slots=True)
class ExecutionPolicy(JsonSerializable):
    concurrency_enabled: bool = False
    stop_on_first_hard_failure: bool = True
    stage_concurrency: dict[str, int] = field(default_factory=dict)
    artifact_cache_mode: str = "report_only"
    artifact_cache_stages: tuple[str, ...] = ()
    pre_qa_guardrail_mode: str = "report_only"
    pre_qa_dense_paragraph_warning_chars: int = 900
    sentinel_mode: str = "report_only"
    sentinel_fail_on: str = "major"

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any] | None) -> ExecutionPolicy:
        payload = dict(data or {})
        raw_stage_concurrency = payload.get("stage_concurrency")
        stage_concurrency: dict[str, int] = {}
        if isinstance(raw_stage_concurrency, Mapping):
            for stage, value in raw_stage_concurrency.items():
                limit = max(1, int(value))
                stage_concurrency[str(stage)] = limit
        cache_payload = payload.get("artifact_cache")
        if not isinstance(cache_payload, Mapping):
            cache_payload = {}
        cache_mode = str(cache_payload.get("mode", payload.get("artifact_cache_mode", "report_only"))).strip().lower()
        if cache_mode not in {"off", "report_only", "enabled"}:
            raise ValueError("artifact_cache mode must be one of: off, report_only, enabled")
        pre_qa_payload = payload.get("pre_qa_guardrail")
        if not isinstance(pre_qa_payload, Mapping):
            pre_qa_payload = {}
        pre_qa_mode = str(pre_qa_payload.get("mode", payload.get("pre_qa_guardrail_mode", "report_only"))).strip().lower()
        if pre_qa_mode not in {"off", "report_only", "blocking"}:
            raise ValueError("pre_qa_guardrail mode must be one of: off, report_only, blocking")
        sentinel_payload = payload.get("sentinel")
        if not isinstance(sentinel_payload, Mapping):
            sentinel_payload = {}
        sentinel_mode = str(sentinel_payload.get("mode", payload.get("sentinel_mode", "report_only"))).strip().lower()
        if sentinel_mode not in {"off", "report_only", "blocking"}:
            raise ValueError("sentinel mode must be one of: off, report_only, blocking")
        sentinel_fail_on = str(sentinel_payload.get("fail_on", payload.get("sentinel_fail_on", "major"))).strip().lower()
        if sentinel_fail_on not in {"blocker", "major", "minor"}:
            raise ValueError("sentinel fail_on must be one of: blocker, major, minor")
        return cls(
            concurrency_enabled=bool(payload.get("concurrency_enabled", False)),
            stop_on_first_hard_failure=bool(payload.get("stop_on_first_hard_failure", True)),
            stage_concurrency=stage_concurrency,
            artifact_cache_mode=cache_mode,
            artifact_cache_stages=as_string_tuple(cache_payload.get("stages", payload.get("artifact_cache_stages"))),
            pre_qa_guardrail_mode=pre_qa_mode,
            pre_qa_dense_paragraph_warning_chars=max(
                1,
                int(pre_qa_payload.get("dense_paragraph_warning_chars", payload.get("pre_qa_dense_paragraph_warning_chars", 900))),
            ),
            sentinel_mode=sentinel_mode,
            sentinel_fail_on=sentinel_fail_on,
        )

    def limit_for_stage(self, stage: str) -> int:
        if not self.concurrency_enabled:
            return 1
        return max(1, int(self.stage_concurrency.get(stage, 1)))

    def pre_qa_blocks_runtime(self) -> bool:
        return self.pre_qa_guardrail_mode == "blocking"

    def sentinel_blocks_runtime(self) -> bool:
        return self.sentinel_mode == "blocking"

    def cache_skips_runtime(self) -> bool:
        return self.artifact_cache_mode == "enabled"


@dataclass(slots=True)
class StyleProfile(JsonSerializable):
    key: str
    name: str
    description: str
    genre_label: str = ""
    tone: str = ""
    naming_notes: str = ""
    narration_density: str = ""
    glossary_categories: tuple[str, ...] = ()
    qa_criteria: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, key: str, data: Mapping[str, Any] | None) -> StyleProfile:
        payload = dict(data or {})
        return cls(
            key=key,
            name=str(payload.get("name", key)),
            description=str(payload.get("description", "")),
            genre_label=str(payload.get("genre_label", "")),
            tone=str(payload.get("tone", "")),
            naming_notes=str(payload.get("naming_notes", "")),
            narration_density=str(payload.get("narration_density", "")),
            glossary_categories=as_string_tuple(payload.get("glossary_categories")),
            qa_criteria=as_string_tuple(payload.get("qa_criteria")),
            metadata={
                str(k): v
                for k, v in payload.items()
                if k not in {"name", "description", "genre_label", "tone", "naming_notes", "narration_density", "glossary_categories", "qa_criteria"}
            },
        )

    def instruction_text(self) -> str:
        lines: list[str] = []
        genre_label = self.genre_label.strip()
        tone = self.tone.strip()
        naming_notes = self.naming_notes.strip()
        narration_density = self.narration_density.strip()
        has_structured_fields = bool(
            genre_label
            or tone
            or naming_notes
            or narration_density
            or self.glossary_categories
            or self.qa_criteria
        )
        if has_structured_fields:
            lines.append(f"Genre label: {genre_label or self.name}")
        if tone:
            lines.append(f"Tone: {tone}")
        if naming_notes:
            lines.append(f"Naming notes: {naming_notes}")
        if narration_density:
            lines.append(f"Narration density: {narration_density}")
        if self.glossary_categories:
            lines.append("Glossary categories: " + ", ".join(self.glossary_categories))
        if self.qa_criteria:
            lines.append("QA criteria: " + "; ".join(self.qa_criteria))
        if lines:
            return "\n".join(lines)
        if self.description.strip():
            return self.description.strip()
        return self.name


@dataclass(slots=True)
class StageRouting(JsonSerializable):
    stage: str
    provider: str
    model: str = ""
    fallback_provider: str = ""
    fallback_model: str = ""
    fallbacks: tuple[dict[str, str], ...] = ()
    timeout_seconds: float | None = None
    retry_max_attempts: int | None = None
    retry_initial_delay_seconds: float | None = None
    retry_backoff_multiplier: float | None = None
    retry_failure_kinds: tuple[str, ...] | None = None
    max_calls_per_scan: int | None = None
    max_failures_per_scan: int | None = None

    @classmethod
    def from_mapping(cls, stage: str, value: Any) -> StageRouting:
        if isinstance(value, str):
            return cls(stage=stage, provider=value)
        if isinstance(value, Mapping):
            # Parse retry sub-mapping if present
            retry_section = value.get("retry")
            retry_max_attempts = None
            retry_initial_delay_seconds = None
            retry_backoff_multiplier = None
            retry_failure_kinds = None
            if isinstance(retry_section, Mapping):
                retry_max_attempts = retry_section.get("max_attempts")
                if retry_max_attempts is not None:
                    retry_max_attempts = int(retry_max_attempts)
                retry_initial_delay_seconds = retry_section.get("initial_delay_seconds")
                if retry_initial_delay_seconds is not None:
                    retry_initial_delay_seconds = float(retry_initial_delay_seconds)
                retry_backoff_multiplier = retry_section.get("backoff_multiplier")
                if retry_backoff_multiplier is not None:
                    retry_backoff_multiplier = float(retry_backoff_multiplier)
                failure_kinds_raw = retry_section.get("failure_kinds")
                if failure_kinds_raw is not None:
                    if isinstance(failure_kinds_raw, str):
                        failure_kinds_raw = (failure_kinds_raw,)
                    else:
                        failure_kinds_raw = tuple(str(kind).strip().lower() for kind in failure_kinds_raw)
                    retry_failure_kinds = failure_kinds_raw
            # Parse timeout_seconds
            timeout_seconds = value.get("timeout_seconds")
            if timeout_seconds is not None:
                timeout_seconds = float(timeout_seconds)
            # Parse ordered fallback chain. Legacy fallback_provider/fallback_model
            # remains supported, but fallbacks allows provider A -> B -> C.
            fallback_provider = as_string_or_empty(value.get("fallback_provider"))
            fallback_model = as_string_or_empty(value.get("fallback_model"))
            fallbacks: list[dict[str, str]] = []
            raw_fallbacks = value.get("fallbacks")
            if raw_fallbacks is not None:
                if isinstance(raw_fallbacks, (str, Mapping)):
                    raw_fallbacks = (raw_fallbacks,)
                for item in raw_fallbacks:
                    if isinstance(item, str):
                        provider_name = item
                        model_name = ""
                    elif isinstance(item, Mapping):
                        provider_name = as_string_or_empty(item.get("provider"))
                        model_name = as_string_or_empty(item.get("model"))
                    else:
                        raise TypeError(f"Unsupported fallback definition for stage '{stage}': {item!r}")
                    if provider_name:
                        fallbacks.append({"provider": provider_name, "model": model_name})
            elif fallback_provider:
                fallbacks.append({"provider": fallback_provider, "model": fallback_model})
            # Parse scan-level budget fields
            max_calls_per_scan = value.get("max_calls_per_scan")
            if max_calls_per_scan is not None:
                max_calls_per_scan = int(max_calls_per_scan)
            max_failures_per_scan = value.get("max_failures_per_scan")
            if max_failures_per_scan is not None:
                max_failures_per_scan = int(max_failures_per_scan)
            return cls(
                stage=stage,
                provider=as_string_or_empty(value.get("provider")),
                model=as_string_or_empty(value.get("model")),
                fallback_provider=fallback_provider,
                fallback_model=fallback_model,
                fallbacks=tuple(fallbacks),
                timeout_seconds=timeout_seconds,
                retry_max_attempts=retry_max_attempts,
                retry_initial_delay_seconds=retry_initial_delay_seconds,
                retry_backoff_multiplier=retry_backoff_multiplier,
                retry_failure_kinds=retry_failure_kinds,
                max_calls_per_scan=max_calls_per_scan,
                max_failures_per_scan=max_failures_per_scan,
            )
        raise TypeError(f"Unsupported routing definition for stage '{stage}': {value!r}")


@dataclass(slots=True)
class ProviderRequest(JsonSerializable):
    prompt: str
    provider: str = ""
    stage: str = ""
    model: str = ""
    cwd: Path | None = None
    timeout_seconds: float | None = None
    env: dict[str, str] = field(default_factory=dict)
    extra_args: tuple[str, ...] = ()


@dataclass(slots=True)
class ProviderResponse(JsonSerializable):
    provider: str
    command: tuple[str, ...]
    stdout: str
    stderr: str = ""
    returncode: int = 0
    started_at: str = ""
    finished_at: str = ""
    duration_seconds: float = 0.0
    model: str = ""
    stage: str = ""


@dataclass(slots=True)
class ProviderSpec(JsonSerializable):
    name: str
    executable: tuple[str, ...]
    prompt_flag: str | None = "-p"
    prompt_position: str = "flag"
    prompt_transport: str = "argv"
    model_flag: str | None = "--model"
    model_position: str = "after_prompt"
    default_model: str = ""
    extra_args: tuple[str, ...] = ()
    timeout_seconds: float = 120.0
    working_dir: Path | None = None
    env: dict[str, str] = field(default_factory=dict)
    retry_max_attempts: int = 1
    retry_initial_delay_seconds: float = 0.0
    retry_backoff_multiplier: float = 1.0
    retry_failure_kinds: tuple[str, ...] = ()
    max_command_chars: int = 24000

    @classmethod
    def from_mapping(
        cls,
        name: str,
        data: Mapping[str, Any] | None,
        *,
        base_dir: Path | None = None,
    ) -> ProviderSpec:
        payload = dict(data or {})
        executable = payload.get("executable", payload.get("command", (name,)))
        if isinstance(executable, str):
            executable = (executable,)
        else:
            executable = tuple(str(item) for item in executable)
        extra_args = payload.get("extra_args", ())
        if isinstance(extra_args, str):
            extra_args = (extra_args,)
        else:
            extra_args = tuple(str(item) for item in extra_args)
        working_dir_value = payload.get("working_dir")
        working_dir = None
        if working_dir_value is not None:
            working_dir = Path(working_dir_value)
            if not working_dir.is_absolute() and base_dir is not None:
                working_dir = (base_dir / working_dir).resolve()
        env_payload = payload.get("env") or {}
        env = {str(key): str(value) for key, value in dict(env_payload).items()}
        # retry config
        retry_section = payload.get("retry")
        if isinstance(retry_section, Mapping):
            retry_max_attempts = int(retry_section.get("max_attempts", payload.get("retry_max_attempts", 1)))
            retry_initial_delay_seconds = float(retry_section.get("initial_delay_seconds", payload.get("retry_initial_delay_seconds", 0.0)))
            retry_backoff_multiplier = float(retry_section.get("backoff_multiplier", payload.get("retry_backoff_multiplier", 1.0)))
            failure_kinds_raw = retry_section.get("failure_kinds", payload.get("retry_failure_kinds", ()))
        else:
            retry_max_attempts = int(payload.get("retry_max_attempts", 1))
            retry_initial_delay_seconds = float(payload.get("retry_initial_delay_seconds", 0.0))
            retry_backoff_multiplier = float(payload.get("retry_backoff_multiplier", 1.0))
            failure_kinds_raw = payload.get("retry_failure_kinds", ())
        # normalize failure kinds
        if isinstance(failure_kinds_raw, str):
            failure_kinds_raw = (failure_kinds_raw,)
        retry_failure_kinds = tuple(str(kind).strip().lower() for kind in failure_kinds_raw)
        # validation
        if retry_max_attempts < 1:
            raise ValueError(f"retry_max_attempts must be at least 1, got {retry_max_attempts}")
        if retry_initial_delay_seconds < 0:
            raise ValueError(f"retry_initial_delay_seconds must be >= 0, got {retry_initial_delay_seconds}")
        if retry_backoff_multiplier < 1:
            raise ValueError(f"retry_backoff_multiplier must be >= 1, got {retry_backoff_multiplier}")
        max_command_chars = int(payload.get("max_command_chars", 24000))
        if max_command_chars < 1000:
            raise ValueError(f"max_command_chars must be >= 1000, got {max_command_chars}")
        prompt_position = str(
            payload.get(
                "prompt_position",
                "positional" if name == "codex" else "flag",
            )
        ).lower()
        return cls(
            name=name,
            executable=tuple(executable),
            prompt_flag=payload.get("prompt_flag", "-p"),
            prompt_position=prompt_position,
            prompt_transport=str(payload.get("prompt_transport", "argv")).lower(),
            model_flag=payload.get("model_flag", "--model"),
            model_position=str(payload.get("model_position", "after_prompt")).lower(),
            default_model=as_string_or_empty(payload.get("default_model")),
            extra_args=extra_args,
            timeout_seconds=float(payload.get("timeout_seconds", 120.0)),
            working_dir=working_dir,
            env=env,
            retry_max_attempts=retry_max_attempts,
            retry_initial_delay_seconds=retry_initial_delay_seconds,
            retry_backoff_multiplier=retry_backoff_multiplier,
            retry_failure_kinds=retry_failure_kinds,
            max_command_chars=max_command_chars,
        )

    def build_command(self, request: ProviderRequest) -> list[str]:
        command = [*self.executable, *self.extra_args, *request.extra_args]
        prompt = request.prompt
        if not prompt:
            raise ValueError("ProviderRequest.prompt cannot be empty.")

        model = request.model or self.default_model
        if model and self.model_position == "before_prompt":
            if not self.model_flag:
                raise ValueError(f"Provider '{self.name}' does not define a model_flag.")
            command.extend([self.model_flag, model])

        if self.prompt_transport == "stdin":
            if self.prompt_position == "flag":
                if not self.prompt_flag:
                    raise ValueError(f"Provider '{self.name}' requires a prompt_flag.")
                command.extend([self.prompt_flag])
                # prompt will be passed via stdin, not argv
            elif self.prompt_position == "positional":
                # Positional stdin providers such as Codex use "-" as a stdin marker.
                # Qwen uses stdin without a marker, so prompt_flag remains empty there.
                if self.prompt_flag:
                    command.append(self.prompt_flag)
            else:
                raise ValueError(f"Unsupported prompt_position '{self.prompt_position}' for provider '{self.name}'.")
        else:
            if self.prompt_position == "flag":
                if not self.prompt_flag:
                    raise ValueError(f"Provider '{self.name}' requires a prompt_flag.")
                command.extend([self.prompt_flag, prompt])
            elif self.prompt_position == "positional":
                command.append(prompt)
            else:
                raise ValueError(f"Unsupported prompt_position '{self.prompt_position}' for provider '{self.name}'.")

        if model and self.model_position != "before_prompt":
            if not self.model_flag:
                raise ValueError(f"Provider '{self.name}' does not define a model_flag.")
            command.extend([self.model_flag, model])

        return command


@dataclass(slots=True)
class GlossaryEntry(JsonSerializable):
    original_term: str
    thai_term: str
    category: str
    file_name: str = ""
    status: str = "proposed"
    aliases: tuple[str, ...] = ()
    description: str = ""
    related: tuple[str, ...] = ()
    source_language: str = ""
    novel: str = ""
    notes: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def all_keys(self) -> tuple[str, ...]:
        keys = {self.original_term, self.thai_term, self.file_name}
        keys.update(self.aliases)
        keys.update(self.related)
        return tuple(sorted(key for key in keys if key))


@dataclass(slots=True)
class TermSuggestion(JsonSerializable):
    original_term: str
    category: str
    context: tuple[str, ...] = ()
    options: tuple[str, ...] = ()
    rationales: tuple[str, ...] = ()
    rationale: str = ""
    provider: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ChapterSource(JsonSerializable):
    novel_id: str
    chapter_id: str
    title: str = ""
    source_language: str = ""
    source_path: Path | None = None
    source_url: str = ""
    raw_text: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ChapterMeta(JsonSerializable):
    """Metadata for one chapter from a table-of-contents page."""
    index: int                          # 1-based ordinal position in TOC
    chapter_id: str                     # pipeline chapter ID, e.g. "ch001"
    title: str = ""                     # chapter title from TOC link text
    url: str = ""                       # full URL to chapter page
    source_id: str = ""                 # site-specific ID (e.g. "10186846")
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class SourceConfig(JsonSerializable):
    """Configuration for a website fetch adapter."""
    adapter: str = ""                   # adapter name, e.g. "piaotia"
    toc_url: str = ""                   # URL of table-of-contents page
    base_url: str = ""                  # base URL for relative chapter links
    delay_seconds: float = 1.0          # politeness delay between requests
    encoding: str = ""                  # override encoding (empty = auto-detect)
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ResearchProfile(JsonSerializable):
    title: str
    source_url: str
    aliases: tuple[str, ...] = ()
    synopsis: str = ""
    tags: tuple[str, ...] = ()
    style_notes: str = ""
    reader_expectations: str = ""
    review_summary: str = ""
    last_reviewed_at: str = ""
    reviewed_by: str = ""
    terminology: tuple[str, ...] = ()
    reference_links: tuple[str, ...] = ()
    notes: str = ""
    status: str = "pending"
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any] | None) -> ResearchProfile:
        payload = dict(data or {})
        source_payload = payload.get("source")
        if isinstance(source_payload, Mapping):
            payload.setdefault("title", source_payload.get("title", ""))
            payload.setdefault("source_url", source_payload.get("url", source_payload.get("source_url", "")))
        if "synopsis" not in payload and payload.get("summary"):
            payload["synopsis"] = payload.get("summary")
        status = str(payload.get("status", "pending")).strip().lower() or "pending"
        if status not in {"pending", "drafted", "active"}:
            raise ValueError(
                "Research profile status must be one of pending, drafted, or active."
            )
        reviewed_at = payload.get("last_reviewed_at", "")
        if isinstance(reviewed_at, datetime):
            reviewed_at = reviewed_at.isoformat()
        return cls(
            title=str(payload.get("title", "")).strip(),
            aliases=as_string_tuple(payload.get("aliases")),
            source_url=str(payload.get("source_url", "")).strip(),
            synopsis=str(payload.get("synopsis", "")).strip(),
            tags=as_string_tuple(payload.get("tags")),
            style_notes=str(payload.get("style_notes", "")).strip(),
            reader_expectations=str(payload.get("reader_expectations", "")).strip(),
            review_summary=str(payload.get("review_summary", "")).strip(),
            last_reviewed_at=str(reviewed_at).strip(),
            reviewed_by=str(payload.get("reviewed_by", "")).strip(),
            terminology=as_string_tuple(payload.get("terminology")),
            reference_links=as_string_tuple(payload.get("reference_links")),
            notes=str(payload.get("notes", "")).strip(),
            status=status,
            metadata={
                str(k): v
                for k, v in payload.items()
                if k not in {
                    "title",
                    "aliases",
                    "source_url",
                    "source",
                    "summary",
                    "synopsis",
                    "tags",
                    "style_notes",
                    "reader_expectations",
                    "review_summary",
                    "last_reviewed_at",
                    "reviewed_by",
                    "terminology",
                    "reference_links",
                    "notes",
                    "status",
                }
            },
        )

    def normalized_status(self) -> str:
        status = self.status.strip().lower() or "pending"
        if status not in {"pending", "drafted", "active"}:
            raise ValueError(
                "Research profile status must be one of pending, drafted, or active."
            )
        return status

    def required_fields(self) -> tuple[str, ...]:
        status = self.normalized_status()
        required = ["title", "source_url"]
        if status in {"drafted", "active"}:
            required.extend(["synopsis", "tags", "style_notes"])
        if status == "active":
            required.extend(["last_reviewed_at", "reviewed_by"])
        return tuple(required)

    def missing_fields(self) -> tuple[str, ...]:
        missing: list[str] = []
        for field_name in self.required_fields():
            value = getattr(self, field_name, "")
            if isinstance(value, str):
                if not value.strip():
                    missing.append(field_name)
            elif not value:
                missing.append(field_name)
        return tuple(missing)

    def readiness_summary(self) -> dict[str, Any]:
        status = self.normalized_status()
        missing_fields = list(self.missing_fields())
        required_fields = list(self.required_fields())
        review = {
            "last_reviewed_at": self.last_reviewed_at.strip(),
            "reviewed_by": self.reviewed_by.strip(),
        }
        missing_required_fields = bool(missing_fields)
        translation_ready = status == "active" and not missing_required_fields
        bounded_translation_ready = status in {"drafted", "active"} and not missing_required_fields
        if translation_ready:
            readiness = "ready"
        elif bounded_translation_ready:
            readiness = "degraded"
        else:
            readiness = "blocked"
        warnings: list[str] = []
        blocking_reasons: list[str] = []
        next_safe_action = ""
        if status == "pending":
            warnings.append("Research profile status is pending.")
            next_safe_action = "Fill synopsis, tags, and style_notes, then move status to drafted."
        elif status == "drafted" and bounded_translation_ready:
            warnings.append("Research profile is drafted; bounded translation is allowed with a degraded readiness state.")
            if not review["last_reviewed_at"]:
                warnings.append("last_reviewed_at is blank.")
            if not review["reviewed_by"]:
                warnings.append("reviewed_by is blank.")
            next_safe_action = "Use bounded translation only, then review the profile and promote it to active before wider production."
        elif status == "drafted":
            blocking_reasons.append("Research profile is drafted but incomplete.")
            next_safe_action = "Fill the missing required fields before bounded translation."
        if missing_fields:
            blocking_reasons.append("Missing required fields: " + ", ".join(missing_fields))
        if status == "active" and missing_fields:
            blocking_reasons.append("Research profile is active but incomplete.")
        if status == "active" and not missing_fields:
            next_safe_action = "Research profile is ready for normal production."
        return {
            "status": status,
            "readiness": readiness,
            "translation_ready": translation_ready,
            "bounded_translation_ready": bounded_translation_ready,
            "fetch_ready": True,
            "glossary_scan_ready": True,
            "required_fields": required_fields,
            "missing_fields": missing_fields,
            "warnings": warnings,
            "blocking_reasons": blocking_reasons,
            "review": review,
            "next_safe_action": next_safe_action,
        }

    def context_text(self) -> str:
        lines: list[str] = []
        title = self.title.strip()
        source_url = self.source_url.strip()
        synopsis = self.synopsis.strip()
        style_notes = self.style_notes.strip()
        reader_expectations = self.reader_expectations.strip()
        review_summary = self.review_summary.strip()
        notes = self.notes.strip()
        if title:
            lines.append(f"Title: {title}")
        if self.aliases:
            lines.append("Aliases: " + ", ".join(self.aliases))
        if source_url:
            lines.append(f"Source URL: {source_url}")
        if synopsis:
            lines.append(f"Synopsis: {synopsis}")
        if self.tags:
            lines.append("Tags: " + ", ".join(self.tags))
        if style_notes:
            lines.append(f"Style notes: {style_notes}")
        if reader_expectations:
            lines.append(f"Reader expectations: {reader_expectations}")
        if review_summary:
            lines.append(f"Review summary: {review_summary}")
        if self.terminology:
            lines.append("Terminology: " + ", ".join(self.terminology))
        if notes:
            lines.append(f"Notes: {notes}")
        if lines:
            return "\n".join(lines)
        return "none"


@dataclass(slots=True)
class NovelProfile(JsonSerializable):
    novel_id: str
    title: str
    aliases: tuple[str, ...] = ()
    source_language: str = ""
    target_language: str = ""
    genre: str = ""
    style_profile: str = ""
    source_adapter: str = ""
    source_toc_url: str = ""
    notes: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class TextBlock(JsonSerializable):
    block_id: str
    chapter_id: str
    block_index: int = 0
    source_text: str = ""
    source_language: str = ""
    start_offset: int = 0
    end_offset: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)
    order: int = 0
    text: str = ""
    context_before: str = ""
    context_after: str = ""
    character_count: int = 0
    word_count: int = 0

    def __post_init__(self) -> None:
        if not self.source_text and self.text:
            self.source_text = self.text
        if not self.text and self.source_text:
            self.text = self.source_text
        if not self.block_index and self.order:
            self.block_index = self.order
        if not self.order and self.block_index:
            self.order = self.block_index
        if not self.character_count:
            self.character_count = len(self.text or self.source_text)
        if not self.word_count:
            source = self.text or self.source_text
            self.word_count = len([token for token in source.split() if token])


@dataclass(slots=True)
class LiteralSentencePair(JsonSerializable):
    source_sentence: str
    literal_sentence: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class LiteralDraft(JsonSerializable):
    block_id: str
    chapter_id: str
    sentence_pairs: tuple[LiteralSentencePair, ...] = ()
    source_text: str = ""
    provider: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RefinedDraft(JsonSerializable):
    block_id: str
    chapter_id: str
    refined_text: str
    provider: str = ""
    style_profile: str = ""
    source_text: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class QAFinding(JsonSerializable):
    severity: str
    code: str
    message: str
    details: str = ""
    source_span: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class QAReport(JsonSerializable):
    block_id: str
    chapter_id: str
    passed: bool
    findings: tuple[QAFinding, ...] = ()
    feedback: str = ""
    retry_count: int = 0
    judge_provider: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RunRecord(JsonSerializable):
    run_id: str
    block_id: str
    stage: str
    status: str
    created_at: str = ""
    provider: str = ""
    input_hash: str = ""
    output_hash: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def new(
        cls,
        *,
        run_id: str,
        block_id: str,
        stage: str,
        status: str,
        provider: str = "",
        input_hash: str = "",
        output_hash: str = "",
        metadata: Mapping[str, Any] | None = None,
        created_at: str | None = None,
    ) -> RunRecord:
        return cls(
            run_id=run_id,
            block_id=block_id,
            stage=stage,
            status=status,
            created_at=created_at or utc_now_iso(),
            provider=provider,
            input_hash=input_hash,
            output_hash=output_hash,
            metadata={str(key): value for key, value in dict(metadata or {}).items()},
        )


@dataclass(slots=True)
class AppConfig(JsonSerializable):
    config_path: Path
    workspace: WorkspacePaths
    novel_id: str
    vault_root: Path
    source_language: str
    default_style_profile: str
    batch: BatchDefaults
    chunking: ChunkingPolicy
    execution: ExecutionPolicy = field(default_factory=ExecutionPolicy)
    research_profile: ResearchProfile | None = None
    source: SourceConfig = field(default_factory=SourceConfig)
    providers: dict[str, ProviderSpec] = field(default_factory=dict)
    stage_routing: dict[str, StageRouting] = field(default_factory=dict)
    style_profiles: dict[str, StyleProfile] = field(default_factory=dict)
    raw_config: dict[str, Any] = field(default_factory=dict)

    @property
    def workspace_root(self) -> Path:
        return self.workspace.root

    @property
    def ledger_path(self) -> Path:
        return self.workspace.logs / "run_ledger.jsonl"

    def stage_provider_name(self, stage: str) -> str:
        routing = self.stage_routing.get(stage)
        if routing is None or not routing.provider:
            raise KeyError(f"No provider routing configured for stage '{stage}'.")
        return routing.provider

    def stage_routing_for(self, stage: str) -> StageRouting:
        try:
            return self.stage_routing[stage]
        except KeyError as exc:
            raise KeyError(f"No stage routing configured for '{stage}'.") from exc

    def stage_model_for(self, stage: str) -> str:
        return self.stage_routing_for(stage).model

    def fallback_provider_name_for(self, stage: str) -> str:
        routing = self.stage_routing_for(stage)
        if routing.fallbacks:
            return routing.fallbacks[0].get("provider", "")
        return routing.fallback_provider

    def fallback_model_for(self, stage: str) -> str:
        routing = self.stage_routing_for(stage)
        if routing.fallbacks:
            return routing.fallbacks[0].get("model", "")
        return routing.fallback_model

    def fallback_provider_for_stage(self, stage: str) -> ProviderSpec | None:
        provider_name = self.fallback_provider_name_for(stage)
        if not provider_name:
            return None
        try:
            return self.providers[provider_name]
        except KeyError as exc:
            raise KeyError(f"Fallback provider '{provider_name}' is not configured for stage '{stage}'.") from exc

    def fallback_routes_for_stage(self, stage: str) -> tuple[tuple[ProviderSpec, str], ...]:
        routing = self.stage_routing_for(stage)
        raw_routes = routing.fallbacks
        if not raw_routes and routing.fallback_provider:
            raw_routes = ({"provider": routing.fallback_provider, "model": routing.fallback_model},)
        routes: list[tuple[ProviderSpec, str]] = []
        for route in raw_routes:
            provider_name = route.get("provider", "")
            if not provider_name:
                continue
            try:
                provider_spec = self.providers[provider_name]
            except KeyError as exc:
                raise KeyError(f"Fallback provider '{provider_name}' is not configured for stage '{stage}'.") from exc
            routes.append((provider_spec, route.get("model", "")))
        return tuple(routes)

    def provider_for_stage(self, stage: str) -> ProviderSpec:
        provider_name = self.stage_provider_name(stage)
        try:
            return self.providers[provider_name]
        except KeyError as exc:
            raise KeyError(f"Provider '{provider_name}' is not configured.") from exc

    def style_profile_for_name(self, name: str | None = None) -> StyleProfile:
        profile_name = name or self.default_style_profile
        try:
            return self.style_profiles[profile_name]
        except KeyError as exc:
            raise KeyError(f"Style profile '{profile_name}' is not configured.") from exc

    def research_context_text(self) -> str:
        if self.research_profile is None:
            return "none"
        return self.research_profile.context_text()

    def research_readiness_summary(self) -> dict[str, Any]:
        profile_path = self.workspace.root / "RESEARCH_PROFILE.yaml"
        if self.research_profile is None:
            return {
                "path": str(profile_path),
                "present": False,
                "status": "missing",
                "readiness": "blocked",
                "translation_ready": False,
                "bounded_translation_ready": False,
                "fetch_ready": True,
                "glossary_scan_ready": True,
                "required_fields": [],
                "missing_fields": [],
                "warnings": ["RESEARCH_PROFILE.yaml is missing."],
                "blocking_reasons": ["RESEARCH_PROFILE.yaml is missing."],
                "review": {
                    "last_reviewed_at": "",
                    "reviewed_by": "",
                },
                "next_safe_action": "Create RESEARCH_PROFILE.yaml and fill the required fields before translation.",
            }
        summary = self.research_profile.readiness_summary()
        expected_source_url = self.source.toc_url.strip()
        profile_source_url = self.research_profile.source_url.strip()
        if expected_source_url and profile_source_url and profile_source_url != expected_source_url:
            message = "Research profile source_url does not match config source.toc_url."
            if summary["status"] == "pending":
                summary["warnings"] = [*summary["warnings"], message]
            else:
                summary["blocking_reasons"] = [*summary["blocking_reasons"], message]
                summary["bounded_translation_ready"] = False
                summary["translation_ready"] = False
                summary["readiness"] = "blocked"
        summary["path"] = str(profile_path)
        summary["present"] = True
        return summary

    def ensure_translation_ready(self, *, bounded: bool) -> dict[str, Any]:
        summary = self.research_readiness_summary()
        is_ready = summary["bounded_translation_ready"] if bounded else summary["translation_ready"]
        if not is_ready:
            mode = "bounded translation" if bounded else "normal production"
            raise ValueError(
                f"Research profile is not ready for {mode}. "
                f"status={summary['status']}; "
                f"missing={', '.join(summary['missing_fields']) or 'none'}; "
                f"blocking={'; '.join(summary['blocking_reasons']) or 'none'}"
            )
        return summary


AppPaths = WorkspacePaths


__all__ = [
    "AppConfig",
    "BatchDefaults",
    "ChapterMeta",
    "ChapterSource",
    "ChunkingPolicy",
    "GlossaryEntry",
    "JsonSerializable",
    "LiteralDraft",
    "LiteralSentencePair",
    "NovelProfile",
    "ProviderRequest",
    "ProviderResponse",
    "ProviderSpec",
    "QAReport",
    "QAFinding",
    "RefinedDraft",
    "RunRecord",
    "ResearchProfile",
    "SourceConfig",
    "StageRouting",
    "StyleProfile",
    "TermSuggestion",
    "TextBlock",
    "AppPaths",
    "WorkspacePaths",
    "as_string_tuple",
    "as_string_or_empty",
    "json_safe",
    "utc_now_iso",
]
