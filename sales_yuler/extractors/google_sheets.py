import logging
from dataclasses import dataclass
from typing import Any

import gspread

from sales_yuler.config import SourceConfig


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class WorksheetRows:
    source: SourceConfig
    document_title: str
    worksheet_title: str
    rows: list[dict[str, str]]


class GoogleSheetsExtractor:
    def __init__(self, client: gspread.Client) -> None:
        self._client = client

    def extract_source(self, source: SourceConfig) -> list[WorksheetRows]:
        spreadsheet = self._client.open_by_url(source.url)
        batches: list[WorksheetRows] = []
        logger.info("Documento abierto: %s", spreadsheet.title)

        for worksheet in spreadsheet.worksheets():
            rows = _records_from_values(worksheet.get_all_values())
            logger.info("Hoja leida: %s filas=%s", worksheet.title, len(rows))
            if not rows:
                continue

            batches.append(
                WorksheetRows(
                    source=source,
                    document_title=spreadsheet.title,
                    worksheet_title=worksheet.title,
                    rows=rows,
                )
            )

        return batches


def _records_from_values(values: list[list[Any]]) -> list[dict[str, Any]]:
    if not values:
        return []

    headers = _unique_headers(values[0])
    records: list[dict[str, Any]] = []

    for values_row in values[1:]:
        if not any(str(value).strip() for value in values_row):
            continue

        row = [
            *values_row,
            *[""] * max(0, len(headers) - len(values_row)),
        ]
        records.append(dict(zip(headers, row[: len(headers)])))

    return records


def _unique_headers(headers: list[Any]) -> list[str]:
    seen: dict[str, int] = {}
    unique_headers: list[str] = []

    for index, header in enumerate(headers, start=1):
        name = str(header).strip() or f"columna {index}"
        seen[name] = seen.get(name, 0) + 1
        unique_headers.append(name if seen[name] == 1 else f"{name} {seen[name]}")

    return unique_headers
