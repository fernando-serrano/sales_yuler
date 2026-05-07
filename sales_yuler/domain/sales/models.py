from dataclasses import dataclass

from sales_yuler.infrastructure.settings import SourceConfig


@dataclass(frozen=True)
class SalesBatch:
    source: SourceConfig
    document_title: str
    worksheet_title: str
    rows: list[dict[str, str]]
