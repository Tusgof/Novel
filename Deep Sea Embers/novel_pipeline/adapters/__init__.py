"""Fetch adapter registry."""
from __future__ import annotations

from novel_pipeline.adapters.base import FetchAdapter
from novel_pipeline.types import SourceConfig


_ADAPTER_REGISTRY: dict[str, type[FetchAdapter]] = {}


def register_adapter(name: str, cls: type[FetchAdapter]) -> None:
    _ADAPTER_REGISTRY[name] = cls


def get_adapter(source_config: SourceConfig) -> FetchAdapter:
    """Look up and instantiate the adapter for the given source config."""
    name = source_config.adapter
    if name not in _ADAPTER_REGISTRY:
        available = ", ".join(sorted(_ADAPTER_REGISTRY)) or "(none)"
        raise ValueError(
            f"Unknown fetch adapter '{name}'. Available: {available}"
        )
    cls = _ADAPTER_REGISTRY[name]
    return cls(source_config)


# -- register built-in adapters on import --
from novel_pipeline.adapters.piaotia import PiaotiaAdapter  # noqa: E402
from novel_pipeline.adapters.local_raw import LocalRawAdapter  # noqa: E402
from novel_pipeline.adapters.roliascan import RoliascanAdapter  # noqa: E402
from novel_pipeline.adapters.wetriedtls import WetriedtlsAdapter  # noqa: E402

register_adapter("local_raw", LocalRawAdapter)
register_adapter("piaotia", PiaotiaAdapter)
register_adapter("roliascan", RoliascanAdapter)
register_adapter("wetriedtls", WetriedtlsAdapter)

__all__ = ["FetchAdapter", "get_adapter", "register_adapter"]
