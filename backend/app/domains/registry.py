from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml
from pydantic import ValidationError

from app.config import get_settings
from app.domains.models import DomainConfig

DomainConfig.model_rebuild()


class DomainRegistry:
    def __init__(self, domains_dir: Path):
        self._domains: dict[str, DomainConfig] = {}
        self._load(domains_dir)

    def _load(self, domains_dir: Path) -> None:
        if not domains_dir.exists():
            raise FileNotFoundError(f"Domain config directory missing: {domains_dir}")
        for path in sorted(domains_dir.glob("*.yaml")):
            raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            try:
                cfg = DomainConfig.model_validate(raw)
            except ValidationError as exc:
                raise ValueError(f"Invalid domain config {path}: {exc}") from exc
            if cfg.id in self._domains:
                raise ValueError(f"Duplicate domain id {cfg.id}")
            self._domains[cfg.id] = cfg
        if not self._domains:
            raise ValueError("No domain configurations loaded")

    def get(self, domain_id: str) -> DomainConfig:
        if domain_id not in self._domains:
            raise KeyError(domain_id)
        return self._domains[domain_id]

    def all(self) -> list[DomainConfig]:
        return list(self._domains.values())

    def ids(self) -> set[str]:
        return set(self._domains)

    def is_registered(self, domain_id: str) -> bool:
        return domain_id in self._domains

    def apply_overrides(self, domain: DomainConfig, overrides: dict | None) -> DomainConfig:
        if not overrides:
            return domain
        data = domain.model_dump()
        data.update({k: v for k, v in overrides.items() if k in data})
        return DomainConfig.model_validate(data)


@lru_cache
def get_registry() -> DomainRegistry:
    return DomainRegistry(get_settings().domains_dir)
