from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

from novel_pipeline.files import read_text_if_exists

_PLACEHOLDER_PATTERN = re.compile(r"\{\{(?P<name>[a-zA-Z_][a-zA-Z0-9_]*)\}\}")


def normalize_prompt_name(name: str) -> str:
    candidate = Path(str(name)).stem if Path(str(name)).suffix else str(name)
    candidate = candidate.strip().lower().replace(" ", "_").replace("-", "_")
    candidate = re.sub(r"[^a-z0-9_]+", "_", candidate)
    return re.sub(r"_+", "_", candidate).strip("_")


@dataclass(slots=True)
class PromptTemplate:
    name: str
    path: Path
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def render(self, context: Mapping[str, Any] | None = None, **kwargs: Any) -> str:
        values: dict[str, Any] = dict(context or {})
        values.update(kwargs)
        missing: set[str] = set()

        def replace(match: re.Match[str]) -> str:
            key = match.group("name")
            if key in values:
                return str(values[key])
            missing.add(key)
            return match.group(0)

        rendered = _PLACEHOLDER_PATTERN.sub(replace, self.content)
        if missing:
            missing_keys = ", ".join(sorted(missing))
            raise KeyError(f"Missing prompt variables for '{self.name}': {missing_keys}")
        return rendered


@dataclass(slots=True)
class PromptStore:
    root: Path
    _cache: dict[str, PromptTemplate] = field(default_factory=dict, init=False, repr=False)

    def available(self) -> tuple[str, ...]:
        if not self.root.exists():
            return ()
        names = set()
        for path in self.root.iterdir():
            if path.is_file() and path.suffix.lower() in {".md", ".txt", ".prompt"}:
                names.add(normalize_prompt_name(path.stem))
        return tuple(sorted(names))

    def resolve(self, name: str) -> Path:
        direct_path = Path(name)
        if direct_path.exists():
            return direct_path.resolve()
        normalized = normalize_prompt_name(name)
        direct_candidate = self.root / f"{normalized}.md"
        if direct_candidate.exists():
            return direct_candidate
        for suffix in (".txt", ".prompt"):
            candidate = self.root / f"{normalized}{suffix}"
            if candidate.exists():
                return candidate
        if direct_path.suffix:
            candidate = self.root / name
            if candidate.exists():
                return candidate
        raise FileNotFoundError(
            f"Prompt template '{name}' not found under {self.root}. "
            f"Available templates: {', '.join(self.available()) or 'none'}."
        )

    def load(self, name: str) -> PromptTemplate:
        normalized = normalize_prompt_name(name)
        cached = self._cache.get(normalized)
        if cached is not None:
            return cached
        path = self.resolve(name)
        content = read_text_if_exists(path)
        if content is None:
            raise FileNotFoundError(f"Prompt template '{path}' could not be read.")
        template = PromptTemplate(name=normalized, path=path.resolve(), content=content)
        self._cache[normalized] = template
        return template

    def render(self, name: str, context: Mapping[str, Any] | None = None, **kwargs: Any) -> str:
        return self.load(name).render(context, **kwargs)


__all__ = ["PromptStore", "PromptTemplate", "normalize_prompt_name"]
