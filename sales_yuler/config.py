import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class Settings:
    google_service_account_json: str | None
    google_service_account_file: Path | None
    target_spreadsheet_id: str
    target_worksheet_name: str
    sources_config: Path


@dataclass(frozen=True)
class SourceConfig:
    name: str
    url: str
    year: int
    month: int
    enabled: bool = True


def load_settings() -> Settings:
    service_account_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    service_account_file = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
    if not service_account_json and not service_account_file:
        raise RuntimeError(
            "Falta configurar GOOGLE_SERVICE_ACCOUNT_JSON o GOOGLE_SERVICE_ACCOUNT_FILE"
        )

    target_spreadsheet_id = _required_env("TARGET_SPREADSHEET_ID")
    target_worksheet_name = os.getenv("TARGET_WORKSHEET_NAME", "ventas_consolidado")
    sources_config = Path(os.getenv("SOURCES_CONFIG", "config/sources.yml"))

    return Settings(
        google_service_account_json=service_account_json,
        google_service_account_file=Path(service_account_file) if service_account_file else None,
        target_spreadsheet_id=target_spreadsheet_id,
        target_worksheet_name=target_worksheet_name,
        sources_config=sources_config,
    )


def load_sources(path: Path) -> list[SourceConfig]:
    if not path.exists():
        raise FileNotFoundError(f"No existe el archivo de fuentes: {path}")

    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    raw_sources: list[dict[str, Any]] = data.get("sources", [])

    sources = [
        SourceConfig(
            name=str(item["name"]),
            url=str(item["url"]),
            year=int(item["year"]),
            month=int(item["month"]),
            enabled=bool(item.get("enabled", True)),
        )
        for item in raw_sources
    ]

    return [source for source in sources if source.enabled]


def _required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Falta configurar la variable de entorno {name}")
    return value
